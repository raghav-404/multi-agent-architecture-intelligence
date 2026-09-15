from prompts import TRACEABILITY_PROMPT
from utils import ask_groq


def traceability_agent(text):
    return ask_groq(TRACEABILITY_PROMPT, text)
