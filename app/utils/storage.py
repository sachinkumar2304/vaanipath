"""Storage utilities for managing local file storage."""
import os
import shutil
from pathlib import Path
from typing import Optional
import uuid


# Base storage directory
STORAGE_ROOT = os.getenv("STORAGE_ROOT", "storage")


def get_storage_root() -> Path:
    """Get the storage root directory."""
    root = Path(STORAGE_ROOT)
    root.mkdir(parents=True, exist_ok=True)
    return root


def init_storage_directories():
    """Initialize all required storage directories."""
    root = get_storage_root()
    
    # Create main directories
    directories = [
        "uploads",
        "jobs"
    ]
    
    for directory in directories:
        (root / directory).mkdir(parents=True, exist_ok=True)
    
    return root


def get_job_directory(job_id: str) -> Path:
    """Get the directory for a specific job."""
    root = get_storage_root()
    job_dir = root / "jobs" / job_id
    
    # Create subdirectories
    subdirs = [
        "original",
        "transcripts/base",
        "translations",
        "subtitles",
        "audio_tts",
        "dubbed_video"
    ]
    
    for subdir in subdirs:
        (job_dir / subdir).mkdir(parents=True, exist_ok=True)
    
    return job_dir


def get_upload_directory() -> Path:
    """Get the upload directory."""
    root = get_storage_root()
    upload_dir = root / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def save_uploaded_file(file_content: bytes, filename: str, job_id: str) -> Path:
    """Save uploaded file to storage."""
    job_dir = get_job_directory(job_id)
    original_dir = job_dir / "original"
    
    file_path = original_dir / filename
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    return file_path


def get_original_file_path(job_id: str, filename: Optional[str] = None) -> Optional[Path]:
    """Get the path to the original uploaded file."""
    job_dir = get_job_directory(job_id)
    original_dir = job_dir / "original"
    
    if filename:
        file_path = original_dir / filename
        if file_path.exists():
            return file_path
    
    # If no filename provided, find the first file
    files = list(original_dir.glob("*"))
    if files:
        return files[0]
    
    return None


def get_audio_path(job_id: str) -> Path:
    """Get the path for extracted audio."""
    job_dir = get_job_directory(job_id)
    return job_dir / "original" / "audio.wav"


def get_transcript_path(job_id: str, format: str = "json") -> Path:
    """Get the path for transcript files."""
    job_dir = get_job_directory(job_id)
    base_dir = job_dir / "transcripts" / "base"
    
    if format == "json":
        return base_dir / "transcript.json"
    elif format == "vtt":
        return base_dir / "transcript.vtt"
    elif format == "srt":
        return base_dir / "transcript.srt"
    else:
        return base_dir / f"transcript.{format}"


def get_translation_path(job_id: str, lang: str) -> Path:
    """Get the path for translation JSON file."""
    job_dir = get_job_directory(job_id)
    return job_dir / "translations" / f"{lang}.json"


def get_subtitle_path(job_id: str, lang: str, format: str = "vtt") -> Path:
    """Get the path for subtitle files."""
    job_dir = get_job_directory(job_id)
    subtitle_dir = job_dir / "subtitles"
    
    if format == "vtt":
        return subtitle_dir / f"{lang}.vtt"
    elif format == "srt":
        return subtitle_dir / f"{lang}.srt"
    else:
        return subtitle_dir / f"{lang}.{format}"


def get_tts_audio_path(job_id: str, lang: str) -> Path:
    """Get the path for TTS audio file."""
    job_dir = get_job_directory(job_id)
    audio_dir = job_dir / "audio_tts"
    return audio_dir / f"{lang}.wav"


def get_dubbed_video_path(job_id: str, lang: str) -> Path:
    """Get the path for dubbed video file."""
    job_dir = get_job_directory(job_id)
    video_dir = job_dir / "dubbed_video"
    return video_dir / f"{lang}.mp4"


def file_exists(file_path: Path) -> bool:
    """Check if a file exists."""
    return file_path.exists() and file_path.is_file()


def generate_job_id() -> str:
    """Generate a unique job ID."""
    return str(uuid.uuid4())


# List of 22 Indic languages
INDIC_LANGUAGES = [
    "hi",  # Hindi
    "bn",  # Bengali
    "mr",  # Marathi
    "ta",  # Tamil
    "te",  # Telugu
    "kn",  # Kannada
    "ml",  # Malayalam
    "or",  # Odia
    "gu",  # Gujarati
    "pa",  # Punjabi
    "as",  # Assamese
    "ks",  # Kashmiri
    "sd",  # Sindhi
    "kok", # Konkani
    "ne",  # Nepali
    "sa",  # Sanskrit
    "ur",  # Urdu
    "si",  # Sinhala
    "my",  # Myanmar
    "th",  # Thai
    "lo",  # Lao
    "km"   # Khmer
]



