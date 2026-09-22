import json
from typing import TypedDict

from langgraph.graph import END, StateGraph

from agents.architect import (architect_agent, architecture_markdown,
                              refine_architecture)
from agents.clarification import clarification_agent
from agents.database import database_agent, database_markdown
from agents.feedback import feedback_agent
from agents.novelty import novelty_agent
from agents.planner import planner_agent
from agents.requirement import requirement_agent, requirements_markdown
from agents.red_team import red_team_agent, red_team_markdown
from agents.reviewer import reviewer_agent
from agents.testing import testing_agent, testing_markdown
from engine import (architecture_changes, build_traceability, conflicts_markdown,
                    detect_requirement_conflicts,
                    check_consistency, consistency_markdown,
                    evaluate_architectures, evaluation_markdown, generate_adrs,
                    adrs_markdown,
                    traceability_markdown, versions_markdown)
from models import (ArchitectureOption, ArchitectureSet, ArchitectureVersion,
                    ConsistencyReport, DatabaseDesign, EvaluationResult,
                    RedTeamReview, RequirementSet, TestPlan,
                    TraceabilityGraph)


class State(TypedDict):
    project: str
    details: str
    option_count: int
    iteration: int
    max_iterations: int
    pending_changes: list[str]
    architecture_versions: list[dict]
    requirements_data: dict
    conflicts_data: dict
    architecture_options: list[dict]
    evaluation_data: dict
    database_data: dict
    testing_data: dict
    consistency_data: dict
    traceability_data: dict
    red_team_data: dict
    adrs_data: list[dict]
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
    consistency: str
    red_team: str
    refinement: str
    adrs: str
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
    evaluation = EvaluationResult.model_validate(state["evaluation_data"])
    selected = next(item for item in state["architecture_options"]
                    if item["id"] == evaluation.selected_architecture_id)
    text = state["details"] + "\nRequirements:\n" + json.dumps(state["requirements_data"])
    text += "\nSelected architecture:\n" + json.dumps(selected)
    result = database_agent(text)
    state["database_data"] = result.model_dump()
    state["database"] = database_markdown(result)
    return state


def novelty_node(state):
    text = build_report(state)
    state["novelty"] = novelty_agent(text[:3000])
    return state


def traceability_node(state):
    requirements = RequirementSet.model_validate(state["requirements_data"])
    evaluation = EvaluationResult.model_validate(state["evaluation_data"])
    selected = next(ArchitectureOption.model_validate(item) for item in state["architecture_options"]
                    if item["id"] == evaluation.selected_architecture_id)
    database = DatabaseDesign.model_validate(state["database_data"])
    tests = TestPlan.model_validate(state["testing_data"])
    result = build_traceability(requirements, selected, database, tests)
    state["traceability_data"] = result.model_dump()
    state["traceability"] = traceability_markdown(result)
    return state


def testing_node(state):
    evaluation = EvaluationResult.model_validate(state["evaluation_data"])
    selected = next(item for item in state["architecture_options"]
                    if item["id"] == evaluation.selected_architecture_id)
    text = json.dumps({"requirements": state["requirements_data"],
                       "architecture": selected, "database": state["database_data"]})
    result = testing_agent(text)
    state["testing_data"] = result.model_dump()
    state["testing"] = testing_markdown(result)
    return state


def consistency_node(state):
    requirements = RequirementSet.model_validate(state["requirements_data"])
    evaluation = EvaluationResult.model_validate(state["evaluation_data"])
    selected = next(ArchitectureOption.model_validate(item) for item in state["architecture_options"]
                    if item["id"] == evaluation.selected_architecture_id)
    database = DatabaseDesign.model_validate(state["database_data"])
    tests = TestPlan.model_validate(state["testing_data"])
    result = check_consistency(requirements, selected, database, tests)
    state["consistency_data"] = result.model_dump()
    state["consistency"] = consistency_markdown(result)
    return state


def red_team_node(state):
    evaluation = EvaluationResult.model_validate(state["evaluation_data"])
    selected = next(item for item in state["architecture_options"]
                    if item["id"] == evaluation.selected_architecture_id)
    text = json.dumps({"requirements": state["requirements_data"],
                       "architecture": selected, "database": state["database_data"],
                       "testing": state["testing_data"], "traceability": state["traceability_data"],
                       "consistency": state.get("consistency_data", {})})
    result = red_team_agent(text)
    valid_ids = {item["id"] for item in state["requirements_data"]["requirements"]}
    valid_ids |= {item["id"] for item in selected["components"] + selected["apis"] + selected["risks"]}
    valid_ids |= {item["id"] for item in state["database_data"]["entities"]}
    valid_ids |= {item["id"] for item in state["testing_data"]["test_cases"]}
    for finding in result.findings:
        finding.affected_artifact_ids = [item for item in finding.affected_artifact_ids if item in valid_ids]
    state["red_team_data"] = result.model_dump()
    state["red_team"] = red_team_markdown(result)
    return state


def reviewer_node(state):
    report = build_report(state)
    state["review"] = reviewer_agent(report[:5000])
    state["feedback"] = feedback_agent(state["review"])

    evaluation = EvaluationResult.model_validate(state["evaluation_data"])
    selected = next(ArchitectureOption.model_validate(item) for item in state["architecture_options"]
                    if item["id"] == evaluation.selected_architecture_id)
    selected_score = next(item for item in evaluation.evaluations
                          if item.architecture_id == evaluation.selected_architecture_id)
    consistency = ConsistencyReport.model_validate(state["consistency_data"])
    traceability = TraceabilityGraph.model_validate(state["traceability_data"])
    red_team = RedTeamReview.model_validate(state["red_team_data"])
    versions = [ArchitectureVersion.model_validate(item) for item in state["architecture_versions"]]
    versions.append(ArchitectureVersion(
        version=len(versions) + 1, architecture=selected, evaluation=selected_score,
        consistency_score=consistency.score,
        traceability_coverage=traceability.coverage_percentage,
        critical_risks=sum(item.severity == "critical" for item in red_team.findings),
        high_risks=sum(item.severity == "high" for item in red_team.findings),
        changes=state["pending_changes"],
    ))
    state["architecture_versions"] = [item.model_dump() for item in versions]
    return state


