"""
pages/1_Resume_Analysis.py

Recruiter Resume Screening:
Upload up to 10 resumes, save them permanently,
analyse each resume, and store candidates.
"""

import streamlit as st
from pathlib import Path

from config.settings import settings


st.set_page_config(
    page_title="Resume Screening",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Resume Screening")


# ─────────────────────────────────────────────────────────────────────────────
# Lazy load orchestrator
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_resource
def get_agent():
    from agents.orchestrator_agent import orchestrator
    return orchestrator


# ─────────────────────────────────────────────────────────────────────────────
# Save uploaded resume
# ─────────────────────────────────────────────────────────────────────────────

def save_uploaded_resume(uploaded_file):
    """
    Permanently save uploaded resume inside data/resumes/.
    """

    settings.RESUME_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    original_name = Path(uploaded_file.name).name

    file_path = settings.RESUME_DIR / original_name

    # Prevent overwriting an existing resume
    if file_path.exists():

        stem = file_path.stem
        suffix = file_path.suffix

        counter = 1

        while file_path.exists():

            file_path = (
                settings.RESUME_DIR
                / f"{stem}_{counter}{suffix}"
            )

            counter += 1

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return file_path


# ─────────────────────────────────────────────────────────────────────────────
# Main page
# ─────────────────────────────────────────────────────────────────────────────

def run():

    orchestrator = get_agent()

    st.markdown(
        """
        Upload candidate resumes for screening against a job description.

        **Maximum resumes per batch: 10**
        """
    )

    # ─────────────────────────────────────────────────────────────────────────
    # Job information
    # ─────────────────────────────────────────────────────────────────────────

    st.subheader("💼 Job Information")

    target_role = st.text_input(
        "Target Role",
        placeholder="Example: Junior AI Engineer"
    )

    job_desc = st.text_area(
        "Job Description",
        height=220,
        placeholder="Paste the complete job description here..."
    )

    st.divider()

    # ─────────────────────────────────────────────────────────────────────────
    # Multiple resume upload
    # ─────────────────────────────────────────────────────────────────────────

    st.subheader("📄 Upload Candidate Resumes")

    uploaded_files = st.file_uploader(
        "Select up to 10 resumes",
        type=["pdf", "docx", "doc", "txt"],
        accept_multiple_files=True
    )

    if uploaded_files:

        if len(uploaded_files) > 10:

            st.error(
                "❌ You can upload a maximum of 10 resumes."
            )

            return

        st.success(
            f"✅ {len(uploaded_files)} resume(s) selected."
        )

        # Show selected files
        for index, uploaded_file in enumerate(
            uploaded_files,
            start=1
        ):

            st.write(
                f"**{index}.** {uploaded_file.name}"
            )

    # ─────────────────────────────────────────────────────────────────────────
    # Analyse button
    # ─────────────────────────────────────────────────────────────────────────

    can_analyse = (
        uploaded_files
        and len(uploaded_files) > 0
        and target_role.strip()
        and job_desc.strip()
    )

    if st.button(
        "🚀 Analyse All Resumes",
        type="primary",
        disabled=not can_analyse
    ):

        st.divider()

        st.subheader("🔄 Resume Processing")

        progress = st.progress(0)

        results = []

        total = len(uploaded_files)

        for index, uploaded_file in enumerate(
            uploaded_files,
            start=1
        ):

            st.write(
                f"### Candidate {index}/{total}"
            )

            try:

                # ─────────────────────────────────────────────────────────────
                # STEP 1 — Save resume
                # ─────────────────────────────────────────────────────────────

                resume_path = save_uploaded_resume(
                    uploaded_file
                )

                st.write(
                    f"📁 Saved: `{resume_path.name}`"
                )

                # ─────────────────────────────────────────────────────────────
                # STEP 2 — Analyse resume
                # ─────────────────────────────────────────────────────────────

                with st.spinner(
                    f"Analysing {uploaded_file.name}..."
                ):

                    candidate = orchestrator.analyse_resume(
                        str(resume_path),
                        target_role=target_role,
                        job_description=job_desc
                    )

                # Store actual file path
                candidate.resume_file_path = str(
                    resume_path
                )

                results.append(
                    {
                        "candidate": candidate,
                        "file": uploaded_file.name,
                        "status": "success"
                    }
                )

                st.success(
                    f"✅ {candidate.name or uploaded_file.name} analysed successfully."
                )

            except Exception as e:

                results.append(
                    {
                        "candidate": None,
                        "file": uploaded_file.name,
                        "status": "failed",
                        "error": str(e)
                    }
                )

                st.error(
                    f"❌ Failed: {uploaded_file.name}"
                )

                st.error(
                    str(e)
                )

            progress.progress(
                index / total
            )

        # Save results in Streamlit session
        st.session_state.screening_candidates = results

        st.success(
            f"🎉 Finished processing {total} resume(s)."
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Results
    # ─────────────────────────────────────────────────────────────────────────

    results = st.session_state.get(
        "screening_candidates",
        []
    )

    if not results:
        return

    st.divider()

    st.header("👥 Processed Candidates")

    successful = [
        r for r in results
        if r["status"] == "success"
    ]

    failed = [
        r for r in results
        if r["status"] == "failed"
    ]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Resumes Uploaded",
        len(results)
    )

    col2.metric(
        "Successfully Analysed",
        len(successful)
    )

    col3.metric(
        "Failed",
        len(failed)
    )

    # ─────────────────────────────────────────────────────────────────────────
    # Candidate cards
    # ─────────────────────────────────────────────────────────────────────────

    for index, result in enumerate(
        successful,
        start=1
    ):

        candidate = result["candidate"]

        with st.expander(
            f"👤 Candidate {index}: {candidate.name or 'Unknown'}",
            expanded=False
        ):

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Experience",
                f"{candidate.years_of_experience:.1f} years"
            )

            col2.metric(
                "Skills",
                len(candidate.skills)
            )

            col3.metric(
                "Work Experience",
                len(candidate.experience)
            )

            st.write(
                "**Resume:**",
                result["file"]
            )

            st.write(
                "**Summary:**"
            )

            st.write(
                candidate.summary
            )

            st.write(
                "**Skills:**"
            )

            st.write(
                ", ".join(candidate.skills)
            )


run()