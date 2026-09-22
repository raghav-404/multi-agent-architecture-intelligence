from typing import Literal

from pydantic import BaseModel, ConfigDict


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Requirement(StrictModel):
    id: str
    category: Literal["functional", "non_functional"]
    statement: str
    priority: Literal["must", "should", "could"]
    quality_attribute: str
    keywords: list[str]


class UserStory(StrictModel):
    id: str
    role: str
    goal: str
    benefit: str
    requirement_ids: list[str]


class RequirementSet(StrictModel):
    summary: str
    requirements: list[Requirement]
    user_stories: list[UserStory]
    assumptions: list[str]


class RequirementConflict(StrictModel):
    id: str
    requirement_ids: list[str]
    title: str
    explanation: str
    severity: Literal["low", "medium", "high"]
    resolution: str


class ConflictReport(StrictModel):
    conflicts: list[RequirementConflict]


class ArchitectureComponent(StrictModel):
    id: str
    name: str
    responsibility: str
    communication: str
    supports_requirements: list[str]


class ArchitectureApi(StrictModel):
    id: str
    method: str
    path: str
    responsibility: str
    component_id: str
    supports_requirements: list[str]


class QualityTactic(StrictModel):
    attribute: str
    tactic: str
    evidence: str


class ArchitectureRisk(StrictModel):
    id: str
    description: str
    component_ids: list[str]
    requirement_ids: list[str]


class ArchitectureOption(StrictModel):
    id: str
    name: str
    style: str
    summary: str
    components: list[ArchitectureComponent]
    apis: list[ArchitectureApi]
    database: str
    technology_stack: list[str]
    quality_tactics: list[QualityTactic]
    advantages: list[str]
    disadvantages: list[str]
    assumptions: list[str]
    risks: list[ArchitectureRisk]


class ArchitectureSet(StrictModel):
    options: list[ArchitectureOption]


class CriterionScore(StrictModel):
    criterion: str
    score: int
    weight: float
    evidence: list[str]


class ArchitectureEvaluation(StrictModel):
    architecture_id: str
    scores: list[CriterionScore]
    weighted_total: float
    covered_requirements: list[str]
    uncovered_requirements: list[str]


class EvaluationResult(StrictModel):
    evaluations: list[ArchitectureEvaluation]
    selected_architecture_id: str
    selection_reason: str


class DatabaseField(StrictModel):
    name: str
    data_type: str
    constraints: list[str]


class DatabaseEntity(StrictModel):
    id: str
    name: str
    purpose: str
    fields: list[DatabaseField]
    supports_requirements: list[str]


class DatabaseRelationship(StrictModel):
    source_entity_id: str
    target_entity_id: str
    relationship: str


class DatabaseDesign(StrictModel):
    engine: str
    rationale: str
    entities: list[DatabaseEntity]
    relationships: list[DatabaseRelationship]
    risks: list[str]


class TestCase(StrictModel):
    id: str
    test_type: Literal["unit", "integration", "acceptance", "edge_case"]
    title: str
    description: str
    requirement_ids: list[str]
    component_ids: list[str]
    api_ids: list[str]


class TestPlan(StrictModel):
    test_cases: list[TestCase]


class ConsistencyIssue(StrictModel):
    id: str
    severity: Literal["low", "medium", "high"]
    category: str
    description: str
    evidence: list[str]
    affected_artifacts: list[str]


class ConsistencyReport(StrictModel):
    status: Literal["pass", "warning", "fail"]
    score: int
    issues: list[ConsistencyIssue]


class TraceNode(StrictModel):
    id: str
    node_type: Literal["requirement", "user_story", "component", "database_entity", "api", "test", "risk"]
    label: str


class TraceEdge(StrictModel):
    source: str
    target: str
    relationship: str


class TraceabilityGraph(StrictModel):
    nodes: list[TraceNode]
    edges: list[TraceEdge]
    coverage_percentage: int
    uncovered_requirements: list[str]


class RedTeamFinding(StrictModel):
    id: str
    severity: Literal["critical", "high", "medium", "low"]
    title: str
    description: str
    evidence: str
    affected_artifact_ids: list[str]
    recommendation: str


class RedTeamReview(StrictModel):
    summary: str
    findings: list[RedTeamFinding]
