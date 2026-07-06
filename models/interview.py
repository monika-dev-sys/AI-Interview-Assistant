"""
models/interview.py
Pydantic models for interview sessions, questions, and answers.
"""
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class InterviewType(str, Enum):
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    CODING = "coding"
    MIXED = "mixed"


class DifficultyLevel(str, Enum):
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    STAFF = "staff"


class QuestionCategory(str, Enum):
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    CODING = "coding"
    SYSTEM_DESIGN = "system_design"
    CULTURE_FIT = "culture_fit"


class Question(BaseModel):
    id: str
    text: str
    category: QuestionCategory
    difficulty: DifficultyLevel
    follow_ups: list[str] = Field(default_factory=list)
    expected_topics: list[str] = Field(default_factory=list)
    time_limit_seconds: int = 180


class Answer(BaseModel):
    question_id: str
    text: str
    time_taken_seconds: Optional[int] = None
    submitted_at: datetime = Field(default_factory=datetime.utcnow)


class InterviewSession(BaseModel):
    id: Optional[str] = None
    candidate_id: str
    interview_type: InterviewType
    difficulty: DifficultyLevel
    target_role: str = ""
    questions: list[Question] = Field(default_factory=list)
    answers: list[Answer] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    is_complete: bool = False

    @property
    def duration_minutes(self) -> Optional[float]:
        if self.ended_at:
            delta = self.ended_at - self.started_at
            return round(delta.total_seconds() / 60, 1)
        return None
