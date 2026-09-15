from prompts import CLARIFICATION_PROMPT
from utils import ask_groq


def clarification_agent(project):
    return ask_groq(CLARIFICATION_PROMPT, project)
