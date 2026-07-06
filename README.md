# 🎯 AI Interview Assistant — Ollama Edition

A fully **local**, **private** AI-powered interview preparation platform built with
**Streamlit** + **Ollama** (`llama3.1:70b` + `nomic-embed-text`).

> 🔒 **No API keys. No cloud. No data leaves your machine.**

## Features

| Page | Feature |
|---|---|
| 📄 Resume Analysis | Upload PDF/DOCX → extract skills, experience, education; job-match scoring |
| 🗣️ Mock Interview | AI-generated technical & behavioural questions with timer and follow-ups |
| 💻 Coding Interview | Problems with progressive hints, simulated test runs, and code review |
| 📊 Feedback Report | Scored report with per-question breakdown, strengths, gaps, and study plan |
| 📜 Interview History | Browse past sessions and revisit feedback |

## Prerequisites

### 1. Install Ollama
```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows: download from https://ollama.com/download
```

### 2. Pull required models
```bash
# LLM (large — ~40GB, use llama3.1:8b to start if disk is limited)
ollama pull llama3.1:70b

# Embedding model (~270MB)
ollama pull nomic-embed-text
```

### 3. Start Ollama server
```bash
ollama serve
# Runs at http://localhost:11434 by default
```

## Quick Start

```bash
# 1. Clone and enter
git clone <repo>
cd ai-interview-assistant-ollama

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure
cp config/.env.example config/.env
# Edit config/.env if needed (defaults work for standard Ollama setup)

# 5. Run
streamlit run app.py
```

## Configuration

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.1:70b` | LLM model for all completions |
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text` | Embedding model for vector search |
| `OLLAMA_TIMEOUT` | `300` | Request timeout in seconds |
| `OLLAMA_NUM_CTX` | `8192` | Context window size |

### Using a smaller model (faster, less RAM)
```bash
# In config/.env
OLLAMA_MODEL=llama3.1:8b
```

### Remote Ollama server
```bash
OLLAMA_BASE_URL=http://192.168.1.100:11434
```

## System Requirements

| Model | RAM | VRAM (GPU) |
|---|---|---|
| llama3.1:8b | 8 GB | 6 GB |
| llama3.1:70b | 64 GB | 48 GB |
| nomic-embed-text | 1 GB | — |

> llama3.1:70b can run on CPU with 64 GB RAM (slower inference ~1–3 tok/s).
> For faster results, use a GPU or switch to llama3.1:8b.

## Architecture

```
Streamlit pages  →  Orchestrator Agent  →  Specialist Agents
                                         ├─ ResumeAgent
                                         ├─ QuestionAgent
                                         ├─ BehavioralAgent
                                         ├─ CodingAgent
                                         ├─ EvaluationAgent
                                         └─ FeedbackAgent
                        ↓                       ↓
                   SQLite DB          ChromaDB + nomic-embed-text
                                       (via Ollama, fully local)
                        ↑
                   Ollama Server
                   llama3.1:70b
```

## Running Tests

```bash
pytest tests/ -v
```
