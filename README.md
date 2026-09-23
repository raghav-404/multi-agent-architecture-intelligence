# MARIS: Multi-Agent Architecture Intelligence System

MARIS is a Software Engineering semester project that turns a software idea
into an evaluated, traceable, and reviewable architecture report.

It is not only a multi-agent chatbot. Groq agents generate and critique design
artifacts, while deterministic Python rules score architectures, find supported
conflicts, validate artifact references, calculate coverage, and analyze change
impact.

## Main Features

- Structured functional requirements, NFRs, user stories, and stable IDs
- Two architecture alternatives for Short reports and three for other depths
- Deterministic architecture scoring with weights, evidence, and selection
- Rule-based requirement conflict detection
- Structured database designs and test cases
- Cross-agent architecture, database, requirement, API, and test validation
- Requirement-to-story/component/entity/API/test/risk traceability graph
- Adversarial red-team architecture review
- Bounded architecture refinement loop with V1/V2 comparison
- Architecture Decision Records (ADRs)
- Traceability-based change-impact analysis
- Rule-based failure and growth scenario analysis
- React workspace with section editing, Mermaid diagrams, PDF, and Markdown export
- Authentication and per-user JSON report history

## Design Principle

```text
Groq agents
  Generation, explanation, critique, and refinement

Python rule engine
  Scoring, validation, conflict rules, traceability,
  coverage, impact traversal, and scenario rules
```

This split makes the system easier to explain, test, and reproduce than a
workflow in which every decision is delegated to an LLM.

## Workflow

```text
Project Idea
    |
    v
Clarification Agent
    |
Requirements Agent --> Requirement Conflict Detector
    |
Planner Agent
    |
Competing Architecture Agent (2-3 options)
    |
Deterministic Evaluation and Selection
    |
Database Agent --> Testing Agent --> Traceability Engine
    |
Red Team Agent --> Consistency Validator --> Reviewer
    |                                      |
    | fail                                 | pass
    v                                      v
Architecture Refinement -----------> ADRs and Final Report
    |
    +---- Re-evaluate (maximum 1-2 refinements)
```

Change impact and scenarios run after a report has been saved:

```text
Change Request --> Requirement Match --> Traceability Traversal --> Impact
Scenario Choice --> Deterministic Failure Rules --> Risks and Mitigations
```

## Architecture Evaluation

Each alternative receives a score from 0 to 10 for:

- Requirement fit
- Scalability
- Security
- Performance
- Maintainability
- Cost
- Complexity, where a higher score means simpler operation
- Availability

Requirement fit is calculated from referenced requirement IDs. Other scores
start from documented architecture-style baselines, receive NFR-derived
weights, and can be adjusted by explicit quality tactics. The highest weighted
score wins; simplicity is the tie-breaker.

## Project Structure

```text
agents/                    Groq-backed generation and review functions
    architect.py
    clarification.py
    database.py
    feedback.py
    novelty.py
    planner.py
    red_team.py
    refine.py
    requirement.py
    reviewer.py
    testing.py

models.py                  Pydantic artifact schemas
engine.py                  Deterministic intelligence rules
workflow.py                LangGraph workflow and bounded loop
prompts.py                 Agent instructions
main.py                    FastAPI routes
utils.py                   Groq, JSON storage, authentication, and PDF helpers

frontend/                  React/Vite source
static/                    Generated production frontend
tests/                     Rule, workflow, storage, and API tests
```

## Setup

```bash
cd multi-agent-architecture-intelligence
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm install
cp .env.example .env
```

Add your Groq API key to `.env`:

```text
GROQ_API_KEY=your_real_key
SESSION_SECRET=replace_with_a_long_random_value
```

MARIS uses `openai/gpt-oss-20b` for schema-constrained Groq responses by
default. Both Groq models can be changed through environment variables. When
the free-tier token window fills, MARIS follows Groq's cooldown and retries the
request once automatically.

## Run

Build the React frontend and start FastAPI:

```bash
npm run build
uvicorn main:app --reload
```

Open `http://127.0.0.1:8000`.

For frontend development, keep FastAPI on port 8000 and run this in a second
terminal:

```bash
npm run dev
```

Then open `http://127.0.0.1:5173`.

## Test

The automated tests do not spend Groq quota because all agents are mocked:

```bash
python -m unittest discover -s tests -v
npm run build
```

The tests cover evaluation, conflicts, consistency, traceability, impact,
scenarios, ADRs, bounded refinement, JSON storage, authentication, and API
integration.

## API

All analysis endpoints require an authenticated session.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | `/register` | Create a local account |
| POST | `/login` | Start a session |
| POST | `/analyze` | Run the complete architecture workflow |
| POST | `/refine` | Revise one report section |
| POST | `/impact` | Analyze a change using saved traceability |
| POST | `/scenario` | Run a predefined architecture scenario |
| GET | `/history` | Load the user's reports |
| POST | `/pdf` | Generate a PDF report |

## Storage

Local accounts and reports are stored in ignored JSON files. New history
records contain the complete structured analysis; older markdown-only records
remain readable but cannot run impact or scenario analysis.

Vercel uses a temporary filesystem, so hosted JSON data may reset. That is
acceptable for a semester demonstration. A persistent database is the logical
next production upgrade.

## Academic Novelty

The novelty is the combination of specialized LLM roles with deterministic
software-engineering analysis. MARIS generates competing architectures,
produces auditable selection evidence, detects cross-artifact contradictions,
maintains a traversable traceability model, attacks the selected architecture,
and measures refinement across versions.

The system deliberately does not generate full applications, predict real
performance, deploy infrastructure, or require a graph database.

## Deployment

The included `vercel.json` builds React and deploys FastAPI. Add these Vercel
environment variables before deploying:

```text
GROQ_API_KEY
SESSION_SECRET
COOKIE_SECURE=true
```

Push the repository to GitHub, import it into Vercel, and deploy with the
included configuration.
