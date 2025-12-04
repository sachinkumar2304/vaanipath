"""Background worker for processing uploaded files."""
import json
import logging
from pathlib import Path
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import Job, JobStatus
from app.utils.storage import (
    get_original_file_path,
    get_audio_path,
    get_transcript_path,
    get_translation_path,
    get_subtitle_path,
    INDIC_LANGUAGES
)
from app.services.ffmpeg_utils import extract_audio, check_ffmpeg_available
from app.services.stt_whisper import WhisperSTT
from app.services.translate_indictrans import get_translator
from app.services.glossary import GlossaryProcessor
from app.services.stt_whisper import WhisperSTT as STTService

logger = logging.getLogger(__name__)


def process_upload_task(job_id: str):
    """
    Process uploaded file: extract audio, transcribe, translate, generate subtitles.
    
    This function runs the complete initial processing pipeline:
    1. Extract audio
    2. Generate transcript using Whisper
    3. Translate to all Indic languages
    4. Apply glossary
    5. Generate subtitles (VTT + SRT)
    6. Mark job as ready
    
    Args:
        job_id: Job ID
    """
    db: Session = SessionLocal()
    
    try:
        # Update job status
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found")
            return
        
        job.status = JobStatus.PROCESSING
        db.commit()
        
        logger.info(f"Starting processing for job {job_id}")
        
        # Step 1: Extract audio
        logger.info("Step 1: Extracting audio...")
        original_file_path = get_original_file_path(job_id)
        if not original_file_path or not original_file_path.exists():
            raise Exception(f"Original file not found for job {job_id}")
        
        audio_path = get_audio_path(job_id)
        
        # Check if FFmpeg is available
        if not check_ffmpeg_available():
            raise Exception("FFmpeg is not available. Please install FFmpeg.")
        
        # Extract audio (only for video/audio files, skip for documents)
        if job.file_type in ["mp4", "mkv", "avi", "mov", "mp3", "wav", "m4a", "flac"]:
            success = extract_audio(original_file_path, audio_path)
            if not success:
                raise Exception("Failed to extract audio")
            logger.info(f"Audio extracted: {audio_path}")
        else:
            # For documents, we'll need OCR/transcription later
            logger.warning(f"File type {job.file_type} may require OCR. Skipping audio extraction.")
            # For now, skip audio extraction for documents
            audio_path = None
        
        # Step 2: Generate transcript using Whisper
        logger.info("Step 2: Generating transcript...")
        
        if audio_path and audio_path.exists():
            # Initialize Whisper STT
            stt_service = WhisperSTT(model_size="base", device="cpu")  # Use "cuda" for GPU
            stt_service.load_model()
            
            # Transcribe
            transcript_data = stt_service.transcribe(
                audio_path,
                language="en",
                word_timestamps=True
            )
            
            # Save transcript files
            transcript_json_path = get_transcript_path(job_id, "json")
            transcript_vtt_path = get_transcript_path(job_id, "vtt")
            transcript_srt_path = get_transcript_path(job_id, "srt")
            
            stt_service.save_transcript_json(transcript_data, transcript_json_path)
            stt_service.save_transcript_vtt(transcript_data, transcript_vtt_path)
            stt_service.save_transcript_srt(transcript_data, transcript_srt_path)
            
            logger.info("Transcript generated and saved")
        else:
            # For documents, create placeholder transcript
            logger.warning("No audio file available. Creating placeholder transcript.")
            transcript_data = {
                "language": "en",
                "full_text": "Document transcription not yet implemented",
                "segments": [
                    {
                        "id": 0,
                        "start": 0.0,
                        "end": 1.0,
                        "text": "Document transcription not yet implemented"
                    }
                ]
            }
            transcript_json_path = get_transcript_path(job_id, "json")
            with open(transcript_json_path, "w", encoding="utf-8") as f:
                json.dump(transcript_data, f, ensure_ascii=False, indent=2)
        
        # Step 3: Translate to all Indic languages
        logger.info("Step 3: Translating to all Indic languages...")
        
        translator = get_translator()
        translator.initialize() if hasattr(translator, 'initialize') else None
        
        # Load glossary if available (optional)
        glossary_processor = GlossaryProcessor()
        # You can load a glossary file here:
        # glossary_path = Path("glossary.json")
        # if glossary_path.exists():
        #     glossary_processor.load_glossary(glossary_path)
        
        translations = translator.translate_to_all_indic_languages(
            transcript_data,
            INDIC_LANGUAGES
        )
        
        # Step 4: Apply glossary and save translations
        logger.info("Step 4: Applying glossary and saving translations...")
        
        for lang, translated_data in translations.items():
            # Apply glossary
            if glossary_processor.glossary:
                translated_data = glossary_processor.apply_glossary_to_translation(
                    translated_data,
                    lang
                )
            
            # Save translation JSON
            translation_path = get_translation_path(job_id, lang)
            translation_path.parent.mkdir(parents=True, exist_ok=True)
            with open(translation_path, "w", encoding="utf-8") as f:
                json.dump(translated_data, f, ensure_ascii=False, indent=2)
            
            # Generate subtitles (VTT + SRT)
            subtitle_vtt_path = get_subtitle_path(job_id, lang, "vtt")
            subtitle_srt_path = get_subtitle_path(job_id, lang, "srt")
            
            # Use STT service to generate subtitle files
            stt_service = WhisperSTT()
            stt_service.save_transcript_vtt(translated_data, subtitle_vtt_path)
            stt_service.save_transcript_srt(translated_data, subtitle_srt_path)
        
        logger.info(f"Translations and subtitles generated for {len(translations)} languages")
        
        # Step 5: Mark job as ready
        job.status = JobStatus.READY_FOR_USE
        job.metadata = {
            "languages_processed": list(translations.keys()),
            "transcript_duration": transcript_data.get("duration", 0),
            "transcript_language": transcript_data.get("language", "en")
        }
        db.commit()
        
        logger.info(f"Job {job_id} processing completed successfully")
        
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {str(e)}")
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = JobStatus.ERROR
            job.error_message = str(e)
            db.commit()
        raise
    
    finally:
        db.close()


# Celery task wrapper (if using Celery)
import os

try:
    from celery import Celery
    
    celery_app = Celery(
        "localisation_engine",
        broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
        backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    )
    
    @celery_app.task(name="process_upload")
    def process_upload_celery_task(job_id: str):
        """Celery task wrapper for process_upload_task."""
        return process_upload_task(job_id)
    
    CELERY_AVAILABLE = True
    
except ImportError:
    # Celery not available
    CELERY_AVAILABLE = False
    logger.warning("Celery not available. Will use FastAPI BackgroundTasks.")


def get_task_runner():
    """
    Get the appropriate task runner function.
    
    Returns:
        Function that accepts (job_id, background_tasks) and starts the task
    """
    if CELERY_AVAILABLE:
        def run_with_celery(job_id: str, background_tasks=None):
            """Run task with Celery."""
            process_upload_celery_task.delay(job_id)
        return run_with_celery
    else:
        def run_with_background_tasks(job_id: str, background_tasks):
            """Run task with FastAPI BackgroundTasks."""
            background_tasks.add_task(process_upload_task, job_id)
        return run_with_background_tasks

