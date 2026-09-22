import unittest

from engine import detect_requirement_conflicts, evaluate_architectures
from models import ArchitectureOption, RequirementSet
from tests.test_workflow import REQUIREMENTS, option


class EvaluationTests(unittest.TestCase):
    def test_low_cost_project_prefers_simpler_option(self):
        requirements = RequirementSet.model_validate(REQUIREMENTS)
        options = [
            ArchitectureOption.model_validate(option("A1", "modular monolith")),
            ArchitectureOption.model_validate(option("A2", "microservices")),
        ]
        result = evaluate_architectures(requirements, options)
        self.assertEqual(result.selected_architecture_id, "A1")
        self.assertGreater(result.evaluations[0].weighted_total,
                           result.evaluations[1].weighted_total)

    def test_requirement_fit_uses_explicit_references(self):
        data = option("A1", "modular monolith")
        data["components"][0]["supports_requirements"] = []
        data["apis"][0]["supports_requirements"] = []
        result = evaluate_architectures(
            REQUIREMENTS, [ArchitectureOption.model_validate(data)])
        fit = result.evaluations[0].scores[0]
        self.assertEqual(fit.criterion, "requirement_fit")
        self.assertEqual(fit.score, 0)

    def test_conflict_requires_both_explicit_sides(self):
        data = REQUIREMENTS.model_dump()
        data["requirements"].append({
            "id": "NFR-02", "category": "non_functional",
            "statement": "Provide 99.99% high availability", "priority": "must",
            "quality_attribute": "availability", "keywords": ["uptime"],
        })
        report = detect_requirement_conflicts(RequirementSet.model_validate(data))
        self.assertEqual(len(report.conflicts), 1)
        self.assertEqual(report.conflicts[0].requirement_ids, ["NFR-01", "NFR-02"])

    def test_no_conflict_is_invented(self):
        report = detect_requirement_conflicts(REQUIREMENTS)
        self.assertEqual(report.conflicts, [])


if __name__ == "__main__":
    unittest.main()
