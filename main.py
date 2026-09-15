import os
import re

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

from agents.refine import refine_agent
from utils import load_history, make_pdf, register_user, save_history, verify_user
from workflow import run_workflow


app = FastAPI()
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "change-this-before-deploy"),
    same_site="lax",
    https_only=os.getenv("COOKIE_SECURE", "false").lower() == "true",
)
app.mount("/static", StaticFiles(directory="static"), name="static")


class AnalyzeRequest(BaseModel):
    project: str
    project_type: str = "General"
    depth: str = "Short"
    context: str = ""


class PdfRequest(BaseModel):
    report: str


class Credentials(BaseModel):
    username: str
    password: str


class RefineRequest(BaseModel):
    project: str
    section: str
    current_text: str
    instruction: str


def current_user(request):
    username = request.session.get("user")
    if not username:
        raise HTTPException(status_code=401, detail="Please sign in first.")
    return username


def check_credentials(data):
    username = data.username.strip().lower()
    if not re.fullmatch(r"[a-z0-9_]{3,30}", username):
        raise ValueError("Use 3-30 letters, numbers, or underscores for the username.")
    if len(data.password) < 6:
        raise ValueError("Password must have at least 6 characters.")
    return username


@app.get("/")
def home():
    return FileResponse("static/index.html")


@app.get("/me")
def me(request: Request):
    return {"username": request.session.get("user")}


@app.post("/register")
def register(data: Credentials, request: Request):
    try:
        username = check_credentials(data)
        register_user(username, data.password)
        request.session["user"] = username
        return {"username": username}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/login")
def login(data: Credentials, request: Request):
    username = data.username.strip().lower()
    if not verify_user(username, data.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password.")
    request.session["user"] = username
    return {"username": username}


@app.post("/logout")
def logout(request: Request):
    request.session.clear()
    return {"ok": True}


@app.post("/analyze")
def analyze(data: AnalyzeRequest, request: Request):
    username = current_user(request)
    if len(data.project.strip()) < 5:
        raise HTTPException(status_code=400, detail="Please enter a longer project idea.")

    try:
        result = run_workflow(data.project, data.project_type, data.depth, data.context)
        save_history(username, data.project, result["report"])
        return result
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Groq request failed: {error}") from error


@app.post("/refine")
def refine(data: RefineRequest, request: Request):
    current_user(request)
    if len(data.instruction.strip()) < 3:
        raise HTTPException(status_code=400, detail="Please enter a clearer update request.")
    text = f"Project: {data.project[:1000]}\nSection: {data.section}\n"
    text += f"Current section:\n{data.current_text[:5000]}\nRequest: {data.instruction[:600]}"
    try:
        return {"text": refine_agent(text)}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Groq request failed: {error}") from error


@app.get("/history")
def history(request: Request):
    return load_history(current_user(request))


@app.post("/pdf")
def pdf(data: PdfRequest, request: Request):
    current_user(request)
    return Response(make_pdf(data.report), media_type="application/pdf")
