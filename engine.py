import re

from models import (ArchitectureEvaluation, ConflictReport, CriterionScore,
                    ConsistencyIssue, ConsistencyReport, EvaluationResult,
                    ImpactResult, RequirementConflict, TraceEdge, TraceNode,
                    TraceabilityGraph)


CRITERIA = ["requirement_fit", "scalability", "security", "performance",
            "maintainability", "cost", "complexity", "availability"]

STYLE_SCORES = {
    "monolith": [5, 7, 7, 7, 9, 9, 5],
    "modular monolith": [7, 7, 8, 9, 8, 8, 7],
    "microservices": [9, 8, 8, 7, 4, 3, 9],
    "serverless": [9, 7, 7, 7, 7, 6, 8],
    "event driven": [9, 7, 8, 6, 5, 4, 8],
    "layered": [6, 7, 7, 8, 8, 8, 6],
}

ATTRIBUTE_ALIASES = {
    "scalability": ["scale", "traffic", "concurrent", "throughput"],
    "security": ["secure", "privacy", "authentication", "authorization", "encrypt"],
    "performance": ["latency", "fast", "response time", "performance"],
    "maintainability": ["maintain", "modular", "changeability", "supportability"],
    "cost": ["cost", "budget", "affordable", "cheap"],
    "complexity": ["simple", "simplicity", "small team", "rapid delivery"],
    "availability": ["available", "uptime", "reliable", "fault tolerance"],
}

CONFLICT_RULES = [
    ("security", "low_latency", "Security controls vs low latency", "medium",
     "Strong authentication and encryption can add processing and network overhead.",
     "Set an explicit latency budget and measure the selected security controls."),
    ("low_cost", "availability", "Low cost vs high availability", "high",
     "Redundancy and failover improve availability but require additional infrastructure.",
     "Define an uptime target and fund only the redundancy needed for that target."),
    ("consistency", "geo_availability", "Strong consistency vs geographic availability", "high",
     "Synchronous cross-region consistency can reduce availability during network partitions.",
     "Choose which operations require strong consistency and allow eventual consistency elsewhere."),
    ("privacy", "analytics", "Data privacy vs broad analytics", "medium",
     "Detailed analytics can conflict with data-minimization and retention requirements.",
     "Anonymize analytics data and document retention and consent boundaries."),
]

CONFLICT_TAGS = {
    "security": ["security", "secure", "authentication", "encryption"],
    "low_latency": ["low latency", "response time", "real time", "real-time"],
    "low_cost": ["low cost", "affordable", "budget", "cheap"],
    "availability": ["high availability", "uptime", "always available", "fault tolerant"],
    "consistency": ["strong consistency", "strict consistency", "immediate consistency"],
    "geo_availability": ["multi region", "multi-region", "global availability", "region failure"],
    "privacy": ["privacy", "data minimization", "personal data", "gdpr"],
    "analytics": ["analytics", "tracking", "behavior data", "behaviour data"],
}


def style_scores(style):
    name = style.lower().replace("-", " ")
    match = next((key for key in STYLE_SCORES if key in name), None)
    return STYLE_SCORES.get(match, [6] * 7), match or "custom"


def detect_requirement_conflicts(requirement_set):
    tagged = {}
    for item in requirement_set.requirements:
        text = " ".join([item.quality_attribute, item.statement, *item.keywords]).lower()
        for tag, phrases in CONFLICT_TAGS.items():
            if any(phrase in text for phrase in phrases):
                tagged.setdefault(tag, []).append(item.id)

    conflicts = []
    for left, right, title, severity, explanation, resolution in CONFLICT_RULES:
        pairs = [(a, b) for a in tagged.get(left, []) for b in tagged.get(right, []) if a != b]
        if pairs:
            conflicts.append(RequirementConflict(
                id=f"CON-{len(conflicts) + 1:02d}", requirement_ids=list(pairs[0]),
                title=title, explanation=explanation, severity=severity, resolution=resolution,
            ))
    return ConflictReport(conflicts=conflicts)


