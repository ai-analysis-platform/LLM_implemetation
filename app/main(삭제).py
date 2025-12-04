import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from .workflow import build_workflow
from typing import Dict
import shutil
import uuid

app = FastAPI(title="LLM Report Generator")

WF = build_workflow()

TMP = os.path.join(os.path.dirname(__file__), "..", "tmp")
os.makedirs(TMP, exist_ok=True)

# 작업 저장소 (in-memory simple)
JOBS: Dict[str, Dict] = {}

@app.post("/generate")
async def generate_report(user_query: str = Form(...), file: UploadFile = File(...)):
    # 1) 파일 저장
    ext = os.path.splitext(file.filename)[1]
    file_id = uuid.uuid4().hex
    save_path = os.path.join(TMP, f"{file_id}{ext}")
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    job_id = uuid.uuid4().hex
    JOBS[job_id] = {"status": "queued", "output": None}

    # 2) 워크플로 실행 (동기 방식 — 필요하면 백그라운드 작업으로 바꿀 것)
    try:
        init_state = {
            "user_query": user_query,
            "csv_path": save_path,
            "df": None,
            "eda_summary": "",
            "charts": [],
            "insights": "",
            "report_md": "",
            "report_path": ""
        }
        JOBS[job_id]["status"] = "running"
        result_state = WF.invoke(init_state)
        JOBS[job_id]["status"] = "done"
        JOBS[job_id]["output"] = result_state
    except Exception as e:
        JOBS[job_id]["status"] = "error"
        JOBS[job_id]["error"] = str(e)
        raise HTTPException(status_code=500, detail=str(e))

    return {"job_id": job_id, "status": JOBS[job_id]["status"]}

@app.get("/status/{job_id}")
def job_status(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    return job

@app.get("/download/{job_id}")
def download_report(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    if job["status"] != "done":
        raise HTTPException(status_code=400, detail="job not completed")
    rp = job["output"]["report_path"]
    return FileResponse(rp, filename=os.path.basename(rp))