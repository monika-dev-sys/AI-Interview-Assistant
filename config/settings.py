"""
config/settings.py
Central configuration loaded from environment variables — Ollama edition.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / "config" / ".env")


class Settings:
    # ── Paths ─────────────────────────────────────────────────────────────────
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    RESUME_DIR: Path = BASE_DIR / "data" / "resumes"
    TRANSCRIPT_DIR: Path = BASE_DIR / "data" / "transcripts"
    REPORT_DIR: Path = BASE_DIR / "data" / "reports"
    EMBEDDING_DIR: Path = BASE_DIR / "data" / "embeddings"
    DATABASE_DIR: Path = BASE_DIR / "database"
    PROMPT_DIR: Path = BASE_DIR / "prompts"

    # ── Ollama ────────────────────────────────────────────────────────────────
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
    OLLAMA_EMBED_MODEL: str = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
    OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", "300"))
    OLLAMA_TEMPERATURE: float = float(os.getenv("OLLAMA_TEMPERATURE", "0.7"))
    OLLAMA_NUM_CTX: int = int(os.getenv("OLLAMA_NUM_CTX", "8192"))

    # ── Vector DB ─────────────────────────────────────────────────────────────
    CHROMA_PERSIST_DIR: str = os.getenv(
        "CHROMA_PERSIST_DIR", str(BASE_DIR / "data" / "embeddings")
    )

    # ── SQL Database ──────────────────────────────────────────────────────────
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR}/database/interview_history.db",
    )

    # ── App ───────────────────────────────────────────────────────────────────
    APP_NAME: str = os.getenv("APP_NAME", "AI Interview Assistant (Ollama)")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    MAX_RESUME_SIZE_MB: int = int(os.getenv("MAX_RESUME_SIZE_MB", "10"))
    SESSION_TIMEOUT_MINUTES: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "60"))

    def ensure_dirs(self) -> None:
        for path in [
            self.DATA_DIR, self.RESUME_DIR, self.TRANSCRIPT_DIR,
            self.REPORT_DIR, self.EMBEDDING_DIR, self.DATABASE_DIR,
            BASE_DIR / "logs",
        ]:
            path.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_dirs()