def conflicts_markdown(report):
    if not report.conflicts:
        return "No rule-supported requirement conflicts were detected."
    lines = []
    for item in report.conflicts:
        lines += [f"### {item.id}: {item.title}",
                  f"**Requirements:** {' ↔ '.join(item.requirement_ids)}  ",
                  f"**Severity:** {item.severity.title()}  ", item.explanation,
                  f"\n**Suggested resolution:** {item.resolution}\n"]
    return "\n".join(lines)


def weights_for(requirements):
    weights = {name: 1.0 for name in CRITERIA}
    weights["requirement_fit"] = 2.0
    for item in requirements:
        if item.category != "non_functional":
            continue
        text = " ".join([item.quality_attribute, item.statement, *item.keywords]).lower()
        for criterion, words in ATTRIBUTE_ALIASES.items():
            if any(word in text for word in words):
                weights[criterion] += 1.0 if item.priority == "must" else 0.5
    return weights


def evaluate_architectures(requirement_set, options):
    requirement_ids = {item.id for item in requirement_set.requirements}
    weights = weights_for(requirement_set.requirements)
    evaluations = []

    for option in options:
        covered = {item for component in option.components for item in component.supports_requirements}
        covered |= {item for api in option.apis for item in api.supports_requirements}
        covered &= requirement_ids
        fit = round(10 * len(covered) / len(requirement_ids)) if requirement_ids else 10
        baselines, matched_style = style_scores(option.style)
        scores = [fit, *baselines]
        evidence = {name: [f"Style baseline: {matched_style}"] for name in CRITERIA[1:]}
        evidence["requirement_fit"] = [f"Covers {len(covered)} of {len(requirement_ids)} requirements"]

        for tactic in option.quality_tactics:
            text = f"{tactic.attribute} {tactic.tactic}".lower()
            for index, criterion in enumerate(CRITERIA[1:], start=1):
                words = [criterion, *ATTRIBUTE_ALIASES.get(criterion, [])]
                if any(word in text for word in words):
                    scores[index] = min(10, scores[index] + 1)
                    evidence[criterion].append(tactic.evidence)

        details = [CriterionScore(criterion=name, score=scores[index],
                                  weight=weights[name], evidence=evidence[name])
                   for index, name in enumerate(CRITERIA)]
        total = sum(item.score * item.weight for item in details) / sum(weights.values())
        evaluations.append(ArchitectureEvaluation(
            architecture_id=option.id, scores=details, weighted_total=round(total, 2),
            covered_requirements=sorted(covered),
            uncovered_requirements=sorted(requirement_ids - covered),
        ))

    winner = max(evaluations, key=lambda item: (item.weighted_total,
                 next(score.score for score in item.scores if score.criterion == "complexity")))
    reason = f"{winner.architecture_id} has the highest deterministic weighted score ({winner.weighted_total}/10)."
    return EvaluationResult(evaluations=evaluations,
                            selected_architecture_id=winner.architecture_id,
                            selection_reason=reason)


def evaluation_markdown(result):
    headings = ["Architecture", *[name.replace("_", " ").title() for name in CRITERIA], "Weighted"]
    lines = ["| " + " | ".join(headings) + " |", "| " + " | ".join(["---"] * len(headings)) + " |"]
    for item in result.evaluations:
        values = [item.architecture_id, *[str(score.score) for score in item.scores], str(item.weighted_total)]
        lines.append("| " + " | ".join(values) + " |")
    lines += ["\n**Selected architecture:** " + result.selected_architecture_id,
              result.selection_reason,
              "\n*Complexity scores are higher when an option is simpler to operate.*"]
    return "\n".join(lines)


def database_tokens(text):
    aliases = {"postgres": "postgresql", "mongo": "mongodb", "dynamo": "dynamodb"}
    known = ["postgresql", "mysql", "mongodb", "dynamodb", "sqlite", "firebase", "supabase"]
    value = text.lower()
    found = {name for name in known if name in value}
    found |= {canonical for alias, canonical in aliases.items() if alias in value}
    return found


