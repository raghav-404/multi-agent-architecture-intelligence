from prompts import FEEDBACK_PROMPT
from utils import ask_groq


def feedback_agent(text):
    return ask_groq(FEEDBACK_PROMPT, text)
