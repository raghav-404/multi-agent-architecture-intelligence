import json

from models import TestCase, TestPlan


def testing_agent(text):
    data = json.loads(text)
    architecture = data["architecture"]
    tests = []
    for index, requirement in enumerate(data["requirements"]["requirements"], 1):
        requirement_id = requirement["id"]
        components = [item["id"] for item in architecture["components"]
                      if requirement_id in item["supports_requirements"]]
        apis = [item["id"] for item in architecture["apis"]
                if requirement_id in item["supports_requirements"]]
        tests.append(TestCase(
            id=f"TC-{index:02d}",
            test_type="acceptance" if requirement["category"] == "functional" else "edge_case",
            title=f"Verify {requirement_id}", description=requirement["statement"],
            requirement_ids=[requirement_id], component_ids=components, api_ids=apis,
        ))
    return TestPlan(test_cases=tests)


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
