from __future__ import annotations

import re
import uuid
from typing import Any

from database.db import db
from services.vector_db_service import vector_db_service


class ResumeScreeningService:
    """
    Recruitment screening pipeline.

    Flow:
        Job Role + Required Skills
                ↓
        Candidate resumes
                ↓
        Structured skill matching
                ↓
        Semantic resume matching
                ↓
        Experience / project / education signals
                ↓
        Final screening score
                ↓
        Save results to SQLite
                ↓
        Rank candidates
    """

    def _normalise(self, value: str) -> str:
        value = value.lower().strip()
        value = re.sub(r"[^a-z0-9+#.\s-]", " ", value)
        value = re.sub(r"\s+", " ", value)
        return value

    def _normalise_skill(self, skill: str) -> str:
        return self._normalise(skill)

    def _skill_matches(
        self,
        required_skill: str,
        candidate_skills: list[str],
        resume_text: str,
    ) -> bool:

        required = self._normalise_skill(required_skill)

        candidate_skill_text = " ".join(
            self._normalise_skill(skill)
            for skill in candidate_skills
        )

        resume_text_normalised = self._normalise(
            resume_text
        )

        return (
            required in candidate_skill_text
            or required in resume_text_normalised
        )

    def calculate_skill_score(
        self,
        required_skills: list[str],
        candidate,
    ) -> tuple[float, list[str], list[str]]:

        if not required_skills:
            return 0.0, [], []

        matched = []
        missing = []

        for skill in required_skills:
            if self._skill_matches(
                skill,
                candidate.skills,
                candidate.resume_text,
            ):
                matched.append(skill)
            else:
                missing.append(skill)

        score = (
            len(matched) / len(required_skills)
        ) * 100

        return round(score, 2), matched, missing

    def calculate_experience_score(
        self,
        candidate,
    ) -> float:
        """
        Converts candidate experience into
        a normalized 0-100 score.
        """

        years = float(
            candidate.years_of_experience or 0
        )

        if years <= 0:
            return 0.0

        if years >= 5:
            return 100.0

        return round(
            (years / 5) * 100,
            2,
        )

    def calculate_project_score(
        self,
        candidate,
        required_skills: list[str],
    ) -> float:

        if not candidate.resume_text:
            return 0.0

        text = self._normalise(
            candidate.resume_text
        )

        project_terms = [
            "project",
            "developed",
            "built",
            "implemented",
            "application",
            "system",
            "api",
            "platform",
        ]

        project_signal = sum(
            1
            for term in project_terms
            if term in text
        )

        skill_signal = sum(
            1
            for skill in required_skills
            if self._normalise(skill) in text
        )

        score = min(
            100,
            (project_signal / len(project_terms))
            * 50
            + (
                (skill_signal / len(required_skills))
                * 50
                if required_skills
                else 0
            ),
        )

        return round(score, 2)

    def calculate_education_score(
        self,
        candidate,
    ) -> float:

        if not candidate.education:
            return 0.0

        relevant = 0

        for education in candidate.education:

            degree_text = self._normalise(
                f"{education.degree} "
                f"{education.field}"
            )

            if any(
                keyword in degree_text
                for keyword in [
                    "computer",
                    "software",
                    "information technology",
                    "information science",
                ]
            ):
                relevant += 1

        if relevant:
            return 100.0

        return 50.0

    def calculate_semantic_score(
        self,
        candidate,
        job_role: str,
        required_skills: list[str],
    ) -> float:

        query = (
            f"Role: {job_role}. "
            f"Required skills: "
            f"{', '.join(required_skills)}. "
            "Relevant professional experience, "
            "projects, technical skills and education."
        )

        results = vector_db_service.search_resume(
            candidate_id=candidate.id,
            query=query,
            n=5,
        )

        if not results:
            return 0.0

        distances = [
            result["distance"]
            for result in results
            if result.get("distance") is not None
        ]

        if not distances:
            return 0.0

        best_distance = min(distances)

        semantic_score = max(
            0.0,
            min(
                100.0,
                (1.0 - best_distance) * 100.0,
            ),
        )

        return round(
            semantic_score,
            2,
        )

    def calculate_final_score(
        self,
        skill_score: float,
        semantic_score: float,
        experience_score: float,
        project_score: float,
        education_score: float,
    ) -> float:

        score = (
            skill_score * 0.35
            + semantic_score * 0.25
            + experience_score * 0.15
            + project_score * 0.15
            + education_score * 0.10
        )

        return round(score, 2)

    def screen_candidate(
        self,
        candidate,
        job_role: str,
        required_skills: list[str],
    ) -> dict[str, Any]:

        skill_score, matched_skills, missing_skills = (
            self.calculate_skill_score(
                required_skills,
                candidate,
            )
        )

        semantic_score = (
            self.calculate_semantic_score(
                candidate,
                job_role,
                required_skills,
            )
        )

        experience_score = (
            self.calculate_experience_score(
                candidate
            )
        )

        project_score = (
            self.calculate_project_score(
                candidate,
                required_skills,
            )
        )

        education_score = (
            self.calculate_education_score(
                candidate
            )
        )

        final_score = (
            self.calculate_final_score(
                skill_score,
                semantic_score,
                experience_score,
                project_score,
                education_score,
            )
        )

        return {
            "candidate_id": candidate.id,
            "candidate_name": candidate.name,
            "skill_score": skill_score,
            "semantic_score": semantic_score,
            "experience_score": experience_score,
            "project_score": project_score,
            "education_score": education_score,
            "final_score": final_score,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
        }

    def screen_all_candidates(
        self,
        job_role: str,
        required_skills: list[str],
        candidates: list,
    ) -> list[dict[str, Any]]:
        """
        Screen all candidates for a job.

        The job and every screening result are
        persisted into SQLite.
        """

        # ---------------------------------------------------------
        # 1. Create a unique Job ID
        # ---------------------------------------------------------

        job_id = str(uuid.uuid4())

        # ---------------------------------------------------------
        # 2. Save the recruitment job
        # ---------------------------------------------------------

        db.create_job(
            job_id=job_id,
            role=job_role,
            required_skills=required_skills,
        )

        # ---------------------------------------------------------
        # 3. Screen every candidate
        # ---------------------------------------------------------

        results = []

        for candidate in candidates:

            result = self.screen_candidate(
                candidate,
                job_role,
                required_skills,
            )

            result["job_id"] = job_id

            results.append(result)

        # ---------------------------------------------------------
        # 4. Sort candidates by final score
        # ---------------------------------------------------------

        results.sort(
            key=lambda item: item["final_score"],
            reverse=True,
        )

        # ---------------------------------------------------------
        # 5. Assign rank + save results to SQLite
        # ---------------------------------------------------------

        for index, result in enumerate(
            results,
            start=1,
        ):

            result["rank"] = index

            db.save_screening_result(
                result_id=str(uuid.uuid4()),
                job_id=job_id,
                candidate_id=result["candidate_id"],
                skill_score=result["skill_score"],
                semantic_score=result["semantic_score"],
                experience_score=result[
                    "experience_score"
                ],
                project_score=result[
                    "project_score"
                ],
                education_score=result[
                    "education_score"
                ],
                final_score=result["final_score"],
                rank=result["rank"],
                matched_skills=result[
                    "matched_skills"
                ],
                missing_skills=result[
                    "missing_skills"
                ],
                status="SCREENED",
            )

        # ---------------------------------------------------------
        # 6. Return ranked results
        # ---------------------------------------------------------

        return results


resume_screening_service = ResumeScreeningService()