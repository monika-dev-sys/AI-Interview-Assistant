from services.resume_ingestion_service import resume_ingestion_service
from services.resume_screening_service import resume_screening_service


JOB_ROLE = "Junior AI Engineer"

REQUIRED_SKILLS = [
    "Python",
    "FastAPI",
    "GenAI",
    "RAG",
    "SQL",
]


def main():
    print("=" * 70)
    print("AI RESUME SCREENING PIPELINE")
    print("=" * 70)

    resumes = resume_ingestion_service.discover_resumes()

    print(f"\nResumes discovered: {len(resumes)}")

    candidates = []

    for resume_path in resumes:
        print(f"\nProcessing: {resume_path.name}")

        candidate = resume_ingestion_service.ingest_resume(
            resume_path
        )

        candidates.append(candidate)

        print(f"Candidate: {candidate.name}")
        print(f"Candidate ID: {candidate.id}")

    print("\n" + "=" * 70)
    print("SCREENING CANDIDATES")
    print("=" * 70)

    results = resume_screening_service.screen_all_candidates(
        job_role=JOB_ROLE,
        required_skills=REQUIRED_SKILLS,
        candidates=candidates,
    )

    print("\n" + "=" * 70)
    print("RANKING")
    print("=" * 70)

    for result in results:
        print(
            f"\nRank #{result['rank']}"
        )

        print(
            f"Candidate: {result['candidate_name']}"
        )

        print(
            f"Final Score: {result['final_score']}"
        )

        print(
            f"Skill Score: {result['skill_score']}"
        )

        print(
            f"Semantic Score: {result['semantic_score']}"
        )

        print(
            f"Experience Score: "
            f"{result['experience_score']}"
        )

        print(
            f"Project Score: "
            f"{result['project_score']}"
        )

        print(
            f"Education Score: "
            f"{result['education_score']}"
        )

        print(
            f"Matched Skills: "
            f"{result['matched_skills']}"
        )

        print(
            f"Missing Skills: "
            f"{result['missing_skills']}"
        )

    print("\n" + "=" * 70)
    print("TOP 3")
    print("=" * 70)

    for result in results[:3]:
        print(
            f"#{result['rank']} "
            f"{result['candidate_name']} "
            f"({result['final_score']})"
        )


if __name__ == "__main__":
    main()