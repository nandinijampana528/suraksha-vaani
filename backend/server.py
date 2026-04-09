import os
import sys
import json
import uuid
import subprocess
import asyncio
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

import asyncio
import sys

# Fix for Windows asyncio subprocess
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

os.environ["NO_PROXY"] = "localhost,127.0.0.1"
os.environ["no_proxy"] = "localhost,127.0.0.1"

BASE_DIR   = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

app = FastAPI(
    title="SurakshaVaani API",
    description="AI-powered safety story narration for thermal power plants",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve audio output files
app.mount("/outputs", StaticFiles(directory=str(OUTPUT_DIR)), name="outputs")

# Serve frontend
FRONTEND_DIR = BASE_DIR / "frontend"
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


class StoryRequest(BaseModel):
    rule: str
    plant_name: str = "PowerPlant"


class StoryResponse(BaseModel):
    story_en: str
    story_hi: str
    audio_url: str


@app.get("/")
async def root():
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.post("/api/generate", response_model=StoryResponse)
async def generate(request: StoryRequest):
    if not request.rule.strip():
        raise HTTPException(status_code=400, detail="Safety rule cannot be empty.")

    pipeline_script = str(BASE_DIR / "backend" / "pipeline.py")

    def run_pipeline():
        result = subprocess.run(
            [sys.executable, pipeline_script, request.rule],
            capture_output=True,
            env={**os.environ, "PLANT_NAME": request.plant_name},
            timeout=300
        )
        return result

    try:
        import concurrent.futures
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            result = await loop.run_in_executor(pool, run_pipeline)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

    if result.returncode != 0:
        err = result.stderr.decode("utf-8", errors="ignore")
        raise HTTPException(status_code=500, detail=f"Pipeline error: {err[-500:]}")

    try:
        output = json.loads(result.stdout.decode("utf-8", errors="ignore"))
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse pipeline output.")

    if "error" in output:
        raise HTTPException(status_code=500, detail=output["error"])

    audio_filename = Path(output["audio_file"]).name
    return StoryResponse(
        story_en=output["story_en"],
        story_hi=output["story_hi"],
        audio_url=f"/outputs/{audio_filename}",
    )


@app.get("/health")
async def health():
    return {"status": "ok", "service": "SurakshaVaani"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
