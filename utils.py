import json
import os
import hashlib
import secrets
from io import BytesIO
from html import escape

from dotenv import load_dotenv
from groq import Groq
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer


load_dotenv()


def ask_groq(prompt, text):
    """Send one simple prompt to Groq and return markdown text."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        raise ValueError("Missing Groq API key. Add GROQ_API_KEY to your .env file.")

    client = Groq(api_key=api_key)
    model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text},
        ],
        temperature=0.3,
        max_tokens=350,
    )
    return response.choices[0].message.content


def read_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def password_hash(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return f"{salt}${digest.hex()}"


def register_user(username, password):
    users = read_json("users.json", {})
    if username in users:
        raise ValueError("That username is already in use.")
    users[username] = password_hash(password)
    write_json("users.json", users)


def verify_user(username, password):
    saved = read_json("users.json", {}).get(username, "")
    if not saved or "$" not in saved:
        return False
    salt, _ = saved.split("$", 1)
    return secrets.compare_digest(saved, password_hash(password, salt))


def save_history(username, project, report):
    history = read_json("history.json", [])
    history.append({"username": username, "project": project, "report": report})
    write_json("history.json", history)


def load_history(username):
    history = read_json("history.json", [])
    return [item for item in history if item.get("username") == username]


def make_pdf(text):
    """Create a simple PDF from markdown text with basic formatting."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    first_heading = True

    for line in text.splitlines():
        clean = escape(line.replace("*", "").strip())
        if not clean:
            story.append(Spacer(1, 8))
        elif line.startswith("# "):
            if not first_heading:
                story.append(PageBreak())
            story.append(Paragraph(clean.replace("#", "").strip(), styles["Title"]))
            first_heading = False
        elif line.startswith("## "):
            story.append(Spacer(1, 10))
            story.append(Paragraph(clean.replace("#", "").strip(), styles["Heading2"]))
        else:
            story.append(Paragraph(clean, styles["BodyText"]))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
