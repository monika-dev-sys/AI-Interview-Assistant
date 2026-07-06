"""
agents/resume_agent.py  — Ollama edition
Parses and analyses a candidate's resume using llama3.1:70b.
Uses stricter JSON prompting to handle local model quirks.
"""
from __future__ import annotations
import json
import re
import uuid
from models.candidate import Candidate, WorkExperience, Education
from services.llm_service import llm_service
from services.vector_db_service import vector_db_service
from utils.file_parser import parse_resume, chunk_text
from utils.logger import logger

SYSTEM = (
    "You are a senior technical recruiter. "
    "IMPORTANT: You must respond with ONLY a valid JSON object. "
    "No markdown, no code fences, no explanation — raw JSON only."
)

EXTRACT_PROMPT = """Extract structured information from this resume.

Return ONLY this JSON structure with no other text:
{{
  "name": "candidate full name",
  "email": "email or null",
  "phone": "phone or null",
  "summary": "2-3 sentence professional summary",
  "years_of_experience": 0.0,
  "skills": ["skill1", "skill2"],
  "experience": [
    {{
      "company": "company name",
      "title": "job title",
      "duration": "dates",
      "responsibilities": ["responsibility 1", "responsibility 2"]
    }}
  ],
  "education": [
    {{
      "institution": "university name",
      "degree": "degree type",
      "field": "field of study",
      "year": "graduation year"
    }}
  ]
}}

Resume:
{resume_text}

JSON response:"""

MATCH_PROMPT = """Rate how well this candidate matches the job description.

Return ONLY this JSON with no other text:
{{
  "match_score": 75,
  "strengths": ["strength 1", "strength 2", "strength 3"],
  "gaps": ["gap 1", "gap 2"],
  "summary": "2-sentence match summary"
}}

Candidate profile:
{candidate_summary}

Job Description:
{job_description}

JSON response:"""


class ResumeAgent:

    def analyse(self, file_path: str, candidate_id: str | None = None) -> Candidate:
        resume_text = parse_resume(file_path)
        # Truncate for context window
        resume_text_trunc = resume_text[:6000]
        logger.info(f"Parsed resume: {len(resume_text)} chars (truncated to {len(resume_text_trunc)})")

        raw = llm_service.complete(
            EXTRACT_PROMPT.format(resume_text=resume_text_trunc),
            system=SYSTEM,
            max_tokens=2000,
        )
        data = self._parse_json(raw)

        candidate = Candidate(
            id=candidate_id or str(uuid.uuid4()),
            name=data.get("name", ""),
            email=data.get("email"),
            phone=data.get("phone"),
            summary=data.get("summary", ""),
            years_of_experience=float(data.get("years_of_experience", 0)),
            skills=data.get("skills", []),
            experience=[WorkExperience(**e) for e in data.get("experience", []) if isinstance(e, dict)],
            education=[Education(**e) for e in data.get("education", []) if isinstance(e, dict)],
            resume_text=resume_text,
            resume_file_path=str(file_path),
        )

        chunks = chunk_text(resume_text)
        vector_db_service.upsert_resume_chunks(candidate.id, chunks)
        logger.info(f"Resume analysis complete for {candidate.name} ({candidate.id})")
        return candidate

    def match_job(self, candidate: Candidate, job_description: str) -> dict:
        summary = (
            f"Name: {candidate.name}\n"
            f"Skills: {', '.join(candidate.skills[:12])}\n"
            f"Experience: {candidate.years_of_experience} years\n"
            f"Summary: {candidate.summary}"
        )
        raw = llm_service.complete(
            MATCH_PROMPT.format(
                candidate_summary=summary,
                job_description=job_description[:3000],
            ),
            system=SYSTEM,
            max_tokens=600,
        )
        return self._parse_json(raw)

    @staticmethod
    def _parse_json(text: str) -> dict:
        # Strip common local-model artifacts
        text = re.sub(r"```json|```", "", text).strip()
        # Find first { ... } block
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            text = match.group(0)
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error in ResumeAgent: {e}\nRaw: {text[:400]}")
            return {}


resume_agent = ResumeAgent()
