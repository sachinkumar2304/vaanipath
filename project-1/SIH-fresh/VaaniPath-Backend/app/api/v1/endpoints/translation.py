from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.models.translation import (
    TranslationRequest,
    TranslationResponse,
    GlossaryCreate,
    GlossaryTerm,
    QualityMetrics
)
from app.api.deps import get_current_admin, get_current_user
from app.db.supabase_client import supabase
from app.config import settings
from datetime import datetime
import logging
import uuid

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/start", response_model=TranslationResponse)
async def start_translation(
    request: TranslationRequest,
    current_user: dict = Depends(get_current_admin)
):
    """
    Start translation job for a video
    This endpoint creates a translation job that will be processed by ML service
    """
    try:
        # Check if Supabase is configured
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.warning("Supabase not configured, returning mock response")
            job_id = str(uuid.uuid4())
            return {
                "job_id": job_id,
                "video_id": request.video_id,
                "status": "queued",
                "created_at": datetime.utcnow().isoformat(),
                "message": "Database not configured - mock response"
            }
        
        # Verify video exists
        video_response = supabase.table("videos").select("*").eq("id", request.video_id).execute()
        
        if not video_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found"
            )
        
        # Create translation records for each target language
        job_ids = []
        for language in request.target_languages:
            # Check if translation already exists
            existing = supabase.table("translations")\
                .select("*")\
                .eq("video_id", request.video_id)\
                .eq("language", language)\
                .execute()
            
            if existing.data:
                logger.info(f"Translation for video {request.video_id} in {language} already exists")
                job_ids.append(existing.data[0]["id"])
                continue
            
            # Create translation record
            translation_data = {
                "video_id": request.video_id,
                "language": language,
                "status": "queued",
                "created_at": datetime.utcnow().isoformat()
            }
            
            translation_response = supabase.table("translations").insert(translation_data).execute()
            
            if translation_response.data:
                translation_id = translation_response.data[0]["id"]
                job_ids.append(translation_id)
                
                # Create processing job
                job_data = {
                    "video_id": request.video_id,
                    "job_type": "translation",
                    "status": "queued",
                    "progress": 0,
                    "created_at": datetime.utcnow().isoformat()
                }
                
                supabase.table("processing_jobs").insert(job_data).execute()
                
                # TODO: Trigger ML service via Celery task
                # from app.workers.tasks import process_translation
                # process_translation.delay(translation_id, language, request.dict())
        
        # Return first job ID (or primary one)
        primary_job_id = job_ids[0] if job_ids else str(uuid.uuid4())
        
        return {
            "job_id": primary_job_id,
            "video_id": request.video_id,
            "status": "queued",
            "created_at": datetime.utcnow()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Translation start error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{job_id}/status")
async def get_translation_status(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get translation job status
    Returns current status, progress, and any error messages
    """
    try:
        # Check if Supabase is configured
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.warning("Supabase not configured, returning mock response")
            return {
                "job_id": job_id,
                "status": "completed",
                "progress": 100,
                "current_step": "Translation completed",
                "steps": {
                    "asr": {"status": "completed", "progress": 100},
                    "translation": {"status": "completed", "progress": 100},
                    "tts": {"status": "completed", "progress": 100},
                    "lip_sync": {"status": "completed", "progress": 100}
                },
                "message": "Database not configured - mock response"
            }
        
        # Get translation record
        translation_response = supabase.table("translations")\
            .select("*")\
            .eq("id", job_id)\
            .execute()
        
        if not translation_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Translation job not found"
            )
        
        translation = translation_response.data[0]
        
        # Get processing job details
        job_response = supabase.table("processing_jobs")\
            .select("*")\
            .eq("video_id", translation["video_id"])\
            .order("created_at", desc=True)\
            .limit(1)\
            .execute()
        
        progress = 0
        current_step = "Queued"
        
        if job_response.data:
            job = job_response.data[0]
            progress = job.get("progress", 0)
            current_step = job.get("job_type", "Processing").title()
        
        return {
            "job_id": job_id,
            "status": translation["status"],
            "progress": progress,
            "current_step": current_step,
            "language": translation["language"],
            "transcript_url": translation.get("transcript_url"),
            "audio_url": translation.get("audio_url"),
            "video_url": translation.get("video_url"),
            "quality_score": translation.get("quality_score")
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Translation status error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{job_id}/quality", response_model=QualityMetrics)
async def get_quality_metrics(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get quality metrics for translation
    ML service will calculate and store these metrics
    """
    try:
        # Check if Supabase is configured
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.warning("Supabase not configured, returning mock response")
            return {
                "translation_accuracy": 92.5,
                "domain_terminology_score": 88.0,
                "cultural_adaptation_score": 85.5,
                "lip_sync_accuracy": 90.0,
                "overall_score": 89.0,
                "message": "Database not configured - mock metrics"
            }
        
        # Get translation record
        translation_response = supabase.table("translations")\
            .select("*")\
            .eq("id", job_id)\
            .execute()
        
        if not translation_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Translation not found"
            )
        
        translation = translation_response.data[0]
        
        # TODO: ML service will populate these fields
        # For now, return mock data or basic metrics
        quality_score = translation.get("quality_score", 0)
        
        # Calculate component scores (ML service will do this)
        return {
            "translation_accuracy": quality_score * 0.95 if quality_score else 0,
            "domain_terminology_score": quality_score * 0.90 if quality_score else 0,
            "cultural_adaptation_score": quality_score * 0.88 if quality_score else 0,
            "lip_sync_accuracy": quality_score * 0.92 if quality_score else None,
            "overall_score": quality_score if quality_score else 0
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Quality metrics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/glossary", response_model=GlossaryTerm)
async def add_glossary_term(
    term: GlossaryCreate,
    current_user: dict = Depends(get_current_admin)
):
    """
    Add a term to the glossary
    ML service will use these terms for domain-specific translation
    """
    try:
        # Check if Supabase is configured
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.warning("Supabase not configured, returning mock response")
            return {
                "term": term.term,
                "translation": term.translations,
                "domain": term.domain,
                "context": term.context,
                "message": "Database not configured - mock response"
            }
        
        # Check if term already exists
        existing = supabase.table("glossary")\
            .select("*")\
            .eq("term", term.term)\
            .eq("domain", term.domain)\
            .execute()
        
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Term already exists in this domain"
            )
        
        # Create glossary entry
        glossary_data = {
            "term": term.term,
            "domain": term.domain,
            "translations": term.translations,
            "context": term.context,
            "created_by": current_user.get("id"),
            "created_at": datetime.utcnow().isoformat()
        }
        
        response = supabase.table("glossary").insert(glossary_data).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create glossary term"
            )
        
        return {
            "term": term.term,
            "translation": term.translations,
            "domain": term.domain,
            "context": term.context
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Glossary creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/glossary/{domain}", response_model=List[GlossaryTerm])
async def get_domain_glossary(
    domain: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all glossary terms for a domain
    ML service will use this to improve translation accuracy
    """
    try:
        # Check if Supabase is configured
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.warning("Supabase not configured, returning mock response")
            return [
                {
                    "term": "Python",
                    "translation": {"hi": "पायथन", "ta": "பைதான்", "te": "పైథాన్"},
                    "domain": domain,
                    "context": "Programming language"
                },
                {
                    "term": "Variable",
                    "translation": {"hi": "चर", "ta": "மாறி", "te": "వేరియబుల్"},
                    "domain": domain,
                    "context": "Programming concept"
                }
            ]
        
        # Get glossary terms for domain
        response = supabase.table("glossary")\
            .select("*")\
            .eq("domain", domain)\
            .execute()
        
        if not response.data:
            return []
        
        return [
            {
                "term": item["term"],
                "translation": item["translations"],
                "domain": item["domain"],
                "context": item.get("context")
            }
            for item in response.data
        ]
    
    except Exception as e:
        logger.error(f"Glossary retrieval error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/glossary/{term}/{domain}")
async def delete_glossary_term(
    term: str,
    domain: str,
    current_user: dict = Depends(get_current_admin)
):
    """
    Delete a glossary term
    """
    try:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            return {"message": "Glossary term deleted (mock)", "term": term}
        
        response = supabase.table("glossary")\
            .delete()\
            .eq("term", term)\
            .eq("domain", domain)\
            .execute()
        
        return {"message": "Glossary term deleted successfully"}
    
    except Exception as e:
        logger.error(f"Glossary deletion error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
