from models import TestPlan
from prompts import TESTING_PROMPT
from utils import ask_groq_json


def testing_agent(text):
    return ask_groq_json(TESTING_PROMPT, text, TestPlan, 3000)


def testing_markdown(data):
    lines = []
    labels = {"unit": "Unit Tests", "integration": "Integration Tests",
              "acceptance": "Acceptance Tests", "edge_case": "Edge Cases"}
    for test_type, label in labels.items():
        lines.append(f"### {label}")
        for item in [test for test in data.test_cases if test.test_type == test_type]:
            refs = ", ".join(item.requirement_ids) or "No requirement reference"
            lines.append(f"- **{item.id}: {item.title}** — {item.description} ({refs})")
        lines.append("")
    return "\n".join(lines)
