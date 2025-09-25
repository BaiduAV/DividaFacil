from fastapi import FastAPI
from fastapi.responses import FileResponse
import os

app = FastAPI()

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/app")
async def serve_react_app():
    index_path = "frontend/build/index.html"
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    return {"error": "React app not found"}

@app.get("/app/{full_path:path}")
async def serve_react_assets(full_path: str):
    file_path = os.path.join("frontend/build", full_path)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "Asset not found"}