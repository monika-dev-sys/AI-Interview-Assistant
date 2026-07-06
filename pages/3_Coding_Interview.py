"""
pages/3_Coding_Interview.py
Coding interview: problem display, code editor, hints, simulated test runs, and review.
"""
import streamlit as st
from models.interview import InterviewType, DifficultyLevel

st.set_page_config(page_title="Coding Interview", page_icon="💻", layout="wide")
st.title("💻 Coding Interview")


@st.cache_resource
def get_agents():
    from agents.orchestrator_agent import orchestrator
    from agents.coding_agent import coding_agent
    return orchestrator, coding_agent


def run():
    orchestrator, coding_agent = get_agents()
    candidate = st.session_state.get("candidate")

    if "coding_session" not in st.session_state:
        st.session_state.coding_session = None
    if "coding_idx" not in st.session_state:
        st.session_state.coding_idx = 0
    if "hint_count" not in st.session_state:
        st.session_state.hint_count = 0
    if "code_review" not in st.session_state:
        st.session_state.code_review = None

    # ── Setup ─────────────────────────────────────────────────────────────────
    if st.session_state.coding_session is None:
        with st.form("coding_setup"):
            col1, col2 = st.columns(2)
            with col1:
                difficulty = st.selectbox("Difficulty", [d.value for d in DifficultyLevel], format_func=str.title)
                language = st.selectbox("Language", ["Python", "JavaScript", "Java", "C++", "Go"])
            with col2:
                role = st.text_input("Target Role", value=candidate.target_role if candidate else "Software Engineer")
                problem_count = st.slider("Number of Problems", 1, 5, 2)

            submitted = st.form_submit_button("🚀 Start Coding Interview", type="primary")

        if submitted:
            with st.spinner("Generating problems…"):
                from models.candidate import Candidate
                cand = candidate or Candidate(id="guest", name="Candidate", target_role=role)
                cand.target_role = role
                session = orchestrator.prepare_interview(
                    candidate=cand,
                    interview_type=InterviewType.CODING,
                    difficulty=DifficultyLevel(difficulty),
                    question_count=problem_count,
                    language=language,
                )
                st.session_state.coding_session = session
                st.session_state.coding_language = language
                st.session_state.coding_idx = 0
                st.rerun()
        return

    # ── Active problem ─────────────────────────────────────────────────────────
    session = st.session_state.coding_session
    questions = session.questions
    idx = st.session_state.coding_idx
    language = st.session_state.get("coding_language", "Python")

    if idx >= len(questions):
        st.success("🎉 All problems completed!")
        if st.button("🔄 Start New Session"):
            st.session_state.coding_session = None
            st.rerun()
        return

    question = questions[idx]

    col_left, col_right = st.columns([1, 1])

    # ── Problem statement ──────────────────────────────────────────────────────
    with col_left:
        st.markdown(f"### Problem {idx + 1} / {len(questions)}")
        with st.container(border=True):
            st.markdown(question.text)

        # Hints
        hint_col1, hint_col2 = st.columns(2)
        with hint_col1:
            if st.button("💡 Get Hint"):
                st.session_state.hint_count += 1
                hint = coding_agent.get_hint(
                    question.text,
                    st.session_state.get(f"code_{idx}", ""),
                    st.session_state.hint_count,
                )
                st.session_state[f"hint_{idx}"] = hint

        hint = st.session_state.get(f"hint_{idx}")
        if hint:
            st.info(f"**Hint {st.session_state.hint_count}:** {hint}")

    # ── Code editor ──────────────────────────────────────────────────────────
    with col_right:
        st.markdown(f"### Your Solution ({language})")
        # Starter code
        starter = getattr(question, "starter_code", "") or f"# Write your {language} solution here\n\ndef solution():\n    pass\n"
        code = st.text_area(
            "Code editor",
            value=st.session_state.get(f"code_{idx}", starter),
            height=350,
            key=f"code_editor_{idx}",
            label_visibility="collapsed",
        )
        st.session_state[f"code_{idx}"] = code

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("▶️ Review Code", type="primary"):
                with st.spinner("Reviewing…"):
                    review = coding_agent.review_code(question.text, code, language)
                    st.session_state.code_review = review

        with c2:
            if st.button("➡️ Next Problem"):
                orchestrator.record_answer(session, question.id, code)
                st.session_state.coding_idx += 1
                st.session_state.hint_count = 0
                st.session_state.code_review = None
                st.rerun()

        with c3:
            if st.button("🛑 End Session"):
                st.session_state.coding_session = None
                st.rerun()

    # ── Review results ────────────────────────────────────────────────────────
    review = st.session_state.code_review
    if review:
        st.divider()
        st.subheader("📋 Code Review")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Correctness", f"{review.get('correctness', 0)}/10")
        m2.metric("Code Quality", f"{review.get('code_quality', 0)}/10")
        m3.metric("Time Complexity", review.get("time_complexity", "N/A"))
        m4.metric("Space Complexity", review.get("space_complexity", "N/A"))

        st.markdown(f"**Overall Score:** {review.get('overall_score', 0)}/10")
        st.markdown(review.get("feedback", ""))

        c1, c2 = st.columns(2)
        with c1:
            if review.get("strengths"):
                st.markdown("**✅ Strengths**")
                for s in review["strengths"]:
                    st.markdown(f"- {s}")
        with c2:
            if review.get("issues"):
                st.markdown("**⚠️ Issues**")
                for i in review["issues"]:
                    st.markdown(f"- {i}")

        if review.get("optimised_solution"):
            with st.expander("🔍 Optimised Solution"):
                st.code(review["optimised_solution"], language=language.lower())


run()
