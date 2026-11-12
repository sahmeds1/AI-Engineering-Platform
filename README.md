# Agentic AI Chatbot

## Project Overview

An enterprise-oriented Agentic AI Chatbot
built using Python and modern AI frameworks.

## Business Objectives

- Build conversational AI agents.
- Implement LangGraph orchestration.
- Integrate external tools using MCP.
- Implement Retrieval-Augmented Generation.
- Add AI security and guardrails.
- Deploy using Docker.

## Technology Stack

- Python 3.12
- FastAPI
- LangGraph
- LangChain
- OpenAI / Amazon Bedrock
- MCP
- PostgreSQL
- Docker

## Planned Modules

1. Project Setup
2. Python Architecture
3. FastAPI Development
4. LLM Integration
5. LangGraph
6. MCP Integration
7. RAG Integration
8. AI Security
9. Testing
10. Docker Deployment

## Project Type

Independent AI Engineering Portfolio Project.





## Development Setup

### Requirements

- Python 3.12+
- Git
- VS Code

### Create virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Configure environment

```powershell
Copy-Item .env.example .env
```

### Run application

```powershell
uvicorn app.main:app --reload
```

### Run tests

```powershell
python -m pytest -v
```

### API documentation

http://127.0.0.1:8000/docs

### Health endpoint

http://127.0.0.1:8000/health
