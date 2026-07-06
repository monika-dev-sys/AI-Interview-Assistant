"""
services/scoring_service.py  — Ollama edition
Scores answers and full sessions using llama3.1:70b.
Includes extra JSON extraction robustness for local models.
"""
from __future__ import annotations
import json
import re
from models.interview import InterviewSession, Question, Answer
from models.score import InterviewScore, QuestionScore, DimensionScore
from services.llm_service import llm_service
from utils.logger import logger

SYSTEM = (
    "You are an expert technical interviewer and evaluator. "
    "Respond with ONLY valid JSON. No markdown, no preamble, no explanation."
)

ANSWER_SCORE_PROMPT = """Score this interview answer across three dimensions.

Question: {question}
Answer: {answer}
Role: {role}
Difficulty: {difficulty}

Return ONLY this JSON:
{{
  "overall_score": 7.5,
  "dimensions": [
    {{
      "dimension": "Technical Accuracy",
      "score": 8.0,
      "rationale": "Explanation of score",
      "improvement_tips": ["Tip 1", "Tip 2"]
    }},
    {{
      "dimension": "Clarity & Communication",
      "score": 7.0,
      "rationale": "Explanation",
      "improvement_tips": ["Tip"]
    }},
    {{
      "dimension": "Depth & Examples",
      "score": 7.5,
      "rationale": "Explanation",
      "improvement_tips": ["Tip"]
    }}
  ],
  "highlights": ["What was done well"],
  "gaps": ["What was missing"]
}}

JSON response:"""

FINAL_SCORE_PROMPT = """Compute an overall interview assessment from these per-question scores.

Per-question data:
{question_scores_json}

Return ONLY this JSON:
{{
  "overall_score": 72.5,
  "technical_score": 75.0,
  "communication_score": 70.0,
  "problem_solving_score": 73.0,
  "confidence_score": 68.0,
  "hire_recommendation": "Hire"
}}

Valid values for hire_recommendation: "Strong Hire", "Hire", "No Hire", "Strong No Hire"

JSON response:"""


class ScoringService:

    def score_answer(self, question: Question, answer: Answer, role: str = "") -> QuestionScore:
        prompt = ANSWER_SCORE_PROMPT.format(
            question=question.text[:800],
            answer=answer.text[:1200],
            role=role or "Software Engineer",
            difficulty=question.difficulty.value,
        )
        raw = llm_service.complete(prompt, system=SYSTEM, max_tokens=1000)
        data = self._parse_json(raw)

        return QuestionScore(
            question_id=question.id,
            question_text=question.text,
            answer_text=answer.text,
            overall_score=float(data.get("overall_score", 0)),
            dimensions=[DimensionScore(**d) for d in data.get("dimensions", []) if isinstance(d, dict)],
            highlights=data.get("highlights", []),
            gaps=data.get("gaps", []),
        )

    def score_session(self, session: InterviewSession) -> InterviewScore:
        question_map = {q.id: q for q in session.questions}
        question_scores: list[QuestionScore] = []

        for answer in session.answers:
            question = question_map.get(answer.question_id)
            if not question:
                continue
            qs = self.score_answer(question, answer, role=session.target_role)
            question_scores.append(qs)

        # Summarise for final score (trim to avoid context overflow)
        summary_data = [
            {
                "question": qs.question_text[:100],
                "overall_score": qs.overall_score,
                "highlights": qs.highlights[:2],
                "gaps": qs.gaps[:2],
            }
            for qs in question_scores
        ]
        raw = llm_service.complete(
            FINAL_SCORE_PROMPT.format(question_scores_json=json.dumps(summary_data, indent=2)),
            system=SYSTEM,
            max_tokens=300,
        )
        agg = self._parse_json(raw)

        return InterviewScore(
            session_id=session.id,
            candidate_id=session.candidate_id,
            question_scores=question_scores,
            overall_score=float(agg.get("overall_score", 0)),
            technical_score=float(agg.get("technical_score", 0)),
            communication_score=float(agg.get("communication_score", 0)),
            problem_solving_score=float(agg.get("problem_solving_score", 0)),
            confidence_score=float(agg.get("confidence_score", 0)),
            hire_recommendation=agg.get("hire_recommendation", ""),
        )

    @staticmethod
    def _parse_json(text: str) -> dict:
        text = re.sub(r"```json|```", "", text).strip()
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            text = match.group(0)
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error in scoring: {e}\nRaw: {text[:300]}")
            return {}


scoring_service = ScoringService()
