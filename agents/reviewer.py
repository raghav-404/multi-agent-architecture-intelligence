def reviewer_agent(report):
    expected = ["## Requirements", "## Architecture Debate", "## Database Design", "## Test Plan"]
    complete = sum(section in report for section in expected)
    score = 6 + complete
    return f"""### Completeness Score: {score}/10

The report contains {complete} of {len(expected)} core engineering sections.

### Suggestions
- Confirm inferred requirements with the project stakeholder.
- Validate architecture assumptions with a small prototype.
- Keep traceability and tests updated when requirements change.

### Final Summary
The report is suitable for an initial software architecture review."""
