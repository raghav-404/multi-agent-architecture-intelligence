from fastapi import FastAPI, Response
from pydantic import BaseModel

from utils import save_history
from workflow import run_workflow


app = FastAPI()


class AnalyzeRequest(BaseModel):
    project: str


@app.post("/analyze")
def analyze(data: AnalyzeRequest):
    report = run_workflow(data.project)
    save_history(data.project, report)
    return Response(content=report, media_type="text/markdown")
