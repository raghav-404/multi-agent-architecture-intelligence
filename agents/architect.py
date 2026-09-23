import json

from models import ArchitectureOption, ArchitectureSet, QualityTactic
from prompts import ARCHITECT_PROMPT, ARCHITECT_REFINE_PROMPT
from utils import ask_groq_json


def architect_agent(project, requirements, option_count):
    brief = [{key: item[key] for key in ["id", "statement", "priority", "quality_attribute"]}
             for item in requirements["requirements"]]
    text = f"{project}\nCreate A1 as a domain-specific modular monolith.\n"
    text += "Use 3-4 components, up to 4 APIs, 3 tactics, and up to 2 risks.\n"
    text += "Requirements:\n" + json.dumps(brief)
    primary = ask_groq_json(ARCHITECT_PROMPT, text, ArchitectureOption, 1700)
    options = [normalize_ids(primary, 1)]
    if option_count > 1:
        options.append(serverless_alternative(primary))
    return ArchitectureSet(options=options)


def serverless_alternative(primary):
    option = primary.model_copy(deep=True)
    option.name = "Managed Serverless Alternative"
    option.style = "serverless"
    option.summary = "The same domain responsibilities run as managed functions and services."
    for component in option.components:
        component.communication = "HTTPS and managed events"
    option.technology_stack = ["Managed functions", "API Gateway", primary.database,
                               "Managed authentication"]
    option.quality_tactics.append(QualityTactic(
        attribute="scalability", tactic="automatic function scaling",
        evidence="Managed functions scale independently with demand."))
    option.advantages = ["Low operational work", "Automatic scaling", "Usage-based cost"]
    option.disadvantages = ["Vendor dependency", "Cold-start latency", "Harder local testing"]
    return normalize_ids(option, 2)


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
    result = ask_groq_json(ARCHITECT_REFINE_PROMPT, context, type(current), 1800)
    number = int(current.id.removeprefix("A"))
    return normalize_ids(result, number)
