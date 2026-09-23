# MARIS

## Multi-Agent Architecture Intelligence System

MARIS is a Software Engineering semester project that converts a software idea
into a structured, evaluated, and traceable architecture report.

Example input:

```text
Build an online food delivery system for customers, restaurants, and delivery partners.
```

MARIS generates requirements, compares architecture alternatives, designs the
database, creates tests, checks consistency, maps traceability, identifies
risks, records architecture decisions, and produces a downloadable report.

## The Problem

Early software planning usually requires several activities:

- Understanding an incomplete project idea
- Writing functional and non-functional requirements
- Selecting an architecture
- Designing the database and APIs
- Planning tests
- Checking whether all artifacts agree with each other
- Explaining why one architecture was selected

A single chatbot response can generate these sections, but it may be difficult
to verify, compare, or trace. MARIS treats architecture planning as a workflow
of specialized roles supported by deterministic Software Engineering rules.

## Project Objective

The objective is to help students and small teams create an initial software
architecture report that is structured, explainable, traceable, consistent,
reviewable, and easy to export and present.

MARIS is a decision-support system. It does not replace an experienced
architect, generate a complete application, or predict real production
performance.

## Academic Novelty

The novelty is the hybrid use of generative AI and deterministic architecture
intelligence.

Groq generates the creative core artifacts. Python rules then evaluate those
artifacts using explicit evidence instead of asking another model to make every
decision. This produces a more reproducible and auditable result.

The main novel elements are:

1. Competing architecture analysis instead of one unchallenged recommendation
2. Requirement-derived evaluation weights and visible scoring evidence
3. Stable IDs linking requirements, components, APIs, entities, risks, and tests
4. Cross-artifact consistency validation
5. Rule-supported requirement conflict detection
6. Architecture red-team analysis
7. Traceability-based change-impact analysis
8. Deterministic growth and failure scenario analysis
9. Automatically generated Architecture Decision Records
10. A hybrid AI and rule-engine design optimized for a free API tier

## Free-Tier Design

The default workflow makes only three Groq requests:

1. Requirement generation
2. Primary architecture generation
3. Database design

The second architecture option, planning, testing, red-team review, scoring,
traceability, consistency checks, ADRs, novelty analysis, and final review are
generated locally with Python.

This reduced the original workflow from approximately 18 model calls to three.
It lowers latency, reduces rate-limit failures, and makes the analytical parts
of the report repeatable.

Groq schema responses use low reasoning effort and limited completion budgets.
If a temporary rate limit still occurs, MARIS reads Groq's cooldown header,
waits, and retries once.

Automatic architecture refinement is disabled by default because it repeats
several generation steps. It can be enabled with:

```env
ENABLE_AUTO_REFINEMENT=true
```

Keep it `false` when using the Groq free tier.

## System Workflow

```text
Project Idea
    |
    v
Clarification Role (Python)
    |
    v
Requirement Agent (Groq + Pydantic)
    |
    v
Requirement Conflict Detector (Python rules)
    |
    v
Project Planner (Python)
    |
    v
Primary Architecture Agent (Groq + Pydantic)
    |
    +--> Serverless Alternative Generator (Python)
    |
    v
Architecture Evaluation and Selection (Python)
    |
    v
Database Agent (Groq + Pydantic)
    |
    v
Test Generator and Traceability Engine (Python)
    |
    v
Red Team and Consistency Validator (Python)
    |
    v
ADRs, Novelty Analysis, Review, and Final Report
```

LangGraph controls this sequence and stores the shared workflow state.

## Feature Guide

### 1. Clarification Role

- Interprets the input as a semester-project MVP
- Establishes baseline assumptions
- Identifies concerns such as authentication, validation, logging, and errors
- Reminds the user that inferred requirements require stakeholder confirmation

This role is deterministic and does not consume Groq quota.

### 2. Requirement Agent

- Generates functional requirements
- Generates non-functional requirements
- Assigns priorities such as must, should, and could
- Creates user stories
- Records assumptions
- Assigns stable IDs such as `FR-01`, `NFR-01`, and `US-01`

