from pydantic_settings import BaseSettings
from pathlib import Path
import os

# Fix tokenizers parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"


# Get the project root directory (2 levels up from this file)
# This file is at: backend/app/core/config.py
# Project root is: ../../ (relative to this file)
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Keys
    groq_api_key: str = ""
    elevenlabs_api_key: str = ""

    # Ollama settings
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:latest"

    # Directories (relative to project root)
    upload_dir: Path = PROJECT_ROOT / "uploads"
    vector_db_dir: Path = PROJECT_ROOT / "vector_db"
    audio_output_dir: Path = PROJECT_ROOT / "generated_audio"

    # Embedding model
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Chunking parameters
    chunk_size: int = 512
    chunk_overlap: int = 50

    # Podcast settings
    max_podcast_duration: int = 180  # 3 minutes in seconds

    class Config:
        # Look for .env in project root, not backend directory
        env_file = str(PROJECT_ROOT / ".env")
        case_sensitive = False


settings = Settings()

# Debug: Print where we're looking for .env
print(f"🔍 Looking for .env file at: {PROJECT_ROOT / '.env'}")
print(f"📁 Project root: {PROJECT_ROOT}")
print(f"🔑 Groq API Key loaded: {'✅ Yes' if settings.groq_api_key else '❌ No'}")
print(f"🎤 ElevenLabs API Key loaded: {'✅ Yes' if settings.elevenlabs_api_key else '❌ No'}")

# Create required directories
settings.upload_dir.mkdir(exist_ok=True)
settings.vector_db_dir.mkdir(exist_ok=True)
settings.audio_output_dir.mkdir(exist_ok=True)
