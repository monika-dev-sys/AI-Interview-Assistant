"""
pages/4_Feedback_Report.py
Displays the full, scored feedback report after an interview.
"""
import streamlit as st

st.set_page_config(page_title="Feedback Report", page_icon="📊", layout="wide")
st.title("📊 Interview Feedback Report")


def score_color(score: float, max_score: float = 100) -> str:
    pct = score / max_score * 100
    if pct >= 80: return "#22c55e"
    if pct >= 60: return "#84cc16"
    if pct >= 40: return "#eab308"
    return "#ef4444"


def score_bar(label: str, score: float, max_score: float = 100):
    color = score_color(score, max_score)
    pct = score / max_score * 100
    st.markdown(
        f"""
        <div style="margin-bottom:8px">
          <span style="font-weight:600">{label}</span>
          <span style="float:right;color:{color};font-weight:700">{score:.0f}/{max_score:.0f}</span>
          <div style="background:#e5e7eb;border-radius:4px;height:10px;margin-top:4px">
            <div style="background:{color};width:{pct:.0f}%;height:10px;border-radius:4px"></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def run():
    feedback = st.session_state.get("feedback")
    score = st.session_state.get("score")

    if not feedback or not score:
        st.warning("No feedback available yet. Complete a mock interview first.")
        if st.button("← Go to Mock Interview"):
            st.switch_page("pages/2_Mock_Interview.py")
        return

    # ── Header ────────────────────────────────────────────────────────────────
    rec_colors = {
        "Strong Hire": "#22c55e", "Hire": "#84cc16",
        "No Hire": "#f97316", "Strong No Hire": "#ef4444",
    }
    rec_color = rec_colors.get(score.hire_recommendation, "#6b7280")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### {feedback.candidate_name} — {feedback.target_role}")
        st.markdown(feedback.executive_summary)
    with col2:
        st.markdown(
            f"""<div style="text-align:center;padding:16px;border-radius:8px;
            background:{rec_color}20;border:2px solid {rec_color}">
            <div style="font-size:1.8rem;font-weight:800;color:{rec_color}">{score.overall_score:.0f}</div>
            <div style="font-size:0.75rem;color:#6b7280">Overall Score</div>
            <div style="font-weight:700;color:{rec_color};margin-top:4px">{score.hire_recommendation}</div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Score breakdown ───────────────────────────────────────────────────────
    st.subheader("Score Breakdown")
    score_bar("Technical Accuracy", score.technical_score)
    score_bar("Communication & Clarity", score.communication_score)
    score_bar("Problem Solving", score.problem_solving_score)
    score_bar("Confidence", score.confidence_score)

    st.divider()

    # ── Strengths & improvements ──────────────────────────────────────────────
    col_s, col_i = st.columns(2)
    with col_s:
        st.markdown("### ✅ Strengths")
        for s in feedback.strengths:
            st.markdown(f"- {s}")
    with col_i:
        st.markdown("### 🔧 Areas for Improvement")
        for a in feedback.areas_for_improvement:
            st.markdown(f"- {a}")

    st.divider()

    # ── Detailed sections ─────────────────────────────────────────────────────
    st.subheader("Detailed Feedback")
    for section in feedback.sections:
        with st.expander(f"📌 {section.title}", expanded=True):
            st.markdown(section.content)
            if section.action_items:
                st.markdown("**Action Items:**")
                for item in section.action_items:
                    st.markdown(f"- {item}")

    st.divider()

    # ── Per-question scores ───────────────────────────────────────────────────
    if score.question_scores:
        st.subheader("Per-Question Breakdown")
        for i, qs in enumerate(score.question_scores):
            with st.expander(f"Q{i+1}: {qs.question_text[:80]}… — Score: {qs.overall_score:.1f}/10"):
                st.markdown(f"**Your Answer:** {qs.answer_text[:300]}…")
                for dim in qs.dimensions:
                    score_bar(dim.dimension, dim.score, max_score=10)
                if qs.highlights:
                    st.markdown("**Highlights:** " + " · ".join(qs.highlights))
                if qs.gaps:
                    st.markdown("**Gaps:** " + " · ".join(qs.gaps))

    st.divider()

    # ── Study plan ────────────────────────────────────────────────────────────
    st.subheader("📚 Recommended Study Topics")
    cols = st.columns(min(len(feedback.recommended_topics), 4))
    for col, topic in zip(cols, feedback.recommended_topics):
        col.markdown(f"**📌 {topic}**")

    if feedback.recommended_resources:
        st.subheader("🔗 Resources")
        for res in feedback.recommended_resources:
            icon = {"book": "📖", "course": "🎓", "article": "📰", "practice": "💻"}.get(res.get("type"), "🔗")
            url = res.get("url", "#")
            title = res.get("title", "Resource")
            st.markdown(f"{icon} [{title}]({url})")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Start New Interview"):
            for key in ["session", "score", "feedback", "interview_started", "current_question_idx", "answers"]:
                st.session_state[key] = None if key != "answers" else {}
            st.switch_page("pages/2_Mock_Interview.py")
    with col2:
        if st.button("📜 View History"):
            st.switch_page("pages/5_Interview_History.py")


run()
