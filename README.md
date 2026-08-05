# Multi-Agent Architecture Intelligence System

A small semester project that accepts a software project idea and sends it through five AI agents:

1. Requirement Agent
2. Project Planner Agent
3. Architecture Agent
4. Database Agent
5. Reviewer Agent

The final output is shown as agent-by-agent tabs and can be downloaded as a PDF.

## Setup

```bash
cd multi-agent-architecture-intelligence
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If Streamlit shows a Starlette `GZipResponder` error, reinstall the pinned versions:

```bash
pip install --upgrade --force-reinstall -r requirements.txt
```

Edit `.env` and add your Groq API key:

```text
GROQ_API_KEY=your_real_key_here
```

## Run the FastAPI Server

```bash
uvicorn main:app --reload
```

Test the API. It returns markdown text:

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"project":"Build an Online Food Delivery System"}'
```

## Run the Streamlit UI

Open a second terminal and run:

```bash
streamlit run frontend.py
```

Then enter a project idea and click **Generate Report**.

The UI shows:

- Separate tabs for each agent output
- A full report tab
- A PDF download button

## Output

Each analysis is saved to `history.json`:

```json
[
  {
    "project": "Online Food Delivery",
    "report": "..."
  }
]
```
