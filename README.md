# Multi-Agent Architecture Intelligence System

A simple Software Engineering semester project that uses multiple AI agents to
turn a project idea into an initial software architecture report.

## Description

The user enters a software project idea, such as:

```text
Build an Online Food Delivery System
```

The system sends the idea through sequential agents. Each agent generates one
part of the final report, and the browser UI displays the output agent by
agent. The final report can also be downloaded as a PDF.

## Features

- FastAPI backend with protected API endpoints
- Simple HTML, CSS, and JavaScript frontend served by FastAPI
- LangGraph sequential multi-agent workflow
- Groq API for AI-generated responses
- Agent-by-agent report display
- Clarification and assumptions agent
- Architecture debate and recommendation
- Risk, testing, diagram, effort, use case, and roadmap generation
- Reviewer feedback loop
- Requirements traceability matrix
- Dedicated testing agent with unit, integration, acceptance, and edge-case tests
- Mermaid architecture and ER diagrams rendered in the browser
- Section-specific AI follow-up and regeneration
- Optional rubric or notes upload
- Editable report sections before export
- Full report view
- PDF report download
- Markdown report download
- Copy report button
- Project type and report depth options
- JSON history storage
- Simple username/password accounts with private report history
- Render deployment configuration

## Agent Workflow

```text
Clarification Agent
      ↓
Requirement Agent
      ↓
Project Planner Agent
      ↓
Architecture Debate Agent
      ↓
Database Agent
      ↓
Novelty Analysis Agent
      ↓
Traceability Agent
      ↓
Testing Agent
      ↓
Reviewer Agent
      ↓
Feedback Loop Agent
      ↓
Final Report
```

## Agent Responsibilities

| Agent | Output |
| --- | --- |
| Requirement Agent | Functional requirements, non-functional requirements, user stories |
| Project Planner Agent | WBS, milestones, sprint plan |
| Architecture Agent | Architecture options, debate, components, tech stack |
| Database Agent | Tables, fields, relationships |
| Novelty Analysis Agent | Risks, testing, diagrams, effort, use cases, roadmap |
| Traceability Agent | Requirement-to-component, database, and test mappings |
| Testing Agent | Unit, integration, acceptance, and edge-case test plan |
| Reviewer Agent | Completeness score, suggestions, final summary |
| Feedback Loop Agent | Agent-wise improvement suggestions for the next version |

## Tech Stack

- Python
- FastAPI
- HTML, CSS, JavaScript
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
    traceability.py
    testing.py
    refine.py
    reviewer.py

workflow.py
prompts.py
main.py
utils.py
static/
    index.html
    style.css
    app.js
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
SESSION_SECRET=a_long_random_value_for_sessions
```

You can copy `.env.example` as the starting point. The first person who uses a
new username and password should choose **Create account**. Future visits use
**Sign in**. Account and history data are saved locally in ignored JSON files.

## Run the App

```bash
uvicorn main:app --reload
```

The app will run at:

```text
http://127.0.0.1:8000
```

Open this URL in your browser. No separate Streamlit command is needed.

## API Example

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "project":"Build an Online Food Delivery System",
  "project_type":"Web App",
    "depth":"Short",
    "context":"Optional rubric or project notes"
  }'
```

The API returns separate fields for each agent:

```json
{
  "clarification": "...",
  "requirements": "...",
  "plan": "...",
  "architecture": "...",
  "database": "...",
  "novelty": "...",
  "traceability": "...",
  "testing": "...",
  "review": "...",
  "feedback": "...",
  "report": "..."
}
```

## Novelty

The novelty of this project is the use of a role-based multi-agent workflow for
early software engineering planning. Instead of one chatbot response, the system
simulates a small software team with specialized agents for clarification,
requirements, planning, architecture debate, database design, novelty analysis,
review, and feedback.

## History Format

Each generated report is saved in `history.json` and linked to its username:

```json
[
  {
    "username": "student_name",
    "project": "Online Food Delivery",
    "report": "..."
  }
]
```

## Phase 2 Scope

This version remains intentionally simple: the workflow is sequential and
history uses local JSON files. For a production deployment, use a real database
for users and history.

## Deploy on Render

1. Push the project to GitHub.
2. In Render, create a **New Blueprint Instance** and select the repository.
3. Add `GROQ_API_KEY` in Render's environment-variable screen.
4. Deploy. The included `render.yaml` starts FastAPI with the correct port.

The hosted app is suitable for a demo. Render's local file storage is not a
reliable long-term database, so accounts and history should move to PostgreSQL
or SQLite-backed persistent storage in a later phase.
