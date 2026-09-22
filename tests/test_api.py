import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from engine import build_traceability, evaluate_architectures
from main import app
from models import ArchitectureOption
from tests.test_workflow import DATABASE, REQUIREMENTS, TESTS, option


class ApiTests(unittest.TestCase):
    def test_authenticated_impact_and_scenario_endpoints(self):
        architecture = ArchitectureOption.model_validate(option("A1", "modular monolith"))
        evaluation = evaluate_architectures(REQUIREMENTS, [architecture])
        traceability = build_traceability(REQUIREMENTS, architecture, DATABASE, TESTS)
        result = {
            "report": "# Architecture Report",
            "analysis": {
                "requirements": REQUIREMENTS.model_dump(),
                "architectures": [architecture.model_dump()],
                "evaluation": evaluation.model_dump(),
                "database": DATABASE.model_dump(),
                "traceability": traceability.model_dump(),
            },
        }

        with tempfile.TemporaryDirectory() as directory, \
             patch("utils.DATA_DIR", directory), \
             patch("main.run_workflow", return_value=result):
            client = TestClient(app)
            registered = client.post("/register", json={"username": "student", "password": "secret1"})
            self.assertEqual(registered.status_code, 200)
            analyzed = client.post("/analyze", json={"project": "Build a room booking app"})
            self.assertEqual(analyzed.status_code, 200)
            analysis_id = analyzed.json()["analysis_id"]

            impact = client.post("/impact", json={
                "analysis_id": analysis_id,
                "change_request": "Students can book rooms from a mobile app",
            })
            self.assertEqual(impact.status_code, 200)
            self.assertEqual(impact.json()["affected_requirements"], ["FR-01"])

            scenario = client.post("/scenario", json={
                "analysis_id": analysis_id, "scenario_id": "database_failure",
            })
            self.assertEqual(scenario.status_code, 200)
            self.assertEqual(scenario.json()["impact_level"], "high")


if __name__ == "__main__":
    unittest.main()
