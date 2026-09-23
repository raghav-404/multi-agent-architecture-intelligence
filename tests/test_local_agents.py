import json
import unittest
from unittest.mock import patch

from agents.architect import architect_agent
from agents.red_team import red_team_agent
from agents.testing import testing_agent
from models import ArchitectureOption
from tests.test_workflow import REQUIREMENTS, option


class LocalAgentTests(unittest.TestCase):
    @patch("agents.architect.ask_groq_json")
    def test_two_architectures_need_one_groq_call(self, ask_groq):
        ask_groq.return_value = ArchitectureOption.model_validate(
            option("A1", "modular monolith"))
        result = architect_agent("Booking app", REQUIREMENTS.model_dump(), 2)
        self.assertEqual(ask_groq.call_count, 1)
        self.assertEqual([item.style for item in result.options],
                         ["modular monolith", "serverless"])

    def test_testing_covers_every_requirement_without_groq(self):
        data = {"requirements": REQUIREMENTS.model_dump(),
                "architecture": option("A1", "modular monolith"), "database": {}}
        plan = testing_agent(json.dumps(data))
        covered = {item for test in plan.test_cases for item in test.requirement_ids}
        self.assertEqual(covered, {"FR-01", "NFR-01"})

    def test_red_team_converts_documented_risks_to_findings(self):
        data = {"architecture": option("A1", "modular monolith")}
        review = red_team_agent(json.dumps(data))
        self.assertEqual(review.findings[0].evidence, "A1-RISK1")
        self.assertEqual(review.findings[0].affected_artifact_ids, ["A1-C1"])


if __name__ == "__main__":
    unittest.main()
