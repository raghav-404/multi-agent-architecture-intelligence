from models import RedTeamReview
from prompts import RED_TEAM_PROMPT
from utils import ask_groq_json


def red_team_agent(text):
    return ask_groq_json(RED_TEAM_PROMPT, text, RedTeamReview, 2200)


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
