# Multi-Agent Architecture Intelligence System

A simple Software Engineering semester project that uses multiple AI agents to
turn a project idea into an initial software architecture report.

## Description

The user enters a software project idea, such as:

```text
Build an Online Food Delivery System
```

The system sends the idea through five sequential agents. Each agent generates
one part of the final report, and the Streamlit interface displays the output
agent by agent. The final report can also be downloaded as a PDF.

## Features

- FastAPI backend with one `/analyze` endpoint
- Streamlit frontend with a simple input form
- LangGraph sequential multi-agent workflow
- Groq API for AI-generated responses
- Agent-by-agent report display
- Full report view
- PDF report download
- JSON history storage

## Agent Workflow

```text
Requirement Agent
      ↓
Project Planner Agent
      ↓
Architecture Agent
      ↓
Database Agent
      ↓
Reviewer Agent
      ↓
Final Report
```

## Agent Responsibilities

| Agent | Output |
| --- | --- |
| Requirement Agent | Functional requirements, non-functional requirements, user stories |
| Project Planner Agent | WBS, milestones, sprint plan |
| Architecture Agent | Suggested architecture, components, tech stack |
| Database Agent | Tables, fields, relationships |
| Reviewer Agent | Completeness score, suggestions, final summary |

## Tech Stack

- Python
- FastAPI
- Streamlit
- LangGraph
- Groq API
- Pydantic
- ReportLab

## Project Structure

```text
agents/
    requirement.py
    planner.py
    architect.py
    database.py
    reviewer.py

workflow.py
prompts.py
frontend.py
main.py
utils.py
history.json
requirements.txt
.env
README.md
```

## Setup

```bash
cd multi-agent-architecture-intelligence
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Edit `.env` and add your Groq API key:

```text
GROQ_API_KEY=your_real_key_here
```

## Run the Backend

```bash
uvicorn main:app --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

## Run the Frontend

Open a second terminal:

```bash
cd multi-agent-architecture-intelligence
source .venv/bin/activate
streamlit run frontend.py
```

Then open the Streamlit URL shown in the terminal.

## API Example

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"project":"Build an Online Food Delivery System"}'
```

## History Format

Each generated report is saved in `history.json`:

```json
[
  {
    "project": "Online Food Delivery",
    "report": "..."
  }
]
```

## Phase 1 Scope

This phase focuses on a simple working prototype. The workflow is sequential,
with no branching, memory, authentication, database server, or complex UI.
