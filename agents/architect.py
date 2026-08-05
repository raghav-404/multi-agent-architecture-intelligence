from prompts import ARCHITECT_PROMPT
from utils import ask_groq


def architect_agent(project):
    return ask_groq(ARCHITECT_PROMPT, project)
