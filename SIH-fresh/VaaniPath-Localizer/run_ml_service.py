"""
ML Service Runner - Wrapper script to start the Localizer API
"""
import sys
import os

# Add parent directory to Python path to resolve relative imports
sys.path.insert(0, os.path.dirname(__file__))

import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Starting VaaniPath ML Localizer Service")
    print("=" * 60)
    print(f"📍 Service URL: http://localhost:8001")
    print(f"📚 API Docs: http://localhost:8001/docs")
    print(f"🔧 Python Path: {sys.path[0]}")
    print("=" * 60)
    print()
    
    uvicorn.run(
        "localizer.api:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