def check_consistency(requirements, architecture, database, test_plan):
    requirement_ids = {item.id for item in requirements.requirements}
    component_ids = {item.id for item in architecture.components}
    api_ids = {item.id for item in architecture.apis}
    entity_ids = {item.id for item in database.entities}
    issues = []

    def add(severity, category, description, evidence, artifacts):
        issues.append(ConsistencyIssue(id=f"INC-{len(issues) + 1:02d}", severity=severity,
                                      category=category, description=description,
                                      evidence=evidence, affected_artifacts=artifacts))

    arch_db = database_tokens(architecture.database + " " + " ".join(architecture.technology_stack))
    design_db = database_tokens(database.engine)
    if arch_db and design_db and arch_db.isdisjoint(design_db):
        add("high", "database_mismatch", "Architecture and database agents selected different engines.",
            [f"Architecture: {', '.join(sorted(arch_db))}", f"Database design: {', '.join(sorted(design_db))}"],
            ["Architecture", "Database Design", "Technology Stack"])

    references = []
    references += [(f"Component {item.id}", ref) for item in architecture.components for ref in item.supports_requirements]
    references += [(f"API {item.id}", ref) for item in architecture.apis for ref in item.supports_requirements]
    references += [(f"Risk {item.id}", ref) for item in architecture.risks for ref in item.requirement_ids]
    references += [(f"Entity {item.id}", ref) for item in database.entities for ref in item.supports_requirements]
    references += [(f"Test {item.id}", ref) for item in test_plan.test_cases for ref in item.requirement_ids]
    invalid = [f"{source} -> {ref}" for source, ref in references if ref not in requirement_ids]
    if invalid:
        add("high", "invalid_requirement_reference", "Artifacts reference unknown requirements.",
            invalid, ["Requirements", "Architecture", "Database Design", "Testing"])

    invalid_api_components = [f"{item.id} -> {item.component_id}" for item in architecture.apis if item.component_id not in component_ids]
    invalid_relationships = [f"{item.source_entity_id} -> {item.target_entity_id}" for item in database.relationships
                             if item.source_entity_id not in entity_ids or item.target_entity_id not in entity_ids]
    invalid_tests = [item.id for item in test_plan.test_cases
                     if any(ref not in component_ids for ref in item.component_ids)
                     or any(ref not in api_ids for ref in item.api_ids)]
    invalid_risks = [item.id for item in architecture.risks
                     if any(ref not in component_ids for ref in item.component_ids)]
    if invalid_api_components or invalid_relationships or invalid_tests or invalid_risks:
        add("high", "broken_artifact_reference", "One or more artifact links point to missing IDs.",
            invalid_api_components + invalid_relationships + invalid_tests + invalid_risks,
            ["Architecture", "Database Design", "Testing"])

    tested = {ref for item in test_plan.test_cases for ref in item.requirement_ids}
    required = {item.id for item in requirements.requirements if item.priority == "must"}
    missing_tests = sorted(required - tested)
    if missing_tests:
        add("medium", "missing_test_coverage", "Must-have requirements are not covered by tests.",
            missing_tests, ["Requirements", "Testing", "Traceability"])

    penalties = {"high": 18, "medium": 8, "low": 3}
    score = max(0, 100 - sum(penalties[item.severity] for item in issues))
    status = "fail" if any(item.severity == "high" for item in issues) else "warning" if issues else "pass"
    return ConsistencyReport(status=status, score=score, issues=issues)


def consistency_markdown(report):
    lines = [f"**Status:** {report.status.upper()}  ", f"**Consistency score:** {report.score}%"]
    if not report.issues:
        return "\n".join(lines + ["\nNo cross-artifact inconsistencies were detected."])
    for item in report.issues:
        lines += [f"\n### {item.id}: {item.category.replace('_', ' ').title()}",
                  f"**Severity:** {item.severity.title()}  ", item.description,
                  "\nEvidence:", *[f"- {value}" for value in item.evidence],
                  f"\nAffected artifacts: {', '.join(item.affected_artifacts)}"]
    return "\n".join(lines)


