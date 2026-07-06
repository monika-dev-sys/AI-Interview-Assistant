"""
pages/2_Mock_Interview.py
Interactive mock interview: Q&A with timer, follow-ups, and progress tracking.
"""
import streamlit as st
import time
from models.interview import InterviewType, DifficultyLevel

st.set_page_config(page_title="Mock Interview", page_icon="🗣️", layout="wide")
st.title("🗣️ Mock Interview")


@st.cache_resource
def get_orchestrator():
    from agents.orchestrator_agent import orchestrator
    return orchestrator


def run():
    orchestrator = get_orchestrator()
    candidate = st.session_state.get("candidate")

    # ── Setup form ────────────────────────────────────────────────────────────
    if not st.session_state.get("interview_started"):
        st.markdown("Configure your mock interview session.")

        if not candidate:
            st.info("💡 For a personalised experience, analyse your resume first.")

        with st.form("interview_setup"):
            col1, col2 = st.columns(2)
            with col1:
                interview_type = st.selectbox(
                    "Interview Type",
                    options=[t.value for t in InterviewType],
                    format_func=lambda x: x.title(),
                )
                difficulty = st.selectbox(
                    "Difficulty",
                    options=[d.value for d in DifficultyLevel],
                    format_func=lambda x: x.title(),
                )
            with col2:
                role = st.text_input(
                    "Target Role",
                    value=candidate.target_role if candidate else "Software Engineer",
                )
                question_count = st.slider("Number of Questions", 3, 10, 5)

            submitted = st.form_submit_button("🚀 Generate Interview", type="primary")

        if submitted:
            with st.spinner("Generating tailored questions…"):
                # Create a minimal candidate if none exists
                from models.candidate import Candidate
                cand = candidate or Candidate(id="guest", name="Candidate", target_role=role)
                cand.target_role = role

                session = orchestrator.prepare_interview(
                    candidate=cand,
                    interview_type=InterviewType(interview_type),
                    difficulty=DifficultyLevel(difficulty),
                    question_count=question_count,
                )
                st.session_state.session = session
                st.session_state.interview_started = True
                st.session_state.current_question_idx = 0
                st.session_state.answers = {}
                st.rerun()
        return

    # ── Active interview ──────────────────────────────────────────────────────
    session = st.session_state.session
    questions = session.questions
    idx = st.session_state.current_question_idx
    total = len(questions)

    # Progress bar
    st.progress(idx / total, text=f"Question {idx + 1} of {total}")

    if idx >= total:
        # All answered — evaluate
        st.success("🎉 You've completed all questions!")
        if st.button("📊 Get My Score & Feedback", type="primary"):
            with st.spinner("Evaluating your answers…"):
                score = orchestrator.evaluate_interview(session)
                st.session_state.score = score
                cand = st.session_state.get("candidate") or \
                    __import__("models.candidate", fromlist=["Candidate"]).Candidate(
                        id="guest", name="Candidate"
                    )
                feedback = orchestrator.generate_feedback(score, cand)
                st.session_state.feedback = feedback
            st.switch_page("pages/4_Feedback_Report.py")
        return

    question = questions[idx]

    # Question card
    with st.container(border=True):
        st.markdown(f"### Q{idx + 1}. {question.text}")
        if question.expected_topics:
            with st.expander("💡 Topics to cover (show after answering)"):
                for t in question.expected_topics:
                    st.markdown(f"- {t}")

    # Answer area
    answer_key = f"answer_{idx}"
    answer = st.text_area(
        "Your answer",
        key=answer_key,
        height=200,
        placeholder="Type your answer here…",
    )

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button("✅ Submit Answer", type="primary"):
            if answer.strip():
                orchestrator.record_answer(session, question.id, answer.strip())
                st.session_state.answers[idx] = answer.strip()
                st.session_state.current_question_idx += 1
                st.rerun()
            else:
                st.warning("Please write an answer before submitting.")

    with col2:
        if st.button("⏭️ Skip"):
            orchestrator.record_answer(session, question.id, "[Skipped]")
            st.session_state.current_question_idx += 1
            st.rerun()

    # Follow-up questions sidebar
    if question.follow_ups:
        with st.sidebar:
            st.markdown("### 🔄 Follow-up questions")
            for fq in question.follow_ups:
                st.markdown(f"- {fq}")

    # End early
    st.divider()
    if st.button("🛑 End Interview Early"):
        st.session_state.interview_started = False
        st.rerun()


run()
