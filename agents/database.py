from prompts import DATABASE_PROMPT
from utils import ask_groq


def database_agent(project):
    return ask_groq(DATABASE_PROMPT, project)
