"""
agents/evaluation_agent.py
Evaluates a complete interview session: scores every answer,
detects patterns, and returns an InterviewScore.
"""
from __future__ import annotations
from models.interview import InterviewSession
from models.score import InterviewScore
from services.scoring_service import scoring_service
from database.db import db
from utils.logger import logger


class EvaluationAgent:

    def evaluate(self, session: InterviewSession) -> InterviewScore:
        """Score a completed session and persist the result."""
        logger.info(f"Evaluating session {session.id} ({len(session.answers)} answers)")
        score = scoring_service.score_session(session)
        db.save_score(score)
        logger.info(
            f"Session {session.id} scored: overall={score.overall_score:.1f} | "
            f"recommendation={score.hire_recommendation}"
        )
        return score


evaluation_agent = EvaluationAgent()
