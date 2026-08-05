import json
import os
from io import BytesIO

from dotenv import load_dotenv
from groq import Groq
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


load_dotenv()


def ask_groq(prompt, text):
    """Send one simple prompt to Groq and return markdown text."""
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text},
        ],
        temperature=0.3,
        max_tokens=700,
    )
    return response.choices[0].message.content


def save_history(project, report):
    """Append the result to history.json."""
    path = "history.json"
    history = []

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as file:
            history = json.load(file)

    history.append({"project": project, "report": report})

    with open(path, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=2)


def make_pdf(text):
    """Create a simple PDF from markdown text."""
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    height = letter[1]
    x, y = 50, height - 50

    for line in text.splitlines():
        if y < 50:
            pdf.showPage()
            y = height - 50

        if line.startswith("#"):
            pdf.setFont("Helvetica-Bold", 12)
            line = line.replace("#", "").strip()
        else:
            pdf.setFont("Helvetica", 10)

        while len(line) > 95:
            pdf.drawString(x, y, line[:95])
            line = line[95:]
            y -= 14
        pdf.drawString(x, y, line)
        y -= 16

    pdf.save()
    buffer.seek(0)
    return buffer.read()
