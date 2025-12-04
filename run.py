"""Simple script to run the localisation engine."""
import uvicorn
import os
from pathlib import Path

# Set default environment variables
os.environ.setdefault("STORAGE_ROOT", str(Path(__file__).parent / "storage"))
os.environ.setdefault("DATABASE_URL", "sqlite:///./localisation_engine.db")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )



