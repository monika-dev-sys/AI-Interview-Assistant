"""
pages/1_Resume_Analysis.py
Resume upload, parsing, and job-match analysis.
"""
import streamlit as st
import tempfile
import os
from pathlib import Path

st.set_page_config(page_title="Resume Analysis", page_icon="📄", layout="wide")
st.title("📄 Resume Analysis")

# ── Lazy imports (avoid heavy imports on other pages) ─────────────────────────
@st.cache_resource
def get_agent():
    from agents.orchestrator_agent import orchestrator
    return orchestrator


def run():
    orchestrator = get_agent()

    st.markdown("Upload your resume and (optionally) a job description to get a personalised match score.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Upload Resume")
        uploaded = st.file_uploader(
            "Supported formats: PDF, DOCX, TXT",
            type=["pdf", "docx", "doc", "txt"],
        )
        target_role = st.text_input("Target role", placeholder="e.g. Senior Backend Engineer")

    with col2:
        st.subheader("Job Description (optional)")
        job_desc = st.text_area(
            "Paste the job description to get a match score",
            height=200,
            placeholder="Paste job description here...",
        )

    if st.button("🔍 Analyse Resume", type="primary", disabled=uploaded is None):
        with st.spinner("Parsing resume and extracting insights…"):
            # Save upload to temp file
            suffix = Path(uploaded.name).suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded.read())
                tmp_path = tmp.name

            try:
                candidate = orchestrator.analyse_resume(
                    tmp_path,
                    target_role=target_role,
                    job_description=job_desc,
                )
                st.session_state.candidate = candidate
            finally:
                os.unlink(tmp_path)

    # ── Display results ───────────────────────────────────────────────────────
    candidate = st.session_state.get("candidate")
    if not candidate:
        return

    st.divider()
    st.success(f"✅ Resume analysed for **{candidate.name}**")

    col1, col2, col3 = st.columns(3)
    col1.metric("Years of Experience", f"{candidate.years_of_experience:.1f}")
    col2.metric("Skills Identified", len(candidate.skills))
    col3.metric("Work Experience", len(candidate.experience))

    with st.expander("📝 Professional Summary", expanded=True):
        st.write(candidate.summary)

    col_a, col_b = st.columns(2)

    with col_a:
        with st.expander("🛠️ Skills", expanded=True):
            cols = st.columns(3)
            for i, skill in enumerate(candidate.skills):
                cols[i % 3].markdown(f"• {skill}")

    with col_b:
        with st.expander("💼 Work Experience", expanded=True):
            for exp in candidate.experience:
                st.markdown(f"**{exp.title}** at {exp.company} _{exp.duration}_")
                for r in exp.responsibilities[:3]:
                    st.markdown(f"  - {r}")

    # ── Job match ─────────────────────────────────────────────────────────────
    if job_desc and st.button("📊 Run Job Match Analysis"):
        with st.spinner("Comparing profile to job description…"):
            match = orchestrator.match_candidate_to_job(candidate, job_desc)

        score = match.get("match_score", 0)
        color = "#22c55e" if score >= 75 else "#eab308" if score >= 50 else "#ef4444"
        st.markdown(
            f"<h2 style='color:{color}'>Match Score: {score}/100</h2>",
            unsafe_allow_html=True,
        )
        st.markdown(match.get("summary", ""))

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**✅ Strengths**")
            for s in match.get("strengths", []):
                st.markdown(f"- {s}")
        with c2:
            st.markdown("**⚠️ Gaps**")
            for g in match.get("gaps", []):
                st.markdown(f"- {g}")

    if candidate:
        st.divider()
        if st.button("▶️ Start Mock Interview with this profile →", type="primary"):
            st.switch_page("pages/2_Mock_Interview.py")


run()
