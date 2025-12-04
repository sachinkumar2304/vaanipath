"""Upload route for handling file uploads."""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
import logging
from pathlib import Path

from app.db.database import get_db
from app.db.models import Job, JobStatus
from app.utils.storage import (
    save_uploaded_file,
    generate_job_id,
    get_job_directory,
    init_storage_directories
)
from app.workers.process_upload import process_upload_task, get_task_runner

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize storage directories on startup
init_storage_directories()

# Allowed file types
ALLOWED_EXTENSIONS = {
    ".mp4", ".mkv", ".avi", ".mov",  # Video
    ".mp3", ".wav", ".m4a", ".flac",  # Audio
    ".pdf", ".docx", ".txt"  # Documents
}


def get_file_extension(filename: str) -> str:
    """Get file extension from filename."""
    return Path(filename).suffix.lower()


def is_allowed_file(filename: str) -> bool:
    """Check if file type is allowed."""
    ext = get_file_extension(filename)
    return ext in ALLOWED_EXTENSIONS


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """
    Upload a file for processing.
    
    Accepts: mp4, mkv, mp3, wav, pdf, docx, txt
    
    Returns:
        Job ID and status
    """
    # Validate file type
    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Generate job ID
    job_id = generate_job_id()
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Save file
        file_path = save_uploaded_file(file_content, file.filename, job_id)
        
        # Determine file type
        file_type = get_file_extension(file.filename).lstrip(".")
        
        # Create job entry in database
        job = Job(
            id=job_id,
            original_filename=file.filename,
            file_type=file_type,
            status=JobStatus.PENDING
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        
        logger.info(f"File uploaded: {file.filename} -> Job ID: {job_id}")
        
        # Start background processing task
        # Supports both Celery and FastAPI BackgroundTasks
        task_runner = get_task_runner()
        task_runner(job_id, background_tasks)
        
        return {
            "job_id": job_id,
            "status": job.status.value,
            "message": "File uploaded successfully. Processing started."
        }
        
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

