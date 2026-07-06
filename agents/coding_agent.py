"""
agents/coding_agent.py  — Ollama edition
Coding problems, hints, code review, and simulated test runs.
"""
from __future__ import annotations
import json, re
from services.llm_service import llm_service
from utils.logger import logger

SYSTEM = (
    "You are a senior software engineer conducting a coding interview. "
    "Be precise and educational. When asked for JSON, return ONLY valid JSON."
)

REVIEW_PROMPT = """Review this code solution.

Problem: {problem}

Code ({language}):
{code}

Return ONLY this JSON:
{{
  "correctness": 8,
  "time_complexity": "O(n log n)",
  "space_complexity": "O(n)",
  "code_quality": 7,
  "issues": ["issue description"],
  "strengths": ["strength description"],
  "optimised_solution": "# optimised code",
  "overall_score": 7,
  "feedback": "2-3 sentence constructive summary"
}}

JSON response:"""

HINT_PROMPT = """The candidate needs hint #{hint_number} for this coding problem (1=gentle nudge, 3=near solution).
Do NOT give the full solution. Keep it to 2-3 sentences maximum.

Problem: {problem}
Current code: {current_code}

Hint:"""

RUN_PROMPT = """Simulate running this {language} code against the test cases.

Code:
{code}

Test cases: {test_cases}

Return ONLY this JSON:
{{
  "results": [
    {{"test_case": "input", "expected": "output", "actual": "output", "passed": true}}
  ],
  "all_passed": false,
  "runtime_notes": "observation about the solution"
}}

JSON response:"""


class CodingAgent:

    def review_code(self, problem: str, code: str, language: str = "Python") -> dict:
        prompt = REVIEW_PROMPT.format(problem=problem[:2000], code=code, language=language)
        raw = llm_service.complete(prompt, system=SYSTEM, max_tokens=1200)
        return self._parse(raw)

    def get_hint(self, problem: str, current_code: str, hint_number: int = 1) -> str:
        prompt = HINT_PROMPT.format(
            hint_number=hint_number,
            problem=problem[:1500],
            current_code=current_code or "# (no code written yet)",
        )
        return llm_service.complete(prompt, system=SYSTEM, max_tokens=200)

    def simulate_run(self, code: str, test_cases: list[dict], language: str = "Python") -> dict:
        prompt = RUN_PROMPT.format(
            code=code,
            test_cases=json.dumps(test_cases[:5]),
            language=language,
        )
        raw = llm_service.complete(prompt, system=SYSTEM, max_tokens=800)
        return self._parse(raw)

    @staticmethod
    def _parse(raw: str) -> dict:
        raw = re.sub(r"```json|```", "", raw).strip()
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            raw = match.group(0)
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            logger.error(f"CodingAgent JSON error: {e}\nRaw: {raw[:300]}")
            return {}


coding_agent = CodingAgent()
