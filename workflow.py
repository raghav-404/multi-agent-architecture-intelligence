from typing import TypedDict

from langgraph.graph import END, StateGraph

from agents.architect import architect_agent
from agents.database import database_agent
from agents.planner import planner_agent
from agents.requirement import requirement_agent
from agents.reviewer import reviewer_agent


class State(TypedDict):
    project: str
    requirements: str
    plan: str
    architecture: str
    database: str
    review: str
    report: str


def requirement_node(state):
    state["requirements"] = requirement_agent(state["project"])
    return state


def planner_node(state):
    state["plan"] = planner_agent(state["project"])
    return state


def architect_node(state):
    state["architecture"] = architect_agent(state["project"])
    return state


def database_node(state):
    state["database"] = database_agent(state["project"])
    return state


def reviewer_node(state):
    report = build_report(state)
    state["review"] = reviewer_agent(report[:3000])
    state["report"] = report + "\n\n# Reviewer Notes\n\n" + state["review"]
    return state


def build_report(state):
    sections = [
        "# Architecture Intelligence Report",
        "## Project\n" + state["project"],
        "## Requirements\n" + state["requirements"],
        "## Project Plan\n" + state["plan"],
        "## Architecture\n" + state["architecture"],
        "## Database Design\n" + state["database"],
    ]
    return "\n\n".join(sections)


def run_workflow(project):
    graph = StateGraph(State)
    nodes = [("requirement", requirement_node), ("planner", planner_node)]
    nodes += [("architect", architect_node), ("database", database_node)]
    nodes += [("reviewer", reviewer_node)]

    for name, node in nodes:
        graph.add_node(name, node)
    graph.set_entry_point("requirement")

    steps = ["requirement", "planner", "architect", "database", "reviewer"]
    for first, second in zip(steps, steps[1:]):
        graph.add_edge(first, second)
    graph.add_edge("reviewer", END)

    result = graph.compile().invoke({"project": project})
    return result["report"]
