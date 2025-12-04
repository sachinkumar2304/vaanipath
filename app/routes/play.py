"""Play route for on-demand TTS and video dubbing."""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pathlib import Path
import logging

from app.db.database import get_db
from app.db.models import Job, JobStatus
from app.utils.storage import (
    get_tts_audio_path,
    get_dubbed_video_path,
    get_subtitle_path,
    get_translation_path,
    get_original_file_path,
    get_audio_path,
    file_exists,
    INDIC_LANGUAGES
)
from app.services.tts_coqui import get_tts_service
from app.services.merge_video import create_dubbed_video
import json

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/play/{job_id}/{lang}")
async def play_language(
    job_id: str,
    lang: str,
    db: Session = Depends(get_db)
):
    """
    Get audio/video for a specific language (on-demand TTS and dubbing).
    
    Args:
        job_id: Job ID
        lang: Language code (e.g., hi, bn, ta)
    
    Returns:
        URLs/paths for audio, video, and subtitles
    """
    # Validate language
    if lang not in INDIC_LANGUAGES and lang != "en":
        raise HTTPException(
            status_code=400,
            detail=f"Language {lang} not supported. Supported languages: {INDIC_LANGUAGES}"
        )
    
    # Get job from database
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if job is ready
    if job.status != JobStatus.READY_FOR_USE:
        raise HTTPException(
            status_code=400,
            detail=f"Job is not ready yet. Current status: {job.status.value}"
        )
    
    try:
        # Get paths
        tts_audio_path = get_tts_audio_path(job_id, lang)
        dubbed_video_path = get_dubbed_video_path(job_id, lang)
        subtitle_vtt_path = get_subtitle_path(job_id, lang, "vtt")
        subtitle_srt_path = get_subtitle_path(job_id, lang, "srt")
        translation_path = get_translation_path(job_id, lang)
        original_video_path = get_original_file_path(job_id)
        audio_path = get_audio_path(job_id)
        
        # Step 1: Generate TTS audio if it doesn't exist
        if not file_exists(tts_audio_path):
            logger.info(f"Generating TTS audio for {lang}...")
            
            # Load translation data
            if not file_exists(translation_path):
                raise HTTPException(
                    status_code=404,
                    detail=f"Translation for language {lang} not found"
                )
            
            with open(translation_path, "r", encoding="utf-8") as f:
                translation_data = json.load(f)
            
            # Generate TTS
            tts_service = get_tts_service(device="cuda")  # Use GPU if available, else CPU
            success = tts_service.synthesize_from_transcript(
                translation_data,
                tts_audio_path,
                lang
            )
            
            if not success:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to generate TTS audio"
                )
        
        # Step 2: Generate dubbed video if it doesn't exist
        if not file_exists(dubbed_video_path):
            logger.info(f"Generating dubbed video for {lang}...")
            
            if not original_video_path or not file_exists(original_video_path):
                raise HTTPException(
                    status_code=404,
                    detail="Original video file not found"
                )
            
            if not file_exists(tts_audio_path):
                raise HTTPException(
                    status_code=404,
                    detail="TTS audio file not found"
                )
            
            # Create dubbed video
            success = create_dubbed_video(
                original_video_path,
                tts_audio_path,
                dubbed_video_path,
                remove_original_audio=True
            )
            
            if not success:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to generate dubbed video"
                )
        
        # Step 3: Return file paths/URLs
        # In production, these would be actual URLs served by a web server
        base_url = f"/storage/jobs/{job_id}"
        
        response = {
            "job_id": job_id,
            "language": lang,
            "audio_url": f"{base_url}/audio_tts/{lang}.wav",
            "video_url": f"{base_url}/dubbed_video/{lang}.mp4",
            "subtitle_vtt_url": f"{base_url}/subtitles/{lang}.vtt" if file_exists(subtitle_vtt_path) else None,
            "subtitle_srt_url": f"{base_url}/subtitles/{lang}.srt" if file_exists(subtitle_srt_path) else None,
            "file_paths": {
                "audio": str(tts_audio_path),
                "video": str(dubbed_video_path),
                "subtitle_vtt": str(subtitle_vtt_path) if file_exists(subtitle_vtt_path) else None,
                "subtitle_srt": str(subtitle_srt_path) if file_exists(subtitle_srt_path) else None
            }
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in play endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")



