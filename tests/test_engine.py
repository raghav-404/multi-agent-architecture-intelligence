import unittest

from engine import (analyze_change_impact, analyze_scenario, build_traceability,
                    check_consistency, detect_requirement_conflicts,
                    evaluate_architectures, generate_adrs)
from agents.architect import normalize_ids
from models import ArchitectureOption, RequirementSet, TestPlan
from tests.test_workflow import DATABASE, REQUIREMENTS, TESTS, option


class EvaluationTests(unittest.TestCase):
    def test_architecture_ids_are_namespaced(self):
        architecture = ArchitectureOption.model_validate(option("OLD", "modular monolith"))
        architecture.components[0].id = "component"
        architecture.apis[0].component_id = "component"
        architecture.risks[0].component_ids = ["component"]
        normalized = normalize_ids(architecture, 2)
        self.assertEqual(normalized.components[0].id, "A2-C1")
        self.assertEqual(normalized.apis[0].component_id, "A2-C1")
        self.assertEqual(normalized.risks[0].component_ids, ["A2-C1"])

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

    def test_consistency_finds_database_mismatch_and_missing_tests(self):
        database = DATABASE.model_copy(update={"engine": "MongoDB"})
        report = check_consistency(
            REQUIREMENTS, ArchitectureOption.model_validate(option("A1", "modular monolith")),
            database, TestPlan(test_cases=[]))
        categories = {item.category for item in report.issues}
        self.assertEqual(report.status, "fail")
        self.assertIn("database_mismatch", categories)
        self.assertIn("missing_test_coverage", categories)

    def test_consistent_artifacts_pass(self):
        report = check_consistency(
            REQUIREMENTS, ArchitectureOption.model_validate(option("A1", "modular monolith")),
            DATABASE, TESTS)
        self.assertEqual(report.status, "pass")
        self.assertEqual(report.score, 100)

    def test_traceability_uses_real_artifact_ids(self):
        graph = build_traceability(
            REQUIREMENTS, ArchitectureOption.model_validate(option("A1", "modular monolith")),
            DATABASE, TESTS)
        fr_targets = {edge.target for edge in graph.edges if edge.source == "FR-01"}
        self.assertTrue({"US-01", "A1-C1", "A1-API1", "DBE-01", "TC-01"}.issubset(fr_targets))
        self.assertEqual(graph.coverage_percentage, 50)
        self.assertEqual(graph.uncovered_requirements, ["NFR-01"])

    def test_change_impact_traverses_traceability_graph(self):
        graph = build_traceability(
            REQUIREMENTS, ArchitectureOption.model_validate(option("A1", "modular monolith")),
            DATABASE, TESTS)
        impact = analyze_change_impact("Students can book rooms from a mobile app", REQUIREMENTS, graph)
        self.assertEqual(impact.affected_requirements, ["FR-01"])
        self.assertIn("A1-C1", impact.affected_components)
        self.assertIn("TC-01", impact.affected_tests)
        self.assertIn("A1-RISK1", impact.affected_risks)

    def test_scenario_analysis_uses_selected_artifacts(self):
        result = analyze_scenario(
            "traffic_100x", ArchitectureOption.model_validate(option("A1", "modular monolith")),
            DATABASE)
        self.assertEqual(result.impact_level, "high")
        self.assertEqual(result.affected_components, ["A1-C1"])
        self.assertEqual(result.affected_database_entities, ["DBE-01"])
        self.assertIn("not a performance prediction", result.disclaimer)

    def test_scenario_reports_missing_dependency(self):
        result = analyze_scenario(
            "authentication_failure", ArchitectureOption.model_validate(option("A1", "modular monolith")),
            DATABASE)
        self.assertEqual(result.affected_components, [])
        self.assertTrue(any("No explicit" in risk for risk in result.risks))

    def test_adrs_use_deterministic_selection(self):
        options = [ArchitectureOption.model_validate(option("A1", "modular monolith")),
                   ArchitectureOption.model_validate(option("A2", "microservices"))]
        evaluation = evaluate_architectures(REQUIREMENTS, options)
        adrs = generate_adrs(REQUIREMENTS, options, evaluation, DATABASE)
        self.assertEqual(adrs[0].decision, options[0].name)
        self.assertIn(str(evaluation.evaluations[0].weighted_total), adrs[0].reason)
        self.assertEqual(adrs[1].decision, "PostgreSQL")


if __name__ == "__main__":
    unittest.main()
