import json
import os
import hashlib
import secrets
import uuid
from datetime import datetime, timezone
from io import BytesIO
from html import escape

from dotenv import load_dotenv
from groq import Groq
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer


load_dotenv()
DATA_DIR = "/tmp" if os.getenv("VERCEL") else "."


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


def ask_groq_json(prompt, text, schema, max_tokens=1800):
    """Ask Groq for JSON and validate it with a Pydantic model."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        raise ValueError("Missing Groq API key. Add GROQ_API_KEY to your .env file.")

    client = Groq(api_key=api_key)
    model = os.getenv("GROQ_STRUCTURED_MODEL", "openai/gpt-oss-20b")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text},
        ],
        temperature=0.2,
        max_completion_tokens=max_tokens,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": schema.__name__.lower(),
                "strict": True,
                "schema": schema.model_json_schema(),
            },
        },
    )
    return schema.model_validate_json(response.choices[0].message.content)


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
    users = read_json(os.path.join(DATA_DIR, "users.json"), {})
    if username in users:
        raise ValueError("That username is already in use.")
    users[username] = password_hash(password)
    write_json(os.path.join(DATA_DIR, "users.json"), users)


def verify_user(username, password):
    saved = read_json(os.path.join(DATA_DIR, "users.json"), {}).get(username, "")
    if not saved or "$" not in saved:
        return False
    salt, _ = saved.split("$", 1)
    return secrets.compare_digest(saved, password_hash(password, salt))


def save_history(username, project, result):
    path = os.path.join(DATA_DIR, "history.json")
    history = read_json(path, [])
    analysis_id = uuid.uuid4().hex[:12]
    stored_result = {**result, "analysis_id": analysis_id}
    history.append({
        "id": analysis_id, "username": username, "project": project,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "report": result["report"], "result": stored_result,
    })
    write_json(path, history)
    return analysis_id


def load_history(username):
    history = read_json(os.path.join(DATA_DIR, "history.json"), [])
    items = [item for item in history if item.get("username") == username]
    for item in items:
        item.setdefault("id", "")
        item.setdefault("result", {"report": item.get("report", "")})
    return items


def get_history_item(username, analysis_id):
    return next((item for item in load_history(username) if item["id"] == analysis_id), None)


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
