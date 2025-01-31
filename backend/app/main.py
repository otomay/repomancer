from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from app.services.clone_repo import clone_repository
from app.services.context_analysis import analyze_context
from app.services.code_scanner import scan_code
from pydantic import BaseModel
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    repository_url: str

progress_updates = {}

@app.post("/api/analyze")
async def analyze_repository(request: AnalyzeRequest):
    try:
        repo_path = clone_repository(request.repository_url)
        context = analyze_context(repo_path)
        
        async def progress_callback(progress):
            progress_updates[request.repository_url] = progress

        results = await scan_code(repo_path, context, progress_callback)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        progress_updates[request.repository_url] = 0

@app.get("/api/progress")
async def get_progress(repo_url: str):
    async def event_stream():
        while True:
            progress = progress_updates.get(repo_url, 0)
            yield f"data: {progress}\n\n"
            await asyncio.sleep(2)
            if progress >= 100:
                break

    return StreamingResponse(event_stream(), media_type="text/event-stream")

try:
    app.mount("/", StaticFiles(directory="../frontend/build", html=True), name="static")
except:
    pass