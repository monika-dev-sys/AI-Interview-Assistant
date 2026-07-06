"""
utils/constants.py
Application-wide constants.
"""

SUPPORTED_RESUME_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}

INTERVIEW_TYPES = ["Technical", "Behavioral", "Coding", "Mixed"]

DIFFICULTY_LABELS = {
    "junior": "Junior (0–2 yrs)",
    "mid": "Mid-level (2–5 yrs)",
    "senior": "Senior (5–8 yrs)",
    "staff": "Staff / Principal (8+ yrs)",
}

SCORE_BANDS = {
    (90, 100): ("Outstanding", "#22c55e"),
    (75, 90):  ("Strong",      "#84cc16"),
    (60, 75):  ("Good",        "#eab308"),
    (45, 60):  ("Fair",        "#f97316"),
    (0,  45):  ("Needs Work",  "#ef4444"),
}

HIRE_RECOMMENDATION_COLORS = {
    "Strong Hire": "#22c55e",
    "Hire":        "#84cc16",
    "No Hire":     "#f97316",
    "Strong No Hire": "#ef4444",
}

MAX_QUESTIONS_PER_SESSION = 10
DEFAULT_ANSWER_TIME_SECONDS = 180  # 3 minutes
CODING_ANSWER_TIME_SECONDS = 1200  # 20 minutes
