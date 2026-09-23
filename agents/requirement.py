from prompts import REQUIREMENT_PROMPT
from models import RequirementSet
from utils import ask_groq_json


def requirement_agent(project):
    return ask_groq_json(REQUIREMENT_PROMPT, project, RequirementSet, 1400)


def requirements_markdown(data):
    lines = [f"{data.summary}\n", "### Functional Requirements"]
    functional = [item for item in data.requirements if item.category == "functional"]
    non_functional = [item for item in data.requirements if item.category == "non_functional"]
    lines += [f"- **{item.id} ({item.priority.title()})**: {item.statement}" for item in functional]
    lines += ["\n### Non-functional Requirements"]
    lines += [f"- **{item.id} ({item.quality_attribute})**: {item.statement}" for item in non_functional]
    lines += ["\n### User Stories"]
    lines += [f"- **{story.id}**: As a {story.role}, I want {story.goal}, so that {story.benefit}." for story in data.user_stories]
    lines += ["\n### Assumptions"] + [f"- {item}" for item in data.assumptions]
    return "\n".join(lines)
