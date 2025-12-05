import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application settings"""
    # App Configuration
    APP_NAME: str = os.getenv("APP_NAME", "Gyanify Localization Engine")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    
    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    
    # Community Supabase (Separate Database)
    COMMUNITY_SUPABASE_URL: str = os.getenv("COMMUNITY_SUPABASE_URL", "")
    COMMUNITY_SUPABASE_KEY: str = os.getenv("COMMUNITY_SUPABASE_KEY", "")
    
    # Storage Configuration - Cloudinary (Primary)
    STORAGE_TYPE: str = os.getenv("STORAGE_TYPE", "cloudinary")
    
    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET", "")
    
    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    
    # File Upload
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "524288000"))  # 500MB
    ALLOWED_VIDEO_FORMATS: str = os.getenv("ALLOWED_VIDEO_FORMATS", "mp4,avi,mov,mkv,webm")
    ALLOWED_AUDIO_FORMATS: str = os.getenv("ALLOWED_AUDIO_FORMATS", "mp3,wav,m4a,aac")
    
    @property
    def video_formats_list(self) -> List[str]:
        return self.ALLOWED_VIDEO_FORMATS.split(",")
    
    @property
    def audio_formats_list(self) -> List[str]:
        return self.ALLOWED_AUDIO_FORMATS.split(",")

    ALLOWED_DOC_FORMATS: str = os.getenv("ALLOWED_DOC_FORMATS", "pdf,doc,docx,ppt,pptx,txt")

    @property
    def doc_formats_list(self) -> List[str]:
        return self.ALLOWED_DOC_FORMATS.split(",")
    
    # ML Models
    WHISPER_MODEL_SIZE: str = os.getenv("WHISPER_MODEL_SIZE", "medium")
    TRANSLATION_MODEL: str = os.getenv("TRANSLATION_MODEL", "ai4bharat/indictrans2-en-indic-1B")
    TTS_MODEL: str = os.getenv("TTS_MODEL", "tts_models/multilingual/multi-dataset/your_tts")
    
    # Processing
    USE_GPU: bool = os.getenv("USE_GPU", "True").lower() == "true"
    MAX_CONCURRENT_JOBS: int = int(os.getenv("MAX_CONCURRENT_JOBS", 3))
    PROCESSING_TIMEOUT: int = int(os.getenv("PROCESSING_TIMEOUT", 3600))
    
    # ML Service
    ML_SERVICE_URL: str = os.getenv("ML_SERVICE_URL", "http://localhost:8001")
    
    # Languages
    SUPPORTED_LANGUAGES: str = os.getenv("SUPPORTED_LANGUAGES", "hi,ta,te,bn,mr,gu,kn,ml,pa,or,as,ur")
    
    # NO Pre-dubbing - All languages are on-demand
    # Transcript in all 22 languages generated on upload
    PRIMARY_LANGUAGES: list[str] = []  # No pre-dubbing
    
    # All 22 Indian languages mapping
    ALL_LANGUAGES: dict[str, str] = {
        # Primary (Pre-dubbed - Available immediately)
        "hi": "हिंदी",
        "mr": "मराठी",
        "ta": "தமிழ்",
        "te": "తెలుగు",
        "gu": "ગુજરાતી",
        
        # On-demand (Dub on request)
        "bn": "বাংলা",
        "kn": "ಕನ್ನಡ",
        "ml": "മലയാളം",
        "pa": "ਪੰਜਾਬੀ",
        "or": "ଓଡ଼ିଆ",
        "as": "অসমীয়া",
        "mai": "मैथिली",
        "sa": "संस्कृत",
        "ks": "कॉशुर",
        "ne": "नेपाली",
        "sd": "سنڌي",
        "ur": "اردو",
        "kok": "कोंकणी",
        "mni": "মৈতৈলোন্",
        "doi": "डोगरी",
        "sat": "ᱥᱟᱱᱛᱟᱲᱤ",
        "brx": "बड़ो",
    }
    
    @property
    def supported_languages_list(self) -> List[str]:
        return self.SUPPORTED_LANGUAGES.split(",")
    
    # Gamification
    QUESTIONS_PER_VIDEO: int = int(os.getenv("QUESTIONS_PER_VIDEO", 5))
    QUESTION_DIFFICULTY: str = os.getenv("QUESTION_DIFFICULTY", "medium")
    
    # Storage Paths
    UPLOAD_DIR: Path = BASE_DIR / os.getenv("UPLOAD_DIR", "storage/uploads")
    PROCESSING_DIR: Path = BASE_DIR / os.getenv("PROCESSING_DIR", "storage/processing")
    OUTPUT_DIR: Path = BASE_DIR / os.getenv("OUTPUT_DIR", "storage/outputs")
    TEMP_DIR: Path = BASE_DIR / os.getenv("TEMP_DIR", "storage/temp")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Path = BASE_DIR / os.getenv("LOG_FILE", "logs/app.log")
    
    # Celery
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"
    



# Initialize settings
settings = Settings()

# Create necessary directories
for directory in [
    settings.UPLOAD_DIR,
    settings.PROCESSING_DIR,
    settings.OUTPUT_DIR,
    settings.TEMP_DIR,
    settings.LOG_FILE.parent,
]:
    directory.mkdir(parents=True, exist_ok=True)
