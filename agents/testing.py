from prompts import TESTING_PROMPT
from utils import ask_groq


def testing_agent(text):
    return ask_groq(TESTING_PROMPT, text)
