import json

from models import ArchitectureOption, ArchitectureSet
from prompts import ARCHITECT_PROMPT, ARCHITECT_REFINE_PROMPT
from utils import ask_groq_json


def architect_agent(project, requirements, option_count):
    styles = ["modular monolith", "serverless", "service-based architecture"]
    options = []
    for index in range(option_count):
        text = f"{project}\nCreate alternative A{index + 1} of {option_count}. "
        text += f"Prefer {styles[index]} when suitable, while remaining domain-specific.\n"
        text += "Use 3-5 components, up to 5 APIs, up to 5 tactics, and up to 3 risks.\n"
        text += "Requirements:\n" + json.dumps(requirements)
        option = ask_groq_json(ARCHITECT_PROMPT, text, ArchitectureOption, 3500)
        options.append(normalize_ids(option, index + 1))
    return ArchitectureSet(options=options)


def normalize_ids(option, number):
    option.id = f"A{number}"
    component_ids = {}
    for index, component in enumerate(option.components, 1):
        new_id = f"A{number}-C{index}"
        component_ids[component.id] = new_id
        component.id = new_id
    for index, api in enumerate(option.apis, 1):
        api.id = f"A{number}-API{index}"
        api.component_id = component_ids.get(api.component_id, api.component_id)
    for index, risk in enumerate(option.risks, 1):
        risk.id = f"A{number}-RISK{index}"
        risk.component_ids = [component_ids.get(item, item) for item in risk.component_ids]
    return option


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


def refine_architecture(context, current):
    result = ask_groq_json(ARCHITECT_REFINE_PROMPT, context, type(current), 3000)
    number = int(current.id.removeprefix("A"))
    return normalize_ids(result, number)
