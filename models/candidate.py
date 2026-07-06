"""
models/candidate.py
Pydantic model representing a candidate and their resume data.
"""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class WorkExperience(BaseModel):
    company: str
    title: str
    duration: str
    responsibilities: list[str] = Field(default_factory=list)


class Education(BaseModel):
    institution: str
    degree: str
    field: str
    year: Optional[str] = None


class Candidate(BaseModel):
    id: Optional[str] = None
    name: str = ""
    email: Optional[str] = None
    phone: Optional[str] = None

    # Resume-derived fields
    skills: list[str] = Field(default_factory=list)
    experience: list[WorkExperience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    summary: str = ""
    years_of_experience: float = 0.0

    # Raw resume text for LLM context
    resume_text: str = ""
    resume_file_path: Optional[str] = None

    # Target role context
    target_role: Optional[str] = None
    target_company: Optional[str] = None
    job_description: Optional[str] = None

    class Config:
        extra = "allow"
