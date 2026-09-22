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
    risks: list[str]


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
