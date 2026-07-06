"""
utils/helpers.py
Miscellaneous helper functions used across the project.
"""
from __future__ import annotations
import uuid
import re
from datetime import datetime
from utils.constants import SCORE_BANDS


def generate_id() -> str:
    return str(uuid.uuid4())


def score_to_band(score: float) -> tuple[str, str]:
    """Return (label, hex_color) for a 0-100 score."""
    for (low, high), (label, color) in SCORE_BANDS.items():
        if low <= score <= high:
            return label, color
    return "N/A", "#6b7280"


def format_duration(seconds: int) -> str:
    """Convert seconds to mm:ss string."""
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def sanitize_filename(name: str) -> str:
    """Strip special characters for safe file names."""
    return re.sub(r"[^\w\-_.]", "_", name)


def truncate(text: str, max_chars: int = 200) -> str:
    return text[:max_chars] + "…" if len(text) > max_chars else text


def utcnow_iso() -> str:
    return datetime.utcnow().isoformat()