The result is validated through a Pydantic schema before later stages use it.

### 3. Requirement Conflict Detector

- Detects only conflicts supported by explicit requirement text
- Checks trade-offs such as low cost versus high availability
- Checks security versus very low latency
- Checks privacy versus broad analytics
- Suggests a resolution for each detected conflict

This avoids inventing conflicts when the required evidence is absent.

### 4. Project Planner

- Produces a simple Work Breakdown Structure
- Defines three project milestones
- Creates a three-sprint implementation plan
- References the approved requirement IDs

The planner is local and deterministic to save API calls.

### 5. Architecture Agent

- Generates the primary domain-specific architecture
- Defines components and their responsibilities
- Defines APIs and communication methods
- Recommends a technology stack and database
- Adds quality tactics, assumptions, advantages, disadvantages, and risks
- Links components and APIs to requirement IDs

The primary option normally favors a modular monolith for a small project.

### 6. Architecture Alternative Generator

- Derives a serverless alternative from the same domain responsibilities
- Changes communication to managed HTTPS and event-based interaction
- Adds automatic scaling tactics
- Records serverless advantages and trade-offs
- Preserves traceability IDs

This produces a useful comparison without another Groq request.

### 7. Architecture Evaluation Engine

Each architecture is scored from 0 to 10 for:

- Requirement fit
- Scalability
- Security
- Performance
- Maintainability
- Cost
- Complexity, where a higher score means easier operation
- Availability

Non-functional requirements adjust the criterion weights. Requirement fit is
calculated from explicit artifact references. The architecture with the highest
weighted score wins, with simplicity used as the tie-breaker.

### 8. Database Agent

- Selects a database engine compatible with the chosen architecture
- Generates entities, fields, data types, and constraints
- Defines entity relationships
- Links entities to requirement IDs
- Explains the database rationale and risks

The database output is also validated with Pydantic.

### 9. Test Generator

- Generates acceptance tests for functional requirements
- Generates edge-case tests for non-functional requirements
- Links every test to requirements, components, and APIs
- Calculates test coverage

Tests are derived from validated artifacts, so this stage needs no extra model
request.

### 10. Traceability Engine

- Builds nodes for requirements, stories, components, APIs, entities, tests, and risks
- Builds edges between related artifacts
- Calculates requirement coverage
- Identifies uncovered requirements
- Produces a Mermaid traceability diagram

The traceability graph is later reused for change-impact analysis.

### 11. Red-Team Review

- Converts documented architecture risks into review findings
- Assigns severity levels
- Identifies affected artifact IDs
- Recommends measurable mitigation and failure testing
- Removes references to nonexistent artifacts

This stage challenges the selected architecture instead of accepting it blindly.

### 12. Consistency Validator

- Detects architecture and database engine mismatches
- Finds invalid requirement references
- Finds APIs linked to missing components
- Finds relationships linked to missing entities
- Finds tests linked to missing components or APIs
- Reports missing test coverage for must-have requirements
- Produces a consistency score and pass, warning, or fail status

### 13. Architecture Decision Records

MARIS creates ADRs containing:

- Decision context
- Considered alternatives
- Selected decision
- Reason for the decision
- Trade-offs
- Decision status

ADRs explain why the system selected an architecture or database choice.

### 14. Version Comparison

- Records architecture snapshots
- Compares requirement fit, traceability, consistency, testing, and risks
- Shows changes between versions when automatic refinement is enabled

The default free-tier mode records one reviewed version.

### 15. Change-Impact Analysis

After a report is saved, the user can enter a proposed change. MARIS:

- Matches the change to requirements
- Traverses the traceability graph
- Lists affected components, APIs, entities, tests, and risks
- Assigns an impact level
- Suggests regression tests

### 16. Scenario Analysis

The user can evaluate predefined scenarios such as:

- 10x users
- 100x traffic
- Database failure
- API failure
- Authentication failure
- Payment failure
- Network latency
- Cloud-region failure