def refinement_node(state):
    evaluation = EvaluationResult.model_validate(state["evaluation_data"])
    selected = next(ArchitectureOption.model_validate(item) for item in state["architecture_options"]
                    if item["id"] == evaluation.selected_architecture_id)
    context = json.dumps({
        "project": state["details"], "requirements": state["requirements_data"],
        "current_architecture": selected.model_dump(), "red_team": state["red_team_data"],
        "consistency": state["consistency_data"], "traceability": state["traceability_data"],
        "reviewer_notes": state["review"],
    })
    refined = refine_architecture(context, selected)
    state["pending_changes"] = architecture_changes(selected, refined)
    state["architecture_options"] = [refined.model_dump() if item["id"] == selected.id else item
                                     for item in state["architecture_options"]]
    state["architecture"] = architecture_markdown(
        ArchitectureSet(options=[ArchitectureOption.model_validate(item)
                                 for item in state["architecture_options"]]))
    state["iteration"] += 1
    return state


def route_after_review(state):
    red_team = RedTeamReview.model_validate(state["red_team_data"])
    consistency = ConsistencyReport.model_validate(state["consistency_data"])
    traceability = TraceabilityGraph.model_validate(state["traceability_data"])
    serious_risk = any(item.severity in ["critical", "high"] for item in red_team.findings)
    needs_work = serious_risk or consistency.status == "fail" or traceability.coverage_percentage < 80
    return "refine" if needs_work and state["iteration"] < state["max_iterations"] else "finish"


def finalize_node(state):
    versions = [ArchitectureVersion.model_validate(item) for item in state["architecture_versions"]]
    state["refinement"] = versions_markdown(versions)
    report = build_report(state)
    state["report"] = report + "\n\n## Reviewer Notes\n" + state["review"]
    state["report"] += "\n\n## Feedback Loop\n" + state["feedback"]
    return state


def adr_node(state):
    requirements = RequirementSet.model_validate(state["requirements_data"])
    options = [ArchitectureOption.model_validate(item) for item in state["architecture_options"]]
    evaluation = EvaluationResult.model_validate(state["evaluation_data"])
    database = DatabaseDesign.model_validate(state["database_data"])
    result = generate_adrs(requirements, options, evaluation, database)
    state["adrs_data"] = [item.model_dump() for item in result]
    state["adrs"] = adrs_markdown(result)
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
        "## Red Team Architecture Review\n" + state.get("red_team", ""),
        "## Cross-Agent Consistency\n" + state.get("consistency", ""),
        "## Architecture Refinement\n" + state.get("refinement", ""),
        "## Architecture Decision Records\n" + state.get("adrs", ""),
    ]
    return "\n\n".join(sections)


def run_workflow(project, project_type="General", depth="Short", context=""):
    graph = StateGraph(State)
    nodes = [("clarification", clarification_node), ("requirement", requirement_node),
             ("conflicts", conflict_node)]
    nodes += [("planner", planner_node), ("architect", architect_node)]
    nodes += [("evaluation", evaluation_node), ("database", database_node)]
    nodes += [("testing", testing_node), ("traceability", traceability_node)]
    nodes += [("red_team", red_team_node), ("consistency", consistency_node), ("reviewer", reviewer_node)]
    nodes += [("refinement", refinement_node), ("adrs", adr_node),
              ("novelty", novelty_node), ("finalize", finalize_node)]

    for name, node in nodes:
        graph.add_node(name, node)
    graph.set_entry_point("clarification")

    steps = ["clarification", "requirement", "conflicts", "planner", "architect", "evaluation"]
    steps += ["database", "testing", "traceability", "red_team", "consistency", "reviewer"]
    for first, second in zip(steps, steps[1:]):
        graph.add_edge(first, second)
    graph.add_conditional_edges("reviewer", route_after_review,
                                {"refine": "refinement", "finish": "adrs"})
    graph.add_edge("refinement", "evaluation")
    graph.add_edge("adrs", "novelty")
    graph.add_edge("novelty", "finalize")
    graph.add_edge("finalize", END)

    details = f"Project: {project}\nType: {project_type}\nDepth: {depth}\nContext: {context[:2000]}"
    option_count = 2 if depth == "Short" else 3
    max_iterations = 1 if depth == "Short" else 2
    result = graph.compile().invoke({
        "project": project, "details": details, "option_count": option_count,
        "iteration": 0, "max_iterations": max_iterations,
        "pending_changes": ["Initial selected architecture."], "architecture_versions": [],
    })
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
        "red_team": result["red_team"],
        "consistency": result["consistency"],
        "refinement": result["refinement"],
        "adrs": result["adrs"],
        "review": result["review"],
        "feedback": result["feedback"],
        "report": result["report"],
        "analysis": {
            "requirements": result["requirements_data"],
            "conflicts": result["conflicts_data"],
            "architectures": result["architecture_options"],
            "evaluation": result["evaluation_data"],
            "database": result["database_data"],
            "testing": result["testing_data"],
            "traceability": result["traceability_data"],
            "red_team": result["red_team_data"],
            "consistency": result["consistency_data"],
            "versions": result["architecture_versions"],
            "adrs": result["adrs_data"],
        },
    }
