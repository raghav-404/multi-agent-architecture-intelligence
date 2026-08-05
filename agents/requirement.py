from prompts import REQUIREMENT_PROMPT
from utils import ask_groq


def requirement_agent(project):
    return ask_groq(REQUIREMENT_PROMPT, project)
