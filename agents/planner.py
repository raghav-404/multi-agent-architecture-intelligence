from prompts import PLANNER_PROMPT
from utils import ask_groq


def planner_agent(project):
    return ask_groq(PLANNER_PROMPT, project)
