"""
services/interview_service.py
High-level service managing the lifecycle of an interview session:
create → add questions → record answers → close.
"""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional

from models.interview import InterviewSession, InterviewType, DifficultyLevel, Answer
from models.candidate import Candidate
from database.db import db
from utils.logger import logger


class InterviewService:

    def create_session(
        self,
        candidate: Candidate,
        interview_type: InterviewType,
        difficulty: DifficultyLevel,
        target_role: str = "",
    ) -> InterviewSession:
        session = InterviewSession(
            id=str(uuid.uuid4()),
            candidate_id=candidate.id or str(uuid.uuid4()),
            interview_type=interview_type,
            difficulty=difficulty,
            target_role=target_role or candidate.target_role or "",
        )
        db.save_session(session)
        logger.info(f"Created interview session {session.id} | type={interview_type} | difficulty={difficulty}")
        return session

    def record_answer(
        self,
        session: InterviewSession,
        question_id: str,
        answer_text: str,
        time_taken_seconds: Optional[int] = None,
    ) -> InterviewSession:
        answer = Answer(
            question_id=question_id,
            text=answer_text,
            time_taken_seconds=time_taken_seconds,
        )
        session.answers.append(answer)
        db.update_session(session)
        return session

    def close_session(self, session: InterviewSession) -> InterviewSession:
        session.ended_at = datetime.utcnow()
        session.is_complete = True
        db.update_session(session)
        logger.info(f"Closed session {session.id} | duration={session.duration_minutes}m")
        return session

    def get_session(self, session_id: str) -> Optional[InterviewSession]:
        return db.get_session(session_id)

    def list_sessions(self, candidate_id: str) -> list[InterviewSession]:
        return db.list_sessions(candidate_id)


interview_service = InterviewService()
