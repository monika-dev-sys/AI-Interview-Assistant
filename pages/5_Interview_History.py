"""
pages/5_Interview_History.py
Browse past interview sessions, scores, and feedback.
"""
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Interview History", page_icon="📜", layout="wide")
st.title("📜 Interview History")


def run():
    candidate = st.session_state.get("candidate")

    if not candidate:
        st.info("No candidate profile loaded. Analyse a resume first to see your history.")
        if st.button("← Resume Analysis"):
            st.switch_page("pages/1_Resume_Analysis.py")
        return

    from database.db import db
    sessions = db.list_sessions(candidate.id)

    if not sessions:
        st.info("No completed interviews yet. Start a mock interview to build your history!")
        return

    st.markdown(f"Showing **{len(sessions)}** interview session(s) for **{candidate.name}**.")

    for session in sessions:
        score = db.get_score(session.id) if session.id else None
        feedback = db.get_feedback(session.id) if session.id else None

        rec = score.hire_recommendation if score else "—"
        rec_colors = {
            "Strong Hire": "🟢", "Hire": "🟡",
            "No Hire": "🟠", "Strong No Hire": "🔴", "—": "⚪",
        }
        emoji = rec_colors.get(rec, "⚪")

        header = (
            f"{emoji} {session.interview_type.value.title()} | "
            f"{session.difficulty.value.title()} | "
            f"{session.started_at.strftime('%b %d, %Y %H:%M') if hasattr(session.started_at, 'strftime') else str(session.started_at)[:16]}"
        )

        with st.expander(header):
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Questions", len(session.questions))
            col2.metric("Answers", len(session.answers))
            col3.metric("Duration", f"{session.duration_minutes or '—'} min")
            if score:
                col4.metric("Overall Score", f"{score.overall_score:.0f}/100")

            if score:
                st.markdown(f"**Recommendation:** {score.hire_recommendation}")

            if feedback:
                st.markdown(f"**Summary:** {feedback.executive_summary}")
                if st.button(f"📄 View Full Report", key=f"report_{session.id}"):
                    st.session_state.feedback = feedback
                    st.session_state.score = score
                    st.switch_page("pages/4_Feedback_Report.py")


run()
