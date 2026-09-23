from __future__ import annotations

import hashlib
from pathlib import Path

from agents.resume_agent import resume_agent
from config.settings import settings
from database.db import db


class ResumeIngestionService:
    SUPPORTED_EXTENSIONS = {
        ".pdf",
        ".docx",
        ".doc",
        ".txt",
    }

    def discover_resumes(self) -> list[Path]:
        resume_dir = settings.RESUME_DIR

        if not resume_dir.exists():
            resume_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

        return sorted(
            [
                file
                for file in resume_dir.iterdir()
                if (
                    file.is_file()
                    and file.suffix.lower()
                    in self.SUPPORTED_EXTENSIONS
                )
            ]
        )

    def generate_candidate_id(
        self,
        resume_path: Path,
    ) -> str:
        """
        Generate a deterministic candidate ID from
        the resume file content.

        The same resume produces the same ID even
        when ingestion runs multiple times.
        """

        sha256 = hashlib.sha256()

        with resume_path.open("rb") as file:
            for chunk in iter(
                lambda: file.read(1024 * 1024),
                b"",
            ):
                sha256.update(chunk)

        return sha256.hexdigest()

    def ingest_resume(
        self,
        resume_path: Path,
    ):
        candidate_id = self.generate_candidate_id(
            resume_path
        )

        candidate = resume_agent.analyse(
            str(resume_path),
            candidate_id=candidate_id,
        )

        candidate.resume_file_path = str(
            resume_path.resolve()
        )

        db.save_candidate(candidate)

        return candidate


resume_ingestion_service = ResumeIngestionService()