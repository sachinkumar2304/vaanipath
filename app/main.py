"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import logging
import os

from app.routes import upload, play, status
from app.db.database import init_db
from app.utils.storage import init_storage_directories

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Localisation Engine",
    description="Multilingual video localization engine with on-demand TTS and dubbing",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database and storage
@app.on_event("startup")
async def startup_event():
    """Initialize database and storage on startup."""
    logger.info("Initializing application...")
    
    # Initialize database
    init_db()
    logger.info("Database initialized")
    
    # Initialize storage directories
    init_storage_directories()
    logger.info("Storage directories initialized")
    
    # Mount static files for serving generated files
    storage_root = Path(os.getenv("STORAGE_ROOT", "storage"))
    if storage_root.exists():
        app.mount("/storage", StaticFiles(directory=str(storage_root)), name="storage")
        logger.info(f"Static files mounted at /storage")


# Include routers
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(play.router, prefix="/api", tags=["play"])
app.include_router(status.router, prefix="/api", tags=["status"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Localisation Engine API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/api/upload",
            "play": "/api/play/{job_id}/{lang}",
            "status": "/api/status/{job_id}"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



