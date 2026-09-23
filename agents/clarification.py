def clarification_agent(project):
    return """### Scope Interpretation
- Treat the submitted idea as a semester-project MVP.
- Include the main user workflow, supporting data, APIs, and quality needs.

### Working Assumptions
- Requirements inferred from the idea should be confirmed with stakeholders.
- Authentication, validation, logging, and error handling are baseline concerns.
- Deployment details remain recommendations until real usage targets are known."""
