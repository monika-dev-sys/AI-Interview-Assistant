"""
services/llm_service.py  — Ollama edition
Wraps the Ollama Python client for chat completions and streaming.
Model: llama3.1:70b  |  Context: 8192 tokens
"""
from __future__ import annotations
import time
from typing import Generator
from tenacity import retry, stop_after_attempt, wait_exponential
import ollama
from config.settings import settings
from utils.logger import logger


class LLMService:
    """Singleton-style service for all Ollama LLM calls."""

    def __init__(self) -> None:
        self.model = settings.OLLAMA_MODEL
        self.base_url = settings.OLLAMA_BASE_URL
        self.timeout = settings.OLLAMA_TIMEOUT
        self.temperature = settings.OLLAMA_TEMPERATURE
        self.num_ctx = settings.OLLAMA_NUM_CTX

        # Initialise client pointing at local Ollama server
        self.client = ollama.Client(
            host=self.base_url,
            timeout=self.timeout,
        )
        self._verify_connection()

    def _verify_connection(self) -> None:
        """Check Ollama is running and the model is available."""
        try:
            models = self.client.list()
            available = [m["name"] for m in models.get("models", [])]
            if not any(self.model in m for m in available):
                logger.warning(
                    f"Model '{self.model}' not found locally. "
                    f"Run: ollama pull {self.model}"
                )
            else:
                logger.info(f"Ollama ready — model: {self.model}")
        except Exception as e:
            logger.error(
                f"Cannot connect to Ollama at {self.base_url}. "
                f"Make sure Ollama is running. Error: {e}"
            )

    # ── Core completion ───────────────────────────────────────────────────────

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=15),
        reraise=True,
    )
    def complete(
        self,
        prompt: str,
        system: str = "",
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Single-turn completion. Returns assistant text."""
        t0 = time.perf_counter()

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat(
            model=self.model,
            messages=messages,
            options={
                "temperature": temperature or self.temperature,
                "num_ctx": self.num_ctx,
                **({"num_predict": max_tokens} if max_tokens else {}),
            },
        )

        text = response["message"]["content"]
        elapsed = time.perf_counter() - t0
        logger.debug(f"LLM complete | {elapsed:.2f}s | model={self.model}")
        return text

    def chat(
        self,
        messages: list[dict],
        system: str = "",
        max_tokens: int | None = None,
    ) -> str:
        """Multi-turn chat. `messages` is a list of {role, content} dicts."""
        full_messages = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)

        response = self.client.chat(
            model=self.model,
            messages=full_messages,
            options={
                "temperature": self.temperature,
                "num_ctx": self.num_ctx,
                **({"num_predict": max_tokens} if max_tokens else {}),
            },
        )
        return response["message"]["content"]

    def stream(
        self,
        prompt: str,
        system: str = "",
    ) -> Generator[str, None, None]:
        """Streaming completion — yields text chunks as they arrive."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        stream = self.client.chat(
            model=self.model,
            messages=messages,
            stream=True,
            options={
                "temperature": self.temperature,
                "num_ctx": self.num_ctx,
            },
        )
        for chunk in stream:
            content = chunk.get("message", {}).get("content", "")
            if content:
                yield content

    # ── Utility ───────────────────────────────────────────────────────────────

    def load_prompt(self, filename: str, **kwargs) -> str:
        """Load a prompt template from prompts/ and interpolate kwargs."""
        path = settings.PROMPT_DIR / filename
        template = path.read_text(encoding="utf-8")
        return template.format(**kwargs) if kwargs else template

    def list_local_models(self) -> list[str]:
        """Return names of all locally available Ollama models."""
        try:
            models = self.client.list()
            return [m["name"] for m in models.get("models", [])]
        except Exception:
            return []

    def pull_model(self, model_name: str | None = None) -> bool:
        """Pull a model from Ollama registry. Returns True on success."""
        target = model_name or self.model
        try:
            logger.info(f"Pulling Ollama model: {target} …")
            self.client.pull(target)
            logger.info(f"Model {target} pulled successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to pull {target}: {e}")
            return False


# Module-level singleton
llm_service = LLMService()
