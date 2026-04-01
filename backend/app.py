import os
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from dotenv import load_dotenv
from db.mongo import connect_mongo, close_mongo
from db.influx import connect_influx, close_influx
from routes.session import router as session_router
from routes.events import router as events_router

load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="Analytics Backend", version="1.0.0")

# CORS middleware — allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base directories
base_dir = Path(__file__).parent
public_dir = base_dir / "public"
demo_dir = base_dir.parent / "demo-site"
dashboard_dir = base_dir.parent / "dashboard"

# Mount static file directories
app.mount("/dashboard", StaticFiles(directory=str(dashboard_dir), html=True), name="dashboard")
app.mount("/demo", StaticFiles(directory=str(demo_dir), html=True), name="demo")
app.mount("/public", StaticFiles(directory=str(public_dir)), name="public")

# Serve tracker.js directly
@app.get("/tracker.js")
async def get_tracker():
    tracker_path = public_dir / "tracker.js"
    if tracker_path.exists():
        return FileResponse(tracker_path, media_type="application/javascript")
    return JSONResponse({"error": "tracker.js not found"}, status_code=404)

# Routes
app.include_router(session_router)
app.include_router(events_router)

# Health check
@app.get("/health")
async def health():
    return {"status": "ok"}

# Startup event
@app.on_event("startup")
async def startup():
    try:
        connect_mongo()
        connect_influx()
        PORT = os.getenv("PORT", "3000")
        print(f"🚀 Analytics backend running at http://localhost:{PORT}")
        print(f"   tracker.js  → http://localhost:{PORT}/tracker.js")
        print(f"   demo site   → http://localhost:{PORT}/demo")
        print(f"   dashboard   → http://localhost:{PORT}/dashboard")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise

# Shutdown event
@app.on_event("shutdown")
async def shutdown():
    close_mongo()
    close_influx()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 3000))
    uvicorn.run(app, host="0.0.0.0", port=port)