def build_traceability(requirements, architecture, database, test_plan):
    nodes = []
    edges = []

    def node(identifier, node_type, label):
        nodes.append(TraceNode(id=identifier, node_type=node_type, label=label))

    def edge(source, target, relationship):
        edges.append(TraceEdge(source=source, target=target, relationship=relationship))

    for item in requirements.requirements:
        node(item.id, "requirement", item.statement)
    for item in requirements.user_stories:
        node(item.id, "user_story", f"{item.role}: {item.goal}")
        for requirement_id in item.requirement_ids:
            edge(requirement_id, item.id, "described_by")
    for item in architecture.components:
        node(item.id, "component", item.name)
        for requirement_id in item.supports_requirements:
            edge(requirement_id, item.id, "implemented_by")
    for item in architecture.apis:
        node(item.id, "api", f"{item.method} {item.path}")
        edge(item.component_id, item.id, "exposes")
        for requirement_id in item.supports_requirements:
            edge(requirement_id, item.id, "exposed_by")
    for item in database.entities:
        node(item.id, "database_entity", item.name)
        for requirement_id in item.supports_requirements:
            edge(requirement_id, item.id, "stored_in")
    for item in test_plan.test_cases:
        node(item.id, "test", item.title)
        for requirement_id in item.requirement_ids:
            edge(requirement_id, item.id, "verified_by")
    for item in architecture.risks:
        node(item.id, "risk", item.description)
        for requirement_id in item.requirement_ids:
            edge(requirement_id, item.id, "threatened_by")
        for component_id in item.component_ids:
            edge(component_id, item.id, "has_risk")

    covered_components = {item.source for item in edges if item.relationship == "implemented_by"}
    covered_tests = {item.source for item in edges if item.relationship == "verified_by"}
    requirement_ids = {item.id for item in requirements.requirements}
    uncovered = sorted(requirement_ids - (covered_components & covered_tests))
    coverage = round(100 * (len(requirement_ids) - len(uncovered)) / len(requirement_ids)) if requirement_ids else 100
    return TraceabilityGraph(nodes=nodes, edges=edges, coverage_percentage=coverage,
                             uncovered_requirements=uncovered)


def traceability_markdown(graph):
    lines = [f"**End-to-end coverage:** {graph.coverage_percentage}%  ",
             f"**Uncovered requirements:** {', '.join(graph.uncovered_requirements) or 'None'}",
             "\n```mermaid", "flowchart LR"]
    important = {"requirement", "component", "database_entity", "api", "test", "risk"}
    for item in graph.nodes:
        if item.node_type in important:
            safe_id = item.id.replace("-", "_")
            safe_label = item.label.replace('"', "'")[:45]
            lines.append(f'    {safe_id}["{item.id}: {safe_label}"]')
    node_ids = {item.id for item in graph.nodes if item.node_type in important}
    for item in graph.edges:
        if item.source in node_ids and item.target in node_ids:
            source = item.source.replace("-", "_")
            target = item.target.replace("-", "_")
            lines.append(f"    {source} -->|{item.relationship}| {target}")
    lines += ["```", "\n### Requirement Links"]
    for requirement in [item for item in graph.nodes if item.node_type == "requirement"]:
        targets = [item.target for item in graph.edges if item.source == requirement.id]
        lines.append(f"- **{requirement.id}:** {', '.join(targets) or 'No linked artifacts'}")
    return "\n".join(lines)


