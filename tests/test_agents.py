"""
tests/test_agents.py  — Ollama edition
Unit tests for agents (pure logic, no LLM calls).
"""
import pytest
import json


def test_resume_agent_parse_json():
    from agents.resume_agent import ResumeAgent
    agent = ResumeAgent.__new__(ResumeAgent)
    raw = json.dumps({"name": "Jane Doe", "skills": ["Python"], "years_of_experience": 3})
    result = agent._parse_json(raw)
    assert result["name"] == "Jane Doe"


def test_resume_agent_parse_json_strips_fences():
    from agents.resume_agent import ResumeAgent
    agent = ResumeAgent.__new__(ResumeAgent)
    raw = "```json\n{\"name\": \"John\"}\n```"
    result = agent._parse_json(raw)
    assert result["name"] == "John"


def test_resume_agent_parse_json_extracts_embedded():
    from agents.resume_agent import ResumeAgent
    agent = ResumeAgent.__new__(ResumeAgent)
    raw = "Sure! Here is the JSON: {\"name\": \"Alice\"} Let me know!"
    result = agent._parse_json(raw)
    assert result["name"] == "Alice"


def test_question_agent_parse_questions():
    from agents.question_agent import QuestionAgent, QuestionCategory
    agent = QuestionAgent.__new__(QuestionAgent)
    raw = json.dumps([{
        "text": "Explain the CAP theorem.",
        "category": "technical",
        "difficulty": "senior",
        "follow_ups": ["What are the tradeoffs?"],
        "expected_topics": ["consistency", "availability"],
        "time_limit_seconds": 180,
    }])
    questions = agent._parse_questions(raw, QuestionCategory.TECHNICAL)
    assert len(questions) == 1
    assert questions[0].text == "Explain the CAP theorem."


def test_scoring_service_parse_json():
    from services.scoring_service import ScoringService
    svc = ScoringService.__new__(ScoringService)
    raw = "Here is the result: {\"overall_score\": 7.5} done."
    result = svc._parse_json(raw)
    assert result["overall_score"] == 7.5


def test_score_to_band():
    from utils.helpers import score_to_band
    assert score_to_band(92)[0] == "Outstanding"
    assert score_to_band(30)[0] == "Needs Work"


def test_chunk_text_overlap():
    from utils.file_parser import chunk_text
    text = " ".join([f"word{i}" for i in range(1000)])
    chunks = chunk_text(text, chunk_size=100, overlap=10)
    assert len(chunks) > 1
    last_words = set(chunks[0].split()[-10:])
    first_words = set(chunks[1].split()[:10])
    assert len(last_words & first_words) > 0


def test_ollama_embedding_function_import():
    from services.vector_db_service import OllamaEmbeddingFunction
    ef = OllamaEmbeddingFunction.__new__(OllamaEmbeddingFunction)
    assert ef is not None
