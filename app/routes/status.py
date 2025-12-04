"""Status route for checking job status."""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import logging

from app.db.database import get_db
from app.db.models import Job

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/status/{job_id}")
async def get_status(
    job_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the status of a job.
    
    Args:
        job_id: Job ID
    
    Returns:
        Job status and metadata
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job.to_dict()


@router.get("/status")
async def list_jobs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all jobs.
    
    Args:
        skip: Number of jobs to skip
        limit: Maximum number of jobs to return
    
    Returns:
        List of jobs
    """
    jobs = db.query(Job).offset(skip).limit(limit).all()
    return [job.to_dict() for job in jobs]



