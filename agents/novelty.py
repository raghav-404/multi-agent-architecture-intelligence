from prompts import NOVELTY_PROMPT
from utils import ask_groq


def novelty_agent(text):
    return ask_groq(NOVELTY_PROMPT, text)
