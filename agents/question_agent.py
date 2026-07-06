"""
agents/question_agent.py  — Ollama edition
Generates tailored interview questions using llama3.1:70b.
"""
from __future__ import annotations
import json
import re
import uuid
from models.interview import Question, QuestionCategory, DifficultyLevel, InterviewType
from models.candidate import Candidate
from services.llm_service import llm_service
from utils.logger import logger

SYSTEM = (
    "You are an experienced technical interviewer. "
    "Respond with ONLY a valid JSON array. No markdown, no explanation."
)

QUESTION_PROMPT = """Generate {count} {interview_type} interview questions.

Role: {role}
Difficulty: {difficulty}
Candidate skills: {skills}
Years of experience: {years}

Return ONLY a JSON array:
[
  {{
    "text": "the question",
    "category": "{category}",
    "difficulty": "{difficulty}",
    "follow_ups": ["follow-up 1", "follow-up 2"],
    "expected_topics": ["topic 1", "topic 2"],
    "time_limit_seconds": 180
  }}
]

JSON array:"""

CODING_QUESTION_PROMPT = """Generate {count} coding problems for a {difficulty}-level {language} interview.

Role: {role}
Candidate skills: {skills}

Return ONLY a JSON array:
[
  {{
    "text": "full problem statement with input/output examples",
    "category": "coding",
    "difficulty": "{difficulty}",
    "follow_ups": ["optimize for space", "handle edge case X"],
    "expected_topics": ["algorithm or data structure"],
    "time_limit_seconds": 1200,
    "starter_code": "def solution():\\n    pass",
    "hints": ["hint 1", "hint 2"]
  }}
]

JSON array:"""


class QuestionAgent:

    def generate(
        self,
        candidate: Candidate,
        interview_type: InterviewType,
        difficulty: DifficultyLevel,
        count: int = 5,
        role: str = "Software Engineer",
        language: str = "Python",
    ) -> list[Question]:
        if interview_type == InterviewType.CODING:
            return self._generate_coding(candidate, difficulty, count, role, language)

        category_map = {
            InterviewType.TECHNICAL: ("technical", QuestionCategory.TECHNICAL),
            InterviewType.BEHAVIORAL: ("behavioral", QuestionCategory.BEHAVIORAL),
            InterviewType.MIXED: ("mixed technical and behavioral", QuestionCategory.TECHNICAL),
        }
        type_label, category = category_map.get(interview_type, ("technical", QuestionCategory.TECHNICAL))

        prompt = QUESTION_PROMPT.format(
            count=count,
            interview_type=type_label,
            role=role,
            difficulty=difficulty.value,
            skills=", ".join(candidate.skills[:10]),
            years=candidate.years_of_experience,
            category=category.value,
        )
        raw = llm_service.complete(prompt, system=SYSTEM, max_tokens=2500)
        return self._parse_questions(raw, category)

    def _generate_coding(
        self,
        candidate: Candidate,
        difficulty: DifficultyLevel,
        count: int,
        role: str,
        language: str,
    ) -> list[Question]:
        prompt = CODING_QUESTION_PROMPT.format(
            count=count,
            difficulty=difficulty.value,
            language=language,
            role=role,
            skills=", ".join(candidate.skills[:8]),
        )
        raw = llm_service.complete(prompt, system=SYSTEM, max_tokens=3000)
        return self._parse_questions(raw, QuestionCategory.CODING)

    def _parse_questions(self, raw: str, default_category: QuestionCategory) -> list[Question]:
        raw = re.sub(r"```json|```", "", raw).strip()
        # Extract JSON array
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if match:
            raw = match.group(0)
        try:
            items = json.loads(raw)
        except json.JSONDecodeError as e:
            logger.error(f"QuestionAgent JSON error: {e}\nRaw: {raw[:400]}")
            return []

        questions: list[Question] = []
        for item in items:
            try:
                cat_str = item.get("category", default_category.value)
                diff_str = item.get("difficulty", DifficultyLevel.MID.value)
                q = Question(
                    id=str(uuid.uuid4()),
                    text=item["text"],
                    category=QuestionCategory(cat_str) if cat_str in QuestionCategory._value2member_map_ else default_category,
                    difficulty=DifficultyLevel(diff_str) if diff_str in DifficultyLevel._value2member_map_ else DifficultyLevel.MID,
                    follow_ups=item.get("follow_ups", []),
                    expected_topics=item.get("expected_topics", []),
                    time_limit_seconds=item.get("time_limit_seconds", 180),
                )
                questions.append(q)
            except Exception as exc:
                logger.warning(f"Skipping malformed question: {exc}")

        logger.info(f"Generated {len(questions)} questions")
        return questions


question_agent = QuestionAgent()
