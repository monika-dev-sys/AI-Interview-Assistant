"""
agents/behavioral_agent.py  — Ollama edition
STAR-method behavioural questions and evaluation.
"""
from __future__ import annotations
import json, re, uuid
from models.candidate import Candidate
from models.interview import Question, QuestionCategory, DifficultyLevel
from services.llm_service import llm_service
from utils.logger import logger

SYSTEM = (
    "You are a behavioural interview expert focused on STAR method. "
    "Respond with ONLY valid JSON. No markdown, no explanation."
)

BEHAVIORAL_PROMPT = """Generate {count} behavioural interview questions for a {role} position.

Difficulty: {difficulty}
Candidate: {background}

Cover competencies like: leadership, conflict, failure/learning, teamwork, prioritisation, communication.

Return ONLY a JSON array:
[
  {{
    "text": "Tell me about a time when...",
    "category": "behavioral",
    "difficulty": "{difficulty}",
    "follow_ups": ["What would you do differently?", "How did the team react?"],
    "expected_topics": ["Situation clarity", "Specific actions taken", "Measurable result"],
    "time_limit_seconds": 240,
    "competency": "leadership"
  }}
]

JSON array:"""

STAR_EVAL_PROMPT = """Evaluate if this answer follows the STAR method.

Question: {question}
Answer: {answer}

Return ONLY this JSON:
{{
  "situation_present": true,
  "task_present": true,
  "action_present": true,
  "result_present": false,
  "star_score": 7,
  "missing_elements": ["result was vague"],
  "suggestions": ["Quantify the outcome with metrics"]
}}

JSON response:"""


class BehavioralAgent:

    def generate_questions(
        self,
        candidate: Candidate,
        difficulty: DifficultyLevel,
        count: int = 5,
        role: str = "Software Engineer",
    ) -> list[Question]:
        background = (
            f"{candidate.years_of_experience} years experience; "
            f"skills: {', '.join(candidate.skills[:6])}"
        )
        prompt = BEHAVIORAL_PROMPT.format(
            count=count, role=role,
            difficulty=difficulty.value, background=background,
        )
        raw = llm_service.complete(prompt, system=SYSTEM, max_tokens=2000)
        raw = re.sub(r"```json|```", "", raw).strip()
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if match:
            raw = match.group(0)

        try:
            items = json.loads(raw)
        except json.JSONDecodeError as e:
            logger.error(f"BehavioralAgent JSON error: {e}")
            return []

        questions = []
        for item in items:
            try:
                questions.append(Question(
                    id=str(uuid.uuid4()),
                    text=item["text"],
                    category=QuestionCategory.BEHAVIORAL,
                    difficulty=difficulty,
                    follow_ups=item.get("follow_ups", []),
                    expected_topics=item.get("expected_topics", []),
                    time_limit_seconds=item.get("time_limit_seconds", 240),
                ))
            except Exception as exc:
                logger.warning(f"Skipping malformed behavioral question: {exc}")
        return questions

    def evaluate_star(self, question: str, answer: str) -> dict:
        prompt = STAR_EVAL_PROMPT.format(question=question, answer=answer)
        raw = llm_service.complete(prompt, system=SYSTEM, max_tokens=400)
        raw = re.sub(r"```json|```", "", raw).strip()
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            raw = match.group(0)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}


behavioral_agent = BehavioralAgent()
