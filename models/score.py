from __future__ import annotations
from pydantic import BaseModel, Field

class DimensionScore(BaseModel):
    dimension: str
    score: float
    max_score: float = 10.0
    rationale: str = ""
    improvement_tips: list[str] = Field(default_factory=list)


class QuestionScore(BaseModel):
    question_id: str
    question_text: str
    answer_text: str
    dimensions: list[DimensionScore] = Field(default_factory=list)
    overall_score: float = 0.0
    highlights: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)


class InterviewScore(BaseModel):
    session_id: str
    candidate_id: str
    question_scores: list[QuestionScore] = Field(default_factory=list)
    overall_score: float = 0.0
    technical_score: float = 0.0
    communication_score: float = 0.0
    problem_solving_score: float = 0.0
    confidence_score: float = 0.0
    hire_recommendation: str = ""