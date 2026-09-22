import unittest
from unittest.mock import patch

from models import ArchitectureSet, RequirementSet
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
        "advantages": ["Simple"], "disadvantages": ["Limited scaling"], "assumptions": ["Small team"], "risks": ["Single instance"],
    }


class WorkflowTests(unittest.TestCase):
    @patch("workflow.feedback_agent", return_value="Feedback")
    @patch("workflow.reviewer_agent", return_value="Score 8/10")
    @patch("workflow.testing_agent", return_value="Tests")
    @patch("workflow.traceability_agent", return_value="Traceability")
    @patch("workflow.novelty_agent", return_value="Novelty")
    @patch("workflow.database_agent", return_value="Database")
    @patch("workflow.planner_agent", return_value="Plan")
    @patch("workflow.architect_agent")
    @patch("workflow.requirement_agent", return_value=REQUIREMENTS)
    @patch("workflow.clarification_agent", return_value="Clarification")
    def test_short_report_contains_two_structured_options(self, _, __, architect, *args):
        architect.return_value = ArchitectureSet(options=[option("A1", "modular monolith"), option("A2", "serverless")])
        result = run_workflow("Build a university booking system", depth="Short")
        self.assertEqual(len(result["analysis"]["architectures"]), 2)
        self.assertEqual(result["analysis"]["requirements"]["requirements"][0]["id"], "FR-01")
        self.assertIn("A1: modular monolith option", result["architecture"])


if __name__ == "__main__":
    unittest.main()
