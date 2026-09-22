import unittest
from unittest.mock import patch

from models import (ArchitectureOption, ArchitectureSet, DatabaseDesign,
                    QualityTactic, RedTeamReview, RequirementSet, TestPlan)
from workflow import run_workflow


REQUIREMENTS = RequirementSet.model_validate({
    "summary": "A booking system.",
    "requirements": [
        {"id": "FR-01", "category": "functional", "statement": "Book a room", "priority": "must", "quality_attribute": "functional", "keywords": ["book", "room"]},
        {"id": "NFR-01", "category": "non_functional", "statement": "Remain affordable", "priority": "should", "quality_attribute": "cost", "keywords": ["low cost"]},
    ],
    "user_stories": [{"id": "US-01", "role": "student", "goal": "book a room", "benefit": "I can study", "requirement_ids": ["FR-01"]}],
    "assumptions": ["The university manages rooms."],
})


def option(identifier, style):
    return {
        "id": identifier, "name": f"{style} option", "style": style, "summary": "Simple design.",
        "components": [{"id": f"{identifier}-C1", "name": "API", "responsibility": "Bookings", "communication": "HTTPS", "supports_requirements": ["FR-01"]}],
        "apis": [{"id": f"{identifier}-API1", "method": "POST", "path": "/bookings", "responsibility": "Create booking", "component_id": f"{identifier}-C1", "supports_requirements": ["FR-01"]}],
        "database": "PostgreSQL", "technology_stack": ["FastAPI", "PostgreSQL"],
        "quality_tactics": [{"attribute": "cost", "tactic": "single deployment", "evidence": "One service"}],
        "advantages": ["Simple"], "disadvantages": ["Limited scaling"], "assumptions": ["Small team"],
        "risks": [{"id": f"{identifier}-RISK1", "description": "Single instance",
                   "component_ids": [f"{identifier}-C1"], "requirement_ids": ["FR-01"]}],
    }


DATABASE = DatabaseDesign.model_validate({
    "engine": "PostgreSQL", "rationale": "Transactional bookings.",
    "entities": [{"id": "DBE-01", "name": "Booking", "purpose": "Stores bookings",
                  "fields": [{"name": "id", "data_type": "uuid", "constraints": ["primary key"]}],
                  "supports_requirements": ["FR-01"]}],
    "relationships": [], "risks": ["Single instance"],
})

TESTS = TestPlan.model_validate({
    "test_cases": [{"id": "TC-01", "test_type": "acceptance", "title": "Create booking",
                    "description": "A student books a room.", "requirement_ids": ["FR-01"],
                    "component_ids": ["A1-C1"], "api_ids": ["A1-API1"]}],
})

RED_TEAM = RedTeamReview.model_validate({
    "summary": "One availability risk was found.",
    "findings": [{"id": "RT-01", "severity": "high", "title": "Single instance",
                  "description": "The API has no failover.", "evidence": "A1-RISK1",
                  "affected_artifact_ids": ["A1-C1", "UNKNOWN"],
                  "recommendation": "Add a health-checked standby."}],
})

REFINED = ArchitectureOption.model_validate(option("A1", "modular monolith"))
REFINED.quality_tactics.append(QualityTactic(
    attribute="availability", tactic="health-checked standby", evidence="Failover instance"))
REFINED.risks = []


class WorkflowTests(unittest.TestCase):
    @patch("workflow.refine_architecture", return_value=REFINED)
    @patch("workflow.feedback_agent", return_value="Feedback")
    @patch("workflow.reviewer_agent", return_value="Score 8/10")
    @patch("workflow.red_team_agent", return_value=RED_TEAM)
    @patch("workflow.testing_agent", return_value=TESTS)
    @patch("workflow.novelty_agent", return_value="Novelty")
    @patch("workflow.database_agent", return_value=DATABASE)
    @patch("workflow.planner_agent", return_value="Plan")
    @patch("workflow.architect_agent")
    @patch("workflow.requirement_agent", return_value=REQUIREMENTS)
    @patch("workflow.clarification_agent", return_value="Clarification")
    def test_short_report_contains_two_structured_options(self, _, __, architect, *args):
        architect.return_value = ArchitectureSet(options=[option("A1", "modular monolith"), option("A2", "microservices")])
        result = run_workflow("Build a university booking system", depth="Short")
        self.assertEqual(len(result["analysis"]["architectures"]), 2)
        self.assertEqual(result["analysis"]["requirements"]["requirements"][0]["id"], "FR-01")
        self.assertEqual(result["analysis"]["red_team"]["findings"][0]["affected_artifact_ids"], ["A1-C1"])
        self.assertEqual(len(result["analysis"]["versions"]), 2)
        self.assertIn("Added quality tactics", result["refinement"])
        self.assertIn("A1: modular monolith option", result["architecture"])


if __name__ == "__main__":
    unittest.main()
