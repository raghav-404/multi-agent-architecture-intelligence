import json

from models import RedTeamFinding, RedTeamReview


def red_team_agent(text):
    data = json.loads(text)
    findings = []
    for index, risk in enumerate(data["architecture"]["risks"], 1):
        description = risk["description"]
        severe = any(word in description.lower() for word in ["security", "data loss", "payment", "auth"])
        findings.append(RedTeamFinding(
            id=f"RT-{index:02d}", severity="high" if severe else "medium",
            title=f"Architecture risk {risk['id']}", description=description,
            evidence=risk["id"], affected_artifact_ids=risk["component_ids"],
            recommendation="Add a measurable mitigation and verify it with a failure test.",
        ))
    summary = f"Deterministic review found {len(findings)} documented architecture risk(s)."
    return RedTeamReview(summary=summary, findings=findings)


def red_team_markdown(review):
    counts = {level: 0 for level in ["critical", "high", "medium", "low"]}
    for item in review.findings:
        counts[item.severity] += 1
    lines = [review.summary, "", "| Critical | High | Medium | Low |",
             "| --- | --- | --- | --- |",
             f"| {counts['critical']} | {counts['high']} | {counts['medium']} | {counts['low']} |"]
    for item in review.findings:
        lines += [f"\n### {item.id}: {item.title}", f"**Severity:** {item.severity.title()}  ",
                  item.description, f"\n**Evidence:** {item.evidence}",
                  f"\n**Affected IDs:** {', '.join(item.affected_artifact_ids) or 'Architecture-wide'}",
                  f"\n**Recommendation:** {item.recommendation}"]
    return "\n".join(lines)
