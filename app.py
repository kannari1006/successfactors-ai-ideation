import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import json
import os
from ai_worker import run_ai_simulation

# Background task reference
bg_task = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global bg_task
    # Start the AI Simulation loop in the background
    bg_task = asyncio.create_task(run_ai_simulation())
    yield
    # Cleanup
    if bg_task:
        bg_task.cancel()

app = FastAPI(lifespan=lifespan)

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    from fastapi.responses import FileResponse
    return FileResponse("static/index.html")

@app.get("/api/ideas")
def get_ideas():
    try:
        if not os.path.exists("ideas.json"):
            return JSONResponse([])
        with open("ideas.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        # return sorted by updated_at descending natively
        data.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return JSONResponse(data)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/check_updates")
def check_updates(last_timestamp: str):
    """
    Returns {"has_updates": True/False} based on whether any idea in ideas.json
    has an updated_at > last_timestamp.
    """
    try:
        if not os.path.exists("ideas.json"):
            return JSONResponse({"has_updates": False})
        with open("ideas.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            
        for idea in data:
            if idea.get("updated_at", "") > last_timestamp:
                return JSONResponse({"has_updates": True})
                
        return JSONResponse({"has_updates": False})
    except Exception as e:
        return JSONResponse({"has_updates": False})

@app.get("/api/events")
def get_events():
    """
    Returns the latest event history logs.
    """
    try:
        if not os.path.exists("events.json"):
            return JSONResponse([])
        with open("events.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return JSONResponse(data)
    except Exception as e:
        return JSONResponse([])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
