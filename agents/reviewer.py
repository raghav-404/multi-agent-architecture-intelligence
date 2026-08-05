from prompts import REVIEWER_PROMPT
from utils import ask_groq


def reviewer_agent(report):
    return ask_groq(REVIEWER_PROMPT, report)