The result describes likely affected artifacts, risks, mitigations, and impact.
It is an architecture review, not a performance prediction.

### 17. React Workspace

- Responsive SaaS-style interface
- Project idea, project type, report depth, and context inputs
- Agent-by-agent report navigation
- Structured evaluation and version tables
- Mermaid diagrams
- Editable report sections
- Manual section refinement
- Copy report action
- Markdown download
- PDF download
- Saved report history
- Change-impact and scenario tools

### 18. Authentication and History

- Simple local account registration and login
- Passwords stored as salted PBKDF2 hashes
- Session-based authentication
- Reports stored per user
- Older markdown-only history records remain readable

This is suitable for a classroom demonstration, not production identity
management.

## Technology Stack

| Layer | Technology | Purpose |
| --- | --- | --- |
| Frontend | React 19 and Vite | Interactive website |
| UI icons | Lucide React | Familiar interface icons |
| Markdown | Marked and DOMPurify | Safe rendered reports |
| Diagrams | Mermaid | Architecture and traceability diagrams |
| Backend | FastAPI and Uvicorn | API and frontend hosting |
| Workflow | LangGraph | Sequential workflow orchestration |
| AI provider | Groq | Fast LLM inference |
| Validation | Pydantic | Structured and validated artifacts |
| PDF | ReportLab | Downloadable PDF reports |
| Storage | JSON files | Simple local history and accounts |

## Project Structure

```text
multi-agent-architecture-intelligence/
|
|-- agents/
|   |-- architect.py
|   |-- clarification.py
|   |-- database.py
|   |-- feedback.py
|   |-- novelty.py
|   |-- planner.py
|   |-- red_team.py
|   |-- refine.py
|   |-- requirement.py
|   |-- reviewer.py
|   `-- testing.py
|
|-- frontend/
|   |-- index.html
|   `-- src/
|       |-- App.jsx
|       `-- styles.css
|
|-- static/                 Generated production frontend
|-- tests/                  Automated unit and API tests
|-- engine.py               Deterministic analysis rules
|-- models.py               Pydantic schemas
|-- workflow.py             LangGraph workflow
|-- prompts.py              Groq instructions
|-- main.py                 FastAPI routes
|-- utils.py                Groq, storage, authentication, and PDF helpers
|-- requirements.txt
|-- package.json
|-- vercel.json
|-- .env.example
`-- README.md
```

## Installation

```bash
cd "/Users/shadow/Projects/Artificial Intelligence/MARIS/multi-agent-architecture-intelligence"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm install
cp .env.example .env
```

Add your Groq key to `.env`:

```env
GROQ_API_KEY=your_actual_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
GROQ_STRUCTURED_MODEL=openai/gpt-oss-20b
ENABLE_AUTO_REFINEMENT=false
SESSION_SECRET=replace_with_a_long_random_value
COOKIE_SECURE=false
```

Do not commit `.env` or expose the API key.

## Running the Project

Build the React frontend:

```bash
npm run build
```

Start FastAPI:

```bash
uvicorn main:app --reload
```

Open `http://127.0.0.1:8000`.

If port 8000 is occupied:

```bash
uvicorn main:app --reload --port 8010
```

### Frontend Development

Run FastAPI on port 8000. In a second terminal, run:

```bash
npm run dev
```

Open `http://127.0.0.1:5173`. Vite forwards API requests to FastAPI.

## How to Use MARIS

1. Create a local account or sign in.
2. Enter a clear software project idea.
3. Select the project type and report depth.
4. Add optional context such as constraints or rubric notes.
5. Select Generate Analysis.
6. Review each section from the report navigation.
7. Compare the architecture evaluation scores.
8. Inspect traceability, tests, risks, and consistency.
9. Run a change-impact or scenario analysis.
10. Download the final report as Markdown or PDF.

## API Endpoints

