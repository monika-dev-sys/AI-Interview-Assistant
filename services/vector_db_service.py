"""
services/vector_db_service.py  — Ollama edition
ChromaDB with nomic-embed-text embeddings via Ollama.
Replaces SentenceTransformers with a fully local embedding model.
"""
from __future__ import annotations
import uuid
from typing import Optional
import chromadb
from chromadb import EmbeddingFunction, Documents, Embeddings
import ollama
from config.settings import settings
from utils.logger import logger


class OllamaEmbeddingFunction(EmbeddingFunction):
    """ChromaDB-compatible embedding function backed by Ollama."""

    def __init__(self, model: str = "nomic-embed-text", host: str = "http://localhost:11434") -> None:
        self.model = model
        self.client = ollama.Client(host=host)

    def __call__(self, input: Documents) -> Embeddings:
        embeddings: Embeddings = []
        for text in input:
            try:
                resp = self.client.embeddings(model=self.model, prompt=text)
                embeddings.append(resp["embedding"])
            except Exception as e:
                logger.error(f"Ollama embedding error: {e}")
                # Return zero vector of typical nomic-embed-text size (768)
                embeddings.append([0.0] * 768)
        return embeddings


class VectorDBService:
    """Manages ChromaDB collections using Ollama nomic-embed-text embeddings."""

    COLLECTIONS = {
        "resumes": "resume_chunks",
        "questions": "question_bank",
        "answers": "answer_history",
    }

    def __init__(self) -> None:
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        self.ef = OllamaEmbeddingFunction(
            model=settings.OLLAMA_EMBED_MODEL,
            host=settings.OLLAMA_BASE_URL,
        )
        self._init_collections()

    def _init_collections(self) -> None:
        for name, collection_name in self.COLLECTIONS.items():
            setattr(
                self,
                f"_{name}_collection",
                self.client.get_or_create_collection(
                    name=collection_name,
                    embedding_function=self.ef,
                    metadata={"hnsw:space": "cosine"},
                ),
            )

    # ── Resume ────────────────────────────────────────────────────────────────

    def upsert_resume_chunks(self, candidate_id: str, chunks: list[str]) -> None:
        col = self._resumes_collection
        ids = [f"{candidate_id}_{i}" for i in range(len(chunks))]
        metadatas = [{"candidate_id": candidate_id, "chunk_index": i} for i in range(len(chunks))]
        col.upsert(ids=ids, documents=chunks, metadatas=metadatas)
        logger.info(f"Upserted {len(chunks)} resume chunks for candidate {candidate_id}")

    def search_resume(self, candidate_id: str, query: str, n: int = 5) -> list[str]:
        col = self._resumes_collection
        results = col.query(
            query_texts=[query],
            n_results=n,
            where={"candidate_id": candidate_id},
        )
        return results["documents"][0] if results["documents"] else []

    # ── Question bank ─────────────────────────────────────────────────────────

    def add_questions(self, questions: list[dict]) -> None:
        col = self._questions_collection
        ids = [q.get("id", str(uuid.uuid4())) for q in questions]
        docs = [q["text"] for q in questions]
        metas = [{k: v for k, v in q.items() if k != "text"} for q in questions]
        col.upsert(ids=ids, documents=docs, metadatas=metas)

    def search_questions(self, query: str, category: Optional[str] = None, n: int = 10) -> list[dict]:
        col = self._questions_collection
        where = {"category": category} if category else None
        results = col.query(query_texts=[query], n_results=n, where=where)
        docs = results["documents"][0] if results["documents"] else []
        metas = results["metadatas"][0] if results["metadatas"] else []
        return [{"text": d, **m} for d, m in zip(docs, metas)]

    # ── Answer history ────────────────────────────────────────────────────────

    def store_answer(self, session_id: str, question_id: str, answer_text: str) -> None:
        col = self._answers_collection
        doc_id = f"{session_id}_{question_id}"
        col.upsert(
            ids=[doc_id],
            documents=[answer_text],
            metadatas=[{"session_id": session_id, "question_id": question_id}],
        )

    def get_similar_answers(self, query: str, n: int = 5) -> list[str]:
        col = self._answers_collection
        results = col.query(query_texts=[query], n_results=n)
        return results["documents"][0] if results["documents"] else []


vector_db_service = VectorDBService()
