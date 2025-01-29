from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from app.services.clone_repo import clone_repository
from app.services.context_analysis import analyze_context
from app.services.code_scanner import scan_code
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

expose_backend = os.getenv("EXPOSE_BACKEND", "false").lower() == "true"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    repository_url: str

if expose_backend:
    @app.post("/api/analyze")
    async def analyze_repository(request: AnalyzeRequest):
        try:
            repo_path = clone_repository(request.repository_url)
            context = analyze_context(repo_path)
            results = await scan_code(repo_path, context)
            return results
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/progress")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        async def progress_callback(progress):
            await websocket.send_json({"progress": progress})

        repo_url = await websocket.receive_text()
        repo_path = clone_repository(repo_url)
        context = analyze_context(repo_path)
        results = await scan_code(repo_path, context, progress_callback)
        
        await websocket.send_json(results)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        error_message = {"error": str(e)}
        await websocket.send_json(error_message)
    finally:
        await websocket.close()

try:
    app.mount("/", StaticFiles(directory="../frontend/build", html=True), name="static")
except:
    pass