All report endpoints require an authenticated session.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/` | Serve the React application |
| GET | `/me` | Return the active user |
| POST | `/register` | Create a local account |
| POST | `/login` | Start a session |
| POST | `/logout` | End a session |
| POST | `/analyze` | Run the architecture workflow |
| POST | `/refine` | Revise one report section |
| GET | `/history` | Load the user's saved reports |
| POST | `/impact` | Analyze a proposed change |
| POST | `/scenario` | Run an architecture scenario |
| POST | `/pdf` | Create a PDF report |

## Testing

The automated suite mocks Groq and does not consume API quota:

```bash
python -m unittest discover -s tests -v
```

Build verification:

```bash
npm run build
```

The tests cover:

- Authentication and protected API endpoints
- Architecture scoring and selection
- Requirement conflict rules
- Cross-artifact consistency
- Stable architecture IDs
- Traceability and change-impact traversal
- Scenario analysis
- ADR generation
- JSON history storage
- Rate-limit retry behavior
- Deterministic testing and red-team output
- One-call generation of two architecture alternatives
- Complete mocked workflow execution

## Storage

Local development uses `users.json` and `history.json`. These files are ignored
by Git. New history entries contain the full structured analysis, while older
markdown-only entries remain readable.

## Deployment

The repository contains `vercel.json` for a FastAPI and React deployment.

Add these environment variables in Vercel:

```text
GROQ_API_KEY
SESSION_SECRET
COOKIE_SECURE=true
ENABLE_AUTO_REFINEMENT=false
```

Vercel's function filesystem is temporary. Accounts and history may reset after
a deployment or serverless restart. This is acceptable for a demonstration,
but a real deployment should use PostgreSQL, Supabase, Neon, or another
persistent database.

## Current Limitations

- Requirements are generated from a short idea and still need human approval.
- Architecture scores use documented heuristics, not benchmark measurements.
- JSON files are not suitable for concurrent production use.
- Local authentication is intentionally basic.
- Scenario analysis is qualitative, not load testing.
- The generated database and APIs are design suggestions, not deployed systems.
- Groq free-tier limits can still require a short cooldown after repeated runs.
- Automatic refinement is disabled in the default free-tier configuration.

## Suggested Future Work

### Phase 2

- Persistent PostgreSQL or Supabase storage
- Project workspaces and report sharing
- User-edited requirements before architecture generation
- Additional architecture patterns
- Export to DOCX and presentation slides
- Better progress streaming from the workflow

### Phase 3

- Repository and codebase analysis
- Architecture drift detection
- Real load-test integration
- Cost estimation using cloud pricing APIs
- Team collaboration and approval workflows
- Deployment diagram generation
- Historical architecture quality analytics

## Demonstration Plan

1. Explain the problem and hybrid novelty.
2. Enter `Build an online food delivery system`.
3. Generate the report.
4. Show the requirements and their stable IDs.
5. Compare the modular-monolith and serverless alternatives.
6. Show the evaluation table and selected architecture.
7. Open the database, testing, traceability, and consistency sections.
8. Run a change such as `Add scheduled food delivery`.
9. Run the database-failure scenario.
10. Download the final PDF.

## Presentation Speech

The following speech is approximately four to five minutes.

> Good morning, ma'am. My project is called MARIS, which stands for
> Multi-Agent Architecture Intelligence System.
>
> The problem I am addressing is that converting a simple software idea into a
> proper engineering plan requires many connected activities. We need to define
> requirements, compare architecture choices, design the database, plan tests,
> identify risks, and verify that every artifact is consistent. A normal chatbot
> can generate a long answer, but that answer is often difficult to verify or
> trace.
>
> MARIS solves this by using a structured workflow rather than one unrestricted
> prompt. The user enters a project idea, such as an online food delivery
> system. A Groq-powered Requirement Agent creates functional requirements,
> non-functional requirements, user stories, assumptions, priorities, and
> stable requirement IDs. Every AI-generated artifact is validated with
> Pydantic before it enters the rest of the workflow.
>
> The system then uses deterministic rules to detect supported requirement
> conflicts. For example, high availability may conflict with a strict low-cost
> requirement because redundancy requires additional infrastructure. MARIS only
> reports this conflict when both sides are actually present in the requirements.
>
> Next, the Architecture Agent generates a primary modular architecture with
> components, APIs, technology choices, quality tactics, and risks. MARIS also
> derives a serverless alternative. The evaluation engine compares both options
> using requirement fit, scalability, security, performance, maintainability,
> cost, complexity, and availability. The weights are influenced by the
> non-functional requirements, and the report displays the evidence behind the
> selected architecture.
>
> After selection, the Database Agent creates entities, fields, relationships,
> and requirement links. The local testing engine generates tests for every
> requirement. The traceability engine then connects requirements to user
> stories, components, APIs, database entities, tests, and risks. This graph is
> important because it allows MARIS to calculate coverage and analyze the impact
> of a future change.
>
> MARIS also performs a red-team review and a cross-agent consistency check. It
> can detect issues such as the architecture and database selecting different
> technologies, tests referencing missing APIs, or must-have requirements having
> no test coverage. It also generates Architecture Decision Records to explain
> what was selected, why it was selected, and what trade-offs were accepted.
>
> The main novelty of MARIS is its hybrid design. Generative AI is used for the
> parts that require interpretation and design creativity, while deterministic
> Python is used for scoring, validation, traceability, conflict detection,
> testing, impact analysis, and scenarios. Therefore, the system is more
> explainable and reproducible than a solution where every decision is made by
> an LLM.
>
> I also optimized the workflow for the Groq free tier. The original design
> could require approximately 18 API calls. The current design requires only
> three calls for a complete report: requirements, primary architecture, and
> database design. The other sections run locally, which reduces cost, latency,
> and rate-limit errors without removing the main intelligence features.
>
> The application uses React and Vite for the website, FastAPI for the backend,
> LangGraph for workflow orchestration, Groq for model inference, Pydantic for
> validation, Mermaid for diagrams, and ReportLab for PDF export. Users can save
> reports, inspect each section, analyze changes and failure scenarios, edit
> content, and download the final report.
>
> MARIS is currently an educational decision-support prototype. It does not
> replace a software architect or perform real load testing. In future phases, I
> would add persistent database storage, repository analysis, architecture drift
> detection, real performance testing, cloud cost estimation, and team approval
> workflows.
>
> In summary, MARIS does more than generate documentation. It creates competing
> designs, evaluates them with visible rules, validates their consistency, and
> preserves traceability across the complete architecture report. Thank you.

## Likely Viva Questions

### Why did you use multiple roles instead of one prompt?

Each role has a limited responsibility and produces an artifact that can be
validated before the next stage. This improves structure, debugging, and
traceability.

### What is the main novelty?

The main novelty is the combination of LLM generation with deterministic
architecture evaluation, conflict detection, consistency validation,
traceability traversal, scenarios, and change-impact analysis.

### Why is the second architecture deterministic?

It preserves meaningful architecture comparison while keeping the complete
workflow inside Groq's free-tier limits. It also demonstrates that AI and
traditional algorithms can cooperate instead of using an LLM for every task.

### Why use LangGraph if the workflow is sequential?

LangGraph makes the workflow state and execution order explicit. It also allows
bounded refinement to be enabled later without redesigning the application.

### How is hallucination reduced?

Pydantic validates the generated structure, deterministic checks reject broken
references, conflicts require explicit evidence, and stable IDs make unsupported
links detectable. Human review is still required.

### Are the architecture scores objective?

They are reproducible heuristics based on documented style baselines,
requirement coverage, quality tactics, and NFR-derived weights. They support a
decision but are not a replacement for benchmarks or expert judgment.

### Why use JSON storage?

JSON keeps the semester prototype small and easy to understand. Persistent SQL
storage is identified as the next production improvement.

### How is security handled?

Passwords use salted PBKDF2 hashes, sessions protect report endpoints, and the
Groq key remains in environment variables. Production deployment would require
stronger identity management, persistent storage, HTTPS, rate limiting, and
security testing.

## Author

Developed as a Software Engineering semester project by **[Your Name]**.
