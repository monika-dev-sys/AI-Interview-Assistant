"""
app.py — Ollama edition
AI Interview Assistant entry point with Ollama health checks.
"""
import streamlit as st

st.set_page_config(
    page_title="AI Interview Assistant (Ollama)",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state defaults ────────────────────────────────────────────────────
defaults = {
    "candidate": None,
    "session": None,
    "score": None,
    "feedback": None,
    "current_question_idx": 0,
    "answers": {},
    "interview_started": False,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ── Ollama health check (sidebar) ─────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_llm_service():
    from services.llm_service import llm_service
    return llm_service


with st.sidebar:
    st.markdown("### ⚙️ Ollama Status")
    try:
        svc = get_llm_service()
        local_models = svc.list_local_models()
        from config.settings import settings

        model_ok = any(settings.OLLAMA_MODEL in m for m in local_models)
        embed_ok = any(settings.OLLAMA_EMBED_MODEL in m for m in local_models)

        st.success(f"✅ Ollama connected\n`{settings.OLLAMA_BASE_URL}`")
        st.markdown(
            f"{'✅' if model_ok else '❌'} **LLM:** `{settings.OLLAMA_MODEL}`"
        )
        st.markdown(
            f"{'✅' if embed_ok else '❌'} **Embed:** `{settings.OLLAMA_EMBED_MODEL}`"
        )

        if not model_ok:
            st.warning(f"Run: `ollama pull {settings.OLLAMA_MODEL}`")
        if not embed_ok:
            st.warning(f"Run: `ollama pull {settings.OLLAMA_EMBED_MODEL}`")

        if local_models:
            with st.expander("All local models"):
                for m in local_models:
                    st.caption(m)

        if st.button("🔄 Pull LLM model", disabled=model_ok):
            with st.spinner(f"Pulling {settings.OLLAMA_MODEL}…"):
                svc.pull_model(settings.OLLAMA_MODEL)
            st.rerun()

    except Exception as e:
        st.error(f"❌ Ollama unreachable\n\n{e}")
        st.info("Start Ollama: `ollama serve`")


# ── Home page ─────────────────────────────────────────────────────────────────
st.title("🎯 AI Interview Assistant")
st.caption("Powered by Ollama · llama3.1:70b · 100% local, no API keys")

st.markdown(
    """
    **Your personal AI-powered interview coach — running entirely on your machine.**
    Practice technical, behavioural, and coding interviews with a local LLM,
    then get detailed, actionable feedback to level up.
    """
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📄 Resume Analysis")
    st.markdown("Upload your resume and get instant insights about your profile and job match score.")
    if st.button("Start with Resume →", use_container_width=True):
        st.switch_page("pages/1_Resume_Analysis.py")

with col2:
    st.markdown("### 🗣️ Mock Interview")
    st.markdown("Practice technical and behavioural questions tailored to your target role.")
    if st.button("Start Mock Interview →", use_container_width=True):
        st.switch_page("pages/2_Mock_Interview.py")

with col3:
    st.markdown("### 💻 Coding Interview")
    st.markdown("Solve coding problems with AI hints, code review, and complexity analysis.")
    if st.button("Start Coding Interview →", use_container_width=True):
        st.switch_page("pages/3_Coding_Interview.py")

st.divider()

st.markdown("### How it works")
steps = [
    ("1️⃣", "Upload Resume", "Skills, experience, and education extracted locally."),
    ("2️⃣", "Choose Interview", "Pick type (technical / behavioural / coding) and difficulty."),
    ("3️⃣", "Practice", "Answer llama3.1:70b-generated questions at your own pace."),
    ("4️⃣", "Get Feedback", "Detailed report with scores, strengths, and a study plan."),
]
cols = st.columns(4)
for col, (icon, title, desc) in zip(cols, steps):
    with col:
        st.markdown(f"**{icon} {title}**")
        st.caption(desc)

st.divider()
st.markdown("### 🔒 Privacy")
st.info(
    "All processing happens **locally on your machine** via Ollama. "
    "No data is sent to any cloud service. Your resumes and answers never leave your device."
)
