from typing import TypedDict

from langgraph.graph import END, StateGraph

from agents.architect import architect_agent, architecture_markdown
from agents.clarification import clarification_agent
from agents.database import database_agent
from agents.feedback import feedback_agent
from agents.novelty import novelty_agent
from agents.planner import planner_agent
from agents.requirement import requirement_agent, requirements_markdown
from agents.reviewer import reviewer_agent
from agents.testing import testing_agent
from agents.traceability import traceability_agent
from engine import (conflicts_markdown, detect_requirement_conflicts,
                    evaluate_architectures, evaluation_markdown)
from models import ArchitectureOption, RequirementSet


class State(TypedDict):
    project: str
    details: str
    option_count: int
    requirements_data: dict
    conflicts_data: dict
    architecture_options: list[dict]
    evaluation_data: dict
    clarification: str
    requirements: str
    conflicts: str
    plan: str
    architecture: str
    evaluation: str
    database: str
    novelty: str
    traceability: str
    testing: str
    review: str
    feedback: str
    report: str


def clarification_node(state):
    state["clarification"] = clarification_agent(state["details"])
    return state


def requirement_node(state):
    result = requirement_agent(state["details"])
    state["requirements_data"] = result.model_dump()
    state["requirements"] = requirements_markdown(result)
    return state


def conflict_node(state):
    requirements = RequirementSet.model_validate(state["requirements_data"])
    result = detect_requirement_conflicts(requirements)
    state["conflicts_data"] = result.model_dump()
    state["conflicts"] = conflicts_markdown(result)
    return state


def planner_node(state):
    state["plan"] = planner_agent(state["details"])
    return state


def architect_node(state):
    result = architect_agent(state["details"], state["requirements_data"], state["option_count"])
    state["architecture_options"] = [item.model_dump() for item in result.options]
    state["architecture"] = architecture_markdown(result)
    return state


def evaluation_node(state):
    requirements = RequirementSet.model_validate(state["requirements_data"])
    options = [ArchitectureOption.model_validate(item) for item in state["architecture_options"]]
    result = evaluate_architectures(requirements, options)
    state["evaluation_data"] = result.model_dump()
    state["evaluation"] = evaluation_markdown(result)
    return state


def database_node(state):
    state["database"] = database_agent(state["details"])
    return state


def novelty_node(state):
    text = build_report(state)
    state["novelty"] = novelty_agent(text[:3000])
    return state


def traceability_node(state):
    state["traceability"] = traceability_agent(build_report(state)[:4500])
    return state


def testing_node(state):
    state["testing"] = testing_agent(build_report(state)[:5000])
    return state


def reviewer_node(state):
    report = build_report(state)
    state["review"] = reviewer_agent(report[:5000])
    state["feedback"] = feedback_agent(state["review"])
    state["report"] = report + "\n\n## Reviewer Notes\n" + state["review"]
    state["report"] += "\n\n## Feedback Loop\n" + state["feedback"]
    return state


def build_report(state):
    sections = [
        "# Architecture Intelligence Report",
        "## Project\n" + state["project"],
        "## Clarification and Assumptions\n" + state.get("clarification", ""),
        "## Requirements\n" + state["requirements"],
        "## Requirement Conflict Analysis\n" + state.get("conflicts", ""),
        "## Project Plan\n" + state["plan"],
        "## Architecture Debate\n" + state["architecture"],
        "## Architecture Evaluation\n" + state.get("evaluation", ""),
        "## Database Design\n" + state["database"],
        "## Novelty Analysis\n" + state.get("novelty", ""),
        "## Requirements Traceability\n" + state.get("traceability", ""),
        "## Test Plan\n" + state.get("testing", ""),
    ]
    return "\n\n".join(sections)


def run_workflow(project, project_type="General", depth="Short", context=""):
    graph = StateGraph(State)
    nodes = [("clarification", clarification_node), ("requirement", requirement_node),
             ("conflicts", conflict_node)]
    nodes += [("planner", planner_node), ("architect", architect_node)]
    nodes += [("evaluation", evaluation_node), ("database", database_node), ("novelty", novelty_node)]
    nodes += [("traceability", traceability_node), ("testing", testing_node)]
    nodes += [("reviewer", reviewer_node)]

    for name, node in nodes:
        graph.add_node(name, node)
    graph.set_entry_point("clarification")

    steps = ["clarification", "requirement", "conflicts", "planner", "architect", "evaluation"]
    steps += ["database", "novelty", "traceability", "testing", "reviewer"]
    for first, second in zip(steps, steps[1:]):
        graph.add_edge(first, second)
    graph.add_edge("reviewer", END)

    details = f"Project: {project}\nType: {project_type}\nDepth: {depth}\nContext: {context[:2000]}"
    option_count = 2 if depth == "Short" else 3
    result = graph.compile().invoke({"project": project, "details": details, "option_count": option_count})
    return {
        "clarification": result["clarification"],
        "requirements": result["requirements"],
        "conflicts": result["conflicts"],
        "plan": result["plan"],
        "architecture": result["architecture"],
        "evaluation": result["evaluation"],
        "database": result["database"],
        "novelty": result["novelty"],
        "traceability": result["traceability"],
        "testing": result["testing"],
        "review": result["review"],
        "feedback": result["feedback"],
        "report": result["report"],
        "analysis": {
            "requirements": result["requirements_data"],
            "conflicts": result["conflicts_data"],
            "architectures": result["architecture_options"],
            "evaluation": result["evaluation_data"],
        },
    }
