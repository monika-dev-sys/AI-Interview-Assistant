# 🎯 AI Interview Assistant

AI Interview Assistant is a locally hosted interview preparation application built using **Python**, **Streamlit**, and **Ollama**. It helps users prepare for technical interviews by analyzing resumes, conducting mock interviews, evaluating coding solutions, and providing detailed feedback—all while keeping data on the local machine.

The application uses **Llama 3.1** for language understanding and **nomic-embed-text** for embeddings, making it possible to run the complete interview workflow without relying on external AI services.

---

## Features

| Module               | Description                                                                                               |
| -------------------- | --------------------------------------------------------------------------------------------------------- |
| 📄 Resume Analysis   | Upload PDF or DOCX resumes to extract skills, education, projects, and experience with job-match scoring. |
| 🗣️ Mock Interview   | Practice technical and behavioral interviews with AI-generated questions and follow-up prompts.           |
| 💻 Coding Interview  | Solve coding problems with hints, code evaluation, and feedback.                                          |
| 📊 Feedback Report   | Receive an overall score along with strengths, improvement areas, and personalized recommendations.       |
| 📜 Interview History | Review previous interview sessions and feedback reports.                                                  |

---

## Prerequisites

Before running the application, make sure the following software is installed.

### Install Ollama

**Windows**

Download and install Ollama from:

https://ollama.com/download

**macOS / Linux**

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

---

## Download Required Models

```bash
ollama pull llama3.1:70b
ollama pull nomic-embed-text
```

If your system has limited memory, you can use the smaller model instead:

```bash
ollama pull llama3.1:8b
```

---

## Start the Ollama Server

```bash
ollama serve
```

The default server runs on:

```text
http://localhost:11434
```

---

## Installation

Clone the repository.

```bash
git clone https://github.com/monika-dev-sys/AI-Interview-Assistant.git

cd AI-Interview-Assistant
```

Create and activate a virtual environment.

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

Install the required dependencies.

```bash
pip install -r requirements.txt
```

---

## Configuration

Create a configuration file inside the `config` folder.

```text
config/.env
```

Example configuration:

```env
OLLAMA_BASE_URL=http://localhost:11434

OLLAMA_MODEL=llama3.1:70b

OLLAMA_EMBED_MODEL=nomic-embed-text

OLLAMA_TIMEOUT=300

OLLAMA_NUM_CTX=8192
```

To use a smaller model:

```env
OLLAMA_MODEL=llama3.1:8b
```

---

## Run the Application

```bash
streamlit run app.py
```

After the application starts, open the local URL displayed in the terminal.

---

## Project Structure

```text
AI-Interview-Assistant
│
├── agents/
├── config/
├── data/
├── database/
├── logs/
├── models/
├── pages/
├── prompts/
├── services/
├── tests/
├── utils/
│
├── app.py
├── requirements.txt
└── README.md
```

---

## System Requirements

| Component        | Recommended                                 |
| ---------------- | ------------------------------------------- |
| Python           | 3.11 or later                               |
| RAM              | 16 GB (32 GB recommended for larger models) |
| Storage          | At least 20 GB                              |
| Operating System | Windows, Linux, or macOS                    |

For better performance, use a GPU if available. Otherwise, the application can also run entirely on the CPU, although larger language models will respond more slowly.

---

## Architecture

```text
                Streamlit Application
                        │
                        ▼
              Interview Orchestrator
                        │
        ┌───────────────┼────────────────┐
        ▼               ▼                ▼
 Resume Agent    Interview Agent   Coding Agent
        │               │                │
        └───────────────┼────────────────┘
                        ▼
                 Feedback Generator
                        │
        ┌───────────────┴────────────────┐
        ▼                                ▼
     SQLite Database              ChromaDB
                        │
                        ▼
                 Ollama Server
         (Llama 3.1 + nomic-embed-text)
```

---

## Running Tests

```bash
pytest tests -v
```

---

## Future Improvements

* Voice-based mock interviews
* Company-specific interview preparation
* Resume ATS compatibility analysis
* Multi-language interview support
* Dashboard for tracking interview performance
* Exportable interview reports

---



Jawaharlal Nehru National College of Engineering, Shivamogga
