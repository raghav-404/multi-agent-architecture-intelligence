def planner_agent(project, requirements=None):
    ids = [item["id"] for item in (requirements or {}).get("requirements", [])]
    scope = ", ".join(ids) or "the approved requirements"
    return f"""### Work Breakdown Structure
1. Confirm scope and acceptance criteria for {scope}.
2. Design the selected architecture, APIs, and database.
3. Implement the core user workflow and integrations.
4. Test, review, document, and demonstrate the system.

### Milestones
- **M1:** Requirements and architecture approved
- **M2:** Core workflow and database complete
- **M3:** Testing, review, and final demonstration complete

### Sprint Plan
- **Sprint 1:** Requirements, UI flow, architecture, and database
- **Sprint 2:** Core implementation and API integration
- **Sprint 3:** Testing, fixes, documentation, and presentation"""
