import json

from models import ArchitectureSet
from prompts import ARCHITECT_PROMPT
from utils import ask_groq_json


def architect_agent(project, requirements, option_count):
    text = f"{project}\nGenerate exactly {option_count} alternatives.\n"
    text += "Requirements:\n" + json.dumps(requirements, indent=2)
    result = ask_groq_json(ARCHITECT_PROMPT, text, ArchitectureSet, 2600)
    if len(result.options) != option_count:
        raise ValueError(f"Groq returned {len(result.options)} architecture options; expected {option_count}.")
    return result


def architecture_markdown(data):
    lines = ["The following alternatives are candidates; selection is performed by the evaluation engine."]
    for option in data.options:
        lines += [f"\n### {option.id}: {option.name}", f"**Style:** {option.style}\n", option.summary]
        lines += ["\n**Components**"] + [f"- **{item.name}:** {item.responsibility} Communication: {item.communication}." for item in option.components]
        lines += [f"\n**Database:** {option.database}", f"\n**Technology stack:** {', '.join(option.technology_stack)}"]
        lines += ["\n**Advantages**"] + [f"- {item}" for item in option.advantages]
        lines += ["\n**Disadvantages**"] + [f"- {item}" for item in option.disadvantages]
        lines += ["\n**Risks**"] + [f"- **{item.id}:** {item.description}" for item in option.risks]
    return "\n".join(lines)
