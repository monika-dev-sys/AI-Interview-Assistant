"""
models/feedback.py

Feedback models.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from .score import InterviewScore


class FeedbackSection(BaseModel):
    title: str
    content: str
    action_items: list[str] = Field(default_factory=list)


class InterviewFeedback(BaseModel):
    session_id: str
    candidate_id: str

    candidate_name: str = ""
    target_role: str = ""

    executive_summary: str = ""

    strengths: list[str] = Field(default_factory=list)
    areas_for_improvement: list[str] = Field(default_factory=list)

    sections: list[FeedbackSection] = Field(default_factory=list)

    # Personalized study plan
    recommended_topics: list[str] = Field(default_factory=list)
    recommended_resources: list[dict] = Field(default_factory=list)

    score: Optional[InterviewScore] = None

    generated_at: str = ""

    class Config:
        arbitrary_types_allowed = True