from models import DatabaseDesign
from prompts import DATABASE_PROMPT
from utils import ask_groq_json


def database_agent(project):
    return ask_groq_json(DATABASE_PROMPT, project, DatabaseDesign, 3500)


def database_markdown(data):
    lines = [f"**Engine:** {data.engine}\n", data.rationale]
    for entity in data.entities:
        lines += [f"\n### {entity.id}: {entity.name}", entity.purpose,
                  "| Field | Type | Constraints |", "| --- | --- | --- |"]
        lines += [f"| {field.name} | {field.data_type} | {', '.join(field.constraints) or 'None'} |" for field in entity.fields]
        lines.append(f"\nSupports: {', '.join(entity.supports_requirements) or 'None'}")
    lines += ["\n### Relationships"]
    lines += [f"- {item.source_entity_id} → {item.target_entity_id}: {item.relationship}" for item in data.relationships]
    lines += ["\n### Database Risks"] + [f"- {item}" for item in data.risks]
    return "\n".join(lines)
