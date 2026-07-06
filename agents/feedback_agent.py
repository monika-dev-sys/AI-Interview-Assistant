"""
agents/feedback_agent.py  — Ollama edition
Generates personalised feedback reports using llama3.1:70b.
"""
from __future__ import annotations
import json, re
from datetime import datetime
from models.score import InterviewScore
from models.feedback import InterviewFeedback, FeedbackSection
from models.candidate import Candidate
from services.llm_service import llm_service
from database.db import db
from utils.logger import logger

SYSTEM = (
    "You are a supportive career coach and interview expert. "
    "Respond with ONLY valid JSON. No markdown, no explanation."
)

FEEDBACK_PROMPT = """Write a personalised interview feedback report.

Candidate: {name}
Role: {role}
Overall Score: {overall}/100
Technical: {technical}/100
Communication: {communication}/100
Problem Solving: {problem_solving}/100
Recommendation: {recommendation}

Key highlights from the interview:
{highlights_json}

Return ONLY this JSON:
{{
  "executive_summary": "3-4 sentence overview of performance",
  "strengths": ["Specific strength 1", "Specific strength 2", "Specific strength 3"],
  "areas_for_improvement": ["Specific area 1", "Specific area 2"],
  "sections": [
    {{
      "title": "Technical Performance",
      "content": "Detailed feedback paragraph",
      "action_items": ["Concrete action 1", "Concrete action 2"]
    }},
    {{
      "title": "Communication & Clarity",
      "content": "Detailed feedback paragraph",
      "action_items": ["Concrete action"]
    }},
    {{
      "title": "30-Day Study Plan",
      "content": "Week-by-week personalised plan",
      "action_items": ["Week 1: ...", "Week 2: ...", "Week 3: ...", "Week 4: ..."]
    }}
  ],
  "recommended_topics": ["Topic 1", "Topic 2", "Topic 3"],
  "recommended_resources": [
    {{"title": "Resource name", "url": "https://example.com", "type": "book"}}
  ]
}}

JSON response:"""


class FeedbackAgent:

    def generate(self, score: InterviewScore, candidate: Candidate) -> InterviewFeedback:
        highlights = [
            {
                "question": qs.question_text[:100],
                "score": qs.overall_score,
                "highlights": qs.highlights[:2],
                "gaps": qs.gaps[:2],
            }
            for qs in score.question_scores[:6]  # limit for context
        ]

        prompt = FEEDBACK_PROMPT.format(
            name=candidate.name,
            role=candidate.target_role or "Software Engineer",
            overall=round(score.overall_score),
            technical=round(score.technical_score),
            communication=round(score.communication_score),
            problem_solving=round(score.problem_solving_score),
            recommendation=score.hire_recommendation,
            highlights_json=json.dumps(highlights, indent=2),
        )

        raw = llm_service.complete(prompt, system=SYSTEM, max_tokens=2500)
        data = self._parse(raw)

        feedback = InterviewFeedback(
            session_id=score.session_id,
            candidate_id=score.candidate_id,
            candidate_name=candidate.name,
            target_role=candidate.target_role or "Software Engineer",
            executive_summary=data.get("executive_summary", ""),
            strengths=data.get("strengths", []),
            areas_for_improvement=data.get("areas_for_improvement", []),
            sections=[FeedbackSection(**s) for s in data.get("sections", []) if isinstance(s, dict)],
            recommended_topics=data.get("recommended_topics", []),
            recommended_resources=data.get("recommended_resources", []),
            score=score,
            generated_at=datetime.utcnow().isoformat(),
        )

        db.save_feedback(feedback)
        logger.info(f"Feedback generated for session {score.session_id}")
        return feedback

    @staticmethod
    def _parse(raw: str) -> dict:
        raw = re.sub(r"```json|```", "", raw).strip()
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            raw = match.group(0)
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            logger.error(f"FeedbackAgent JSON error: {e}\nRaw: {raw[:400]}")
            return {}


feedback_agent = FeedbackAgent()
