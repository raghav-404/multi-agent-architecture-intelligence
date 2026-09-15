from prompts import REFINE_PROMPT
from utils import ask_groq


def refine_agent(text):
    return ask_groq(REFINE_PROMPT, text)
