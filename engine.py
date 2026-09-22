from models import ArchitectureEvaluation, CriterionScore, EvaluationResult


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


def style_scores(style):
    name = style.lower().replace("-", " ")
    match = next((key for key in STYLE_SCORES if key in name), None)
    return STYLE_SCORES.get(match, [6] * 7), match or "custom"


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