def architecture_changes(before, after):
    changes = []
    comparisons = [
        ("components", {item.name for item in before.components}, {item.name for item in after.components}),
        ("technologies", set(before.technology_stack), set(after.technology_stack)),
        ("quality tactics", {item.tactic for item in before.quality_tactics},
         {item.tactic for item in after.quality_tactics}),
        ("risks", {item.description for item in before.risks}, {item.description for item in after.risks}),
    ]
    for label, old, new in comparisons:
        if new - old:
            changes.append(f"Added {label}: {', '.join(sorted(new - old))}")
        if old - new:
            changes.append(f"Removed {label}: {', '.join(sorted(old - new))}")
    if before.database != after.database:
        changes.append(f"Changed database from {before.database} to {after.database}")
    return changes or ["Clarified the architecture without changing its major structure."]


def versions_markdown(versions):
    if not versions:
        return "No architecture versions were recorded."
    lines = ["| Version | Evaluation | Traceability | Consistency | Critical Risks | High Risks |",
             "| --- | --- | --- | --- | --- | --- |"]
    for item in versions:
        lines.append(f"| V{item.version} | {item.evaluation.weighted_total}/10 | "
                     f"{item.traceability_coverage}% | {item.consistency_score}% | "
                     f"{item.critical_risks} | {item.high_risks} |")
    if len(versions) > 1:
        lines += [f"\n### Changes in V{versions[-1].version}"]
        lines += [f"- {change}" for change in versions[-1].changes]
    else:
        lines += ["\nNo refinement was required after the first review."]
    return "\n".join(lines)


def analyze_change_impact(change_request, requirements, graph):
    stop_words = {"the", "and", "for", "with", "should", "now", "able", "using",
                  "from", "into", "that", "this", "have", "will", "user", "users"}

    def words(text):
        return {word for word in re.findall(r"[a-z0-9]+", text.lower())
                if len(word) > 2 and word not in stop_words}

    change_words = words(change_request)
    matches = []
    for item in requirements.requirements:
        source = words(" ".join([item.statement, item.quality_attribute, *item.keywords]))
        score = len(change_words & source)
        if score:
            matches.append((score, item.id))
    affected_requirements = [identifier for _, identifier in sorted(matches, reverse=True)]

    node_types = {item.id: item.node_type for item in graph.nodes}
    reached = set(affected_requirements)
    frontier = list(affected_requirements)
    while frontier:
        current = frontier.pop(0)
        for edge in [item for item in graph.edges if item.source == current]:
            if edge.target not in reached:
                reached.add(edge.target)
                frontier.append(edge.target)

    def ids(node_type):
        return sorted(item for item in reached if node_types.get(item) == node_type)

    components = ids("component")
    apis = ids("api")
    entities = ids("database_entity")
    tests = ids("test")
    risks = ids("risk")
    size = len(components) + len(apis) + len(entities) + len(tests)
    level = "none" if not affected_requirements else "high" if size >= 8 else "medium" if size >= 4 else "low"
    suggestions = [f"Re-run {test_id} after implementing the change." for test_id in tests]
    if affected_requirements and not tests:
        suggestions.append("Add regression tests for the affected requirements.")
    return ImpactResult(
        change_request=change_request, affected_requirements=affected_requirements,
        affected_components=components, affected_apis=apis,
        affected_database_entities=entities, affected_tests=tests,
        affected_risks=risks, impact_level=level,
        regression_suggestions=suggestions,
    )


def impact_markdown(result):
    rows = [
        ("Requirements", result.affected_requirements),
        ("Components", result.affected_components),
        ("APIs", result.affected_apis),
        ("Database entities", result.affected_database_entities),
        ("Tests", result.affected_tests),
        ("Risks", result.affected_risks),
    ]
    lines = ["### Change Request", result.change_request,
             f"\n**Architecture impact:** {result.impact_level.title()}",
             "\n| Artifact | Count | Affected IDs |", "| --- | --- | --- |"]
    lines += [f"| {label} | {len(values)} | {', '.join(values) or 'None'} |" for label, values in rows]
    lines += ["\n### Regression Suggestions"]
    lines += [f"- {item}" for item in result.regression_suggestions] or ["- No regression tests identified."]
    lines += ["\n*This is rule-based architectural impact analysis, not a production change prediction.*"]
    return "\n".join(lines)
