"""
database/db.py
SQLite-backed persistence layer using raw SQL via sqlite3.
Stores sessions, candidates, scores, and feedback as JSON blobs
alongside indexed columns for fast lookups.
"""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from typing import Optional
from config.settings import settings
from utils.logger import logger

DB_PATH = settings.DATABASE_DIR / "interview_history.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


class Database:

    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = str(db_path)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _init_db(self) -> None:
        schema = SCHEMA_PATH.read_text()
        with self._get_conn() as conn:
            conn.executescript(schema)
        logger.info(f"Database initialised at {self.db_path}")

    # ── Candidates ────────────────────────────────────────────────────────────

    def save_candidate(self, candidate) -> None:
        sql = """
            INSERT OR REPLACE INTO candidates (id, name, email, data_json)
            VALUES (?, ?, ?, ?)
        """
        with self._get_conn() as conn:
            conn.execute(sql, (
                candidate.id, candidate.name, candidate.email,
                candidate.model_dump_json(),
            ))

    def get_candidate(self, candidate_id: str):
        from models.candidate import Candidate
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT data_json FROM candidates WHERE id = ?", (candidate_id,)
            ).fetchone()
        if row:
            return Candidate.model_validate_json(row["data_json"])
        return None

    # ── Sessions ──────────────────────────────────────────────────────────────

    def save_session(self, session) -> None:
        sql = """
            INSERT OR REPLACE INTO sessions
              (id, candidate_id, interview_type, difficulty, target_role, started_at, is_complete, data_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        with self._get_conn() as conn:
            conn.execute(sql, (
                session.id, session.candidate_id,
                session.interview_type.value, session.difficulty.value,
                session.target_role,
                session.started_at.isoformat(),
                int(session.is_complete),
                session.model_dump_json(),
            ))

    def update_session(self, session) -> None:
        self.save_session(session)

    def get_session(self, session_id: str):
        from models.interview import InterviewSession
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT data_json FROM sessions WHERE id = ?", (session_id,)
            ).fetchone()
        if row:
            return InterviewSession.model_validate_json(row["data_json"])
        return None

    def list_sessions(self, candidate_id: str) -> list:
        from models.interview import InterviewSession
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT data_json FROM sessions WHERE candidate_id = ? ORDER BY started_at DESC",
                (candidate_id,),
            ).fetchall()
        return [InterviewSession.model_validate_json(r["data_json"]) for r in rows]

    # ── Scores ────────────────────────────────────────────────────────────────

    def save_score(self, score) -> None:
        sql = """
            INSERT OR REPLACE INTO scores (session_id, candidate_id, overall_score, data_json)
            VALUES (?, ?, ?, ?)
        """
        with self._get_conn() as conn:
            conn.execute(sql, (
                score.session_id, score.candidate_id,
                score.overall_score, score.model_dump_json(),
            ))

    def get_score(self, session_id: str):
        from models.score import InterviewScore
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT data_json FROM scores WHERE session_id = ?", (session_id,)
            ).fetchone()
        if row:
            return InterviewScore.model_validate_json(row["data_json"])
        return None

    # ── Feedback ──────────────────────────────────────────────────────────────

    def save_feedback(self, feedback) -> None:
        sql = """
            INSERT OR REPLACE INTO feedback (session_id, candidate_id, data_json)
            VALUES (?, ?, ?)
        """
        with self._get_conn() as conn:
            conn.execute(sql, (
                feedback.session_id, feedback.candidate_id,
                feedback.model_dump_json(),
            ))

    def get_feedback(self, session_id: str):
        from models.feedback import InterviewFeedback
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT data_json FROM feedback WHERE session_id = ?", (session_id,)
            ).fetchone()
        if row:
            return InterviewFeedback.model_validate_json(row["data_json"])
        return None


db = Database()
