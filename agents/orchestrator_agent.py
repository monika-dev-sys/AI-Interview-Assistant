"""
agents/orchestrator_agent.py
Top-level agent that coordinates the full interview pipeline:
  Resume → Questions → Interview → Evaluation → Feedback
"""
from __future__ import annotations
from models.candidate import Candidate
from models.interview import InterviewSession, InterviewType, DifficultyLevel
from models.score import InterviewScore
from models.feedback import InterviewFeedback
from agents.resume_agent import resume_agent
from agents.question_agent import question_agent
from agents.behavioral_agent import behavioral_agent
from agents.evaluation_agent import evaluation_agent
from agents.feedback_agent import feedback_agent
from services.interview_service import interview_service
from database.db import db
from utils.logger import logger


class OrchestratorAgent:
    """
    Coordinates the full interview pipeline. Each method corresponds
    to one stage; the Streamlit pages call these in order.
    """

    # ── Stage 1: Resume Analysis ──────────────────────────────────────────────

    def analyse_resume(
        self,
        file_path: str,
        target_role: str = "",
        job_description: str = "",
    ) -> Candidate:
        candidate = resume_agent.analyse(file_path)
        candidate.target_role = target_role
        candidate.job_description = job_description
        db.save_candidate(candidate)
        logger.info(f"Orchestrator: resume analysed for {candidate.name}")
        return candidate

    def match_candidate_to_job(self, candidate: Candidate, job_description: str) -> dict:
        return resume_agent.match_job(candidate, job_description)

    # ── Stage 2: Question Generation ─────────────────────────────────────────

    def prepare_interview(
        self,
        candidate: Candidate,
        interview_type: InterviewType,
        difficulty: DifficultyLevel,
        question_count: int = 5,
        language: str = "Python",
    ) -> InterviewSession:
        session = interview_service.create_session(
            candidate=candidate,
            interview_type=interview_type,
            difficulty=difficulty,
            target_role=candidate.target_role or "Software Engineer",
        )

        if interview_type == InterviewType.BEHAVIORAL:
            questions = behavioral_agent.generate_questions(
                candidate, difficulty, question_count, candidate.target_role or "Software Engineer"
            )
        else:
            questions = question_agent.generate(
                candidate=candidate,
                interview_type=interview_type,
                difficulty=difficulty,
                count=question_count,
                role=candidate.target_role or "Software Engineer",
                language=language,
            )

        session.questions = questions
        interview_service.interview_service.update_session(session) if hasattr(interview_service, "interview_service") else db.save_session(session)
        logger.info(f"Orchestrator: {len(questions)} questions prepared for session {session.id}")
        return session

    # ── Stage 3: Record answers (called per-question by UI) ───────────────────

    def record_answer(
        self,
        session: InterviewSession,
        question_id: str,
        answer_text: str,
        time_taken_seconds: int | None = None,
    ) -> InterviewSession:
        return interview_service.record_answer(session, question_id, answer_text, time_taken_seconds)

    # ── Stage 4: Evaluation ───────────────────────────────────────────────────

    def evaluate_interview(self, session: InterviewSession) -> InterviewScore:
        session = interview_service.close_session(session)
        return evaluation_agent.evaluate(session)

    # ── Stage 5: Feedback ─────────────────────────────────────────────────────

    def generate_feedback(
        self,
        score: InterviewScore,
        candidate: Candidate,
    ) -> InterviewFeedback:
        return feedback_agent.generate(score, candidate)

    # ── Full pipeline (batch / testing use) ───────────────────────────────────

    def run_full_pipeline(
        self,
        resume_path: str,
        target_role: str,
        interview_type: InterviewType,
        difficulty: DifficultyLevel,
        answers: dict[int, str],   # {question_index: answer_text}
        question_count: int = 5,
    ) -> InterviewFeedback:
        candidate = self.analyse_resume(resume_path, target_role=target_role)
        session = self.prepare_interview(candidate, interview_type, difficulty, question_count)

        for idx, answer_text in answers.items():
            if idx < len(session.questions):
                q = session.questions[idx]
                self.record_answer(session, q.id, answer_text)

        score = self.evaluate_interview(session)
        return self.generate_feedback(score, candidate)


orchestrator = OrchestratorAgent()
