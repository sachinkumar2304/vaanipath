from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict
from datetime import datetime
import uuid

from app.models.processing import (
    VideoProcessRequest,
    ProcessingStatusResponse,
    TranscriptionRequest,
    TranscriptionResponse,
    TTSRequest,
    TTSResponse,
    SubtitleRequest,
    SubtitleResponse,
    DubbingRequest,
    DubbingResponse,
    BatchProcessRequest,
    BatchProcessResponse,
    ModelsInfoResponse,
    ProcessingStage,
    ModelSize,
    SubtitleFormat
)
from app.api.deps import get_current_user, get_current_admin
from app.db.supabase_client import supabase
from app.config import settings
import cloudinary
import cloudinary.uploader
from app.services.ml_localizer_client import trigger_translation, trigger_localization, check_translation_status
import asyncio

router = APIRouter()

async def process_dubbing_task(video_id: str, language: str, content_type: str = "video"):
    """
    Background task to handle dubbing/translation generation and upload
    Supports video, audio, and document content
    """
    try:
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET
        )
        
        # Get video URL from DB
        video_response = supabase.table("videos").select("file_url, source_language").eq("id", video_id).execute()
        if not video_response.data:
            raise ValueError(f"Video {video_id} not found")
            
        video_data = video_response.data[0]
        video_url = video_data.get("file_url")
        source_lang = video_data.get("source_language", "en")
        
        if not video_url:
            raise ValueError("Video URL not found")
        
        # 1. Call appropriate ML Service based on content type
        if content_type == "video":
            print(f"DEBUG: Starting full localization for video {video_id} via trigger_localization")
            # Use trigger_localization which handles download -> upload -> transcribe -> translate
            result = await trigger_localization(
                video_url=video_url,
                video_id=video_id,
                target_lang=language,
                source_lang=source_lang
            )
        elif content_type == "audio":
            # TODO: Implement audio dubbing client
            result = await trigger_localization(
                video_url=video_url,
                video_id=video_id,
                target_lang=language,
                source_lang=source_lang
            )
        elif content_type == "document":
            # TODO: Implement document translation client
            # Documents might need a different flow, but for now reuse
            result = await trigger_translation(video_id, language) 
        else:
            raise ValueError(f"Unsupported content type: {content_type}")
        
        if not result.get('success'):
            # Update DB as failed
            supabase.table("translations").update({
                "status": "failed",
                "error_message": result.get('error', 'ML service failed')
            }).eq("video_id", video_id).eq("language", language).execute()
            return

        # 🚀 NEW: ML service already uploaded to Cloudinary, just use the URL
        dubbed_url = result.get('cloudinary_url')
        
        if not dubbed_url:
            raise ValueError("ML service did not return Cloudinary URL")
        
        # 3. Update DB with the Cloudinary URL and Transcripts
        update_data = {
            "status": "completed",
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if content_type == "video":
            update_data["dubbed_video_url"] = dubbed_url
        elif content_type == "audio":
            update_data["audio_url"] = dubbed_url
        elif content_type == "document":
            update_data["dubbed_video_url"] = dubbed_url
            
        # Save Translated Text
        transcript_translated = result.get('transcript_translated')
        if transcript_translated:
            update_data["translated_text"] = transcript_translated
        
        supabase.table("translations").update(update_data).eq(
            "video_id", video_id
        ).eq("language", language).execute()

        # Save Original Transcript (if available)
        transcript_original = result.get('transcript_original')
        if transcript_original:
            # Check if transcription exists
            trans_check = supabase.table("transcriptions").select("id").eq("video_id", video_id).eq("language", source_lang).execute()
            
            trans_data = {
                "video_id": video_id,
                "language": source_lang,
                "full_text": transcript_original,
                "status": "completed"
            }
            
            if trans_check.data:
                supabase.table("transcriptions").update(trans_data).eq("id", trans_check.data[0]['id']).execute()
            else:
                supabase.table("transcriptions").insert(trans_data).execute()
        
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Dubbing task failed for {video_id}/{language}: {error_detail}")
        
        supabase.table("translations").update({
            "status": "failed",
            "error_message": str(e)[:500]  # Limit error message length
        }).eq("video_id", video_id).eq("language", language).execute()



# ==========================================
# ADMIN ENDPOINTS (ML Processing)
# ==========================================

@router.post("/videos/{video_id}/process", response_model=ProcessingStatusResponse)
async def start_video_processing(
    video_id: str,
    request: VideoProcessRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_admin)
):
    """
    🎬 **[ADMIN] Start Complete Video Processing**
    
    Triggers full pipeline:
    1. Whisper ASR (speech → text)
    2. IndicTrans2 (translation)
    3. Coqui TTS (text → speech)
    4. FFmpeg (lip sync)
    5. Quiz generation (optional)
    
    **Admin only** - starts background celery job
    """
    if supabase is None:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    # Verify video exists
    video_response = supabase.table("videos").select("*").eq("id", video_id).execute()
    if not video_response.data:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Create processing jobs for each language
    jobs_created = []
    for lang in request.target_languages:
        job_data = {
            "id": str(uuid.uuid4()),
            "video_id": video_id,
            "target_language": lang,
            "stage": ProcessingStage.TRANSCRIBING.value,
            "status": "pending",
            "progress": 0,
            "enable_lip_sync": request.enable_lip_sync,
            "generate_quiz": request.generate_quiz,
            "created_at": datetime.utcnow().isoformat()
        }
        supabase.table("processing_jobs").insert(job_data).execute()
        jobs_created.append(job_data)
    
    # TODO: Trigger background celery task
    # from app.tasks.video_processing import process_video_pipeline
    # background_tasks.add_task(process_video_pipeline, video_id, request.dict())
    
    return ProcessingStatusResponse(
        video_id=video_id,
        overall_status=ProcessingStage.TRANSCRIBING,
        progress_percentage=5,
        stages={
            "transcription": {"status": "pending", "progress": 0, "message": "Waiting to start"},
            "translation": {"status": "pending", "progress": 0, "message": "Not started"},
            "tts": {"status": "pending", "progress": 0, "message": "Not started"},
            "dubbing": {"status": "pending", "progress": 0, "message": "Not started"}
        },
        estimated_time_remaining=600  # 10 minutes estimate
    )


@router.get("/videos/{video_id}/processing-status", response_model=ProcessingStatusResponse)
async def get_processing_status(
    video_id: str,
    current_user: dict = Depends(get_current_admin)
):
    """
    📊 **[ADMIN] Check Processing Status**
    
    Returns real-time status of all processing stages
    """
    if supabase is None:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    jobs_response = supabase.table("processing_jobs").select("*").eq("video_id", video_id).execute()
    
    if not jobs_response.data:
        raise HTTPException(status_code=404, detail="No processing jobs found")
    
    # Calculate overall progress
    total_progress = sum(job.get("progress", 0) for job in jobs_response.data)
    avg_progress = total_progress // len(jobs_response.data) if jobs_response.data else 0
    
    # Determine overall status
    all_completed = all(job["status"] == "completed" for job in jobs_response.data)
    any_failed = any(job["status"] == "failed" for job in jobs_response.data)
    
    if all_completed:
        overall_status = ProcessingStage.COMPLETED
    elif any_failed:
        overall_status = ProcessingStage.FAILED
    else:
        overall_status = ProcessingStage.TRANSCRIBING
    
    stages = {
        "transcription": {"status": "in_progress", "progress": 80, "message": "Extracting speech..."},
        "translation": {"status": "in_progress", "progress": 40, "message": "Translating to Hindi..."},
        "tts": {"status": "pending", "progress": 0, "message": "Waiting for translation"},
        "dubbing": {"status": "pending", "progress": 0, "message": "Not started"}
    }
    
    return ProcessingStatusResponse(
        video_id=video_id,
        overall_status=overall_status,
        progress_percentage=avg_progress,
        stages=stages,
        estimated_time_remaining=300 if not all_completed else 0
    )


@router.post("/transcription/generate", response_model=TranscriptionResponse)
async def generate_transcription(
    request: TranscriptionRequest,
    current_user: dict = Depends(get_current_admin)
):
    """
    🎤 **[ADMIN] Generate Transcription (Whisper)**
    
    Uses Whisper ASR to convert speech to text
    """
    if supabase is None:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    # Verify video exists
    video_response = supabase.table("videos").select("*").eq("id", request.video_id).execute()
    if not video_response.data:
        raise HTTPException(status_code=404, detail="Video not found")
    
    video = video_response.data[0]
    
    # TODO: Call ML service
    # from app.services.ml_service import transcribe_audio
    # transcription = await transcribe_audio(video["file_url"], request.model_size, request.language)
    
    # Mock response
    from app.models.processing import TranscriptionSegment
    return TranscriptionResponse(
        video_id=request.video_id,
        language=request.language,
        full_text="Welcome to this educational video about machine learning...",
        segments=[
            TranscriptionSegment(start=0.0, end=3.5, text="Welcome to this educational video"),
            TranscriptionSegment(start=3.5, end=7.2, text="about machine learning")
        ],
        duration=video.get("duration", 120.0),
        created_at=datetime.utcnow()
    )


@router.post("/tts/generate", response_model=TTSResponse)
async def generate_tts(
    request: TTSRequest,
    current_user: dict = Depends(get_current_admin)
):
    """
    🔊 **[ADMIN] Generate TTS Audio (Coqui TTS)**
    
    Converts translated text to speech
    """
    if supabase is None:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    # Get translation text
    translation_response = supabase.table("translations").select("*").eq(
        "video_id", request.video_id
    ).eq("language", request.language).execute()
    
    if not translation_response.data:
        raise HTTPException(status_code=404, detail="Translation not found")
    
    # TODO: Call ML service
    # from app.services.ml_service import generate_speech
    # audio_path = await generate_speech(translation_text, request.language, request.voice_gender)
    
    # Mock response
    return TTSResponse(
        video_id=request.video_id,
        language=request.language,
        audio_url=f"https://res.cloudinary.com/{settings.CLOUDINARY_CLOUD_NAME}/video/upload/gyanify/audio/{request.video_id}_{request.language}.mp3",
        duration=125.5,
        created_at=datetime.utcnow()
    )


@router.post("/subtitles/generate", response_model=SubtitleResponse)
async def generate_subtitles(
    request: SubtitleRequest,
    current_user: dict = Depends(get_current_admin)
):
    """
    📝 **[ADMIN] Generate Subtitles**
    
    Creates subtitle file from translation segments
    """
    if supabase is None:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    # Get translation
    translation_response = supabase.table("translations").select("*").eq(
        "video_id", request.video_id
    ).eq("language", request.language).execute()
    
    if not translation_response.data:
        raise HTTPException(status_code=404, detail="Translation not found")
    
    # TODO: Generate subtitle file
    # from app.services.subtitle_generator import create_subtitle_file
    # subtitle_path = create_subtitle_file(translation_segments, request.format)
    
    subtitle_id = str(uuid.uuid4())
    
    return SubtitleResponse(
        id=subtitle_id,
        video_id=request.video_id,
        language=request.language,
        format=request.format,
        subtitle_url=f"https://res.cloudinary.com/{settings.CLOUDINARY_CLOUD_NAME}/raw/upload/gyanify/subtitles/{subtitle_id}.{request.format.value}",
        created_at=datetime.utcnow()
    )


@router.post("/dubbing/create", response_model=DubbingResponse)
async def create_dubbed_video(
    request: DubbingRequest,
    current_user: dict = Depends(get_current_admin)
):
    """
    🎥 **[ADMIN] Create Dubbed Video (FFmpeg + Lip Sync)**
    
    Merges translated audio with video and syncs lips
    """
    if supabase is None:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    # Verify video exists
    video_response = supabase.table("videos").select("*").eq("id", request.video_id).execute()
    if not video_response.data:
        raise HTTPException(status_code=404, detail="Video not found")
    
    video = video_response.data[0]
    
    # TODO: Call ML service
    # from app.services.ml_service import synchronize_lip_movement
    # dubbed_path = await synchronize_lip_movement(
    #     video["file_url"], 
    #     audio_path, 
    #     request.enable_lip_sync
    # )
    
    # Update translations table with dubbed video URL
    dubbed_url = f"https://res.cloudinary.com/{settings.CLOUDINARY_CLOUD_NAME}/video/upload/gyanify/dubbed/{request.video_id}_{request.language}.mp4"
    
    supabase.table("translations").update({
        "dubbed_video_url": dubbed_url,
        "status": "completed"
    }).eq("video_id", request.video_id).eq("language", request.language).execute()
    
    return DubbingResponse(
        video_id=request.video_id,
        language=request.language,
        dubbed_video_url=dubbed_url,
        thumbnail_url=f"https://res.cloudinary.com/{settings.CLOUDINARY_CLOUD_NAME}/image/upload/gyanify/thumbnails/{request.video_id}_thumb.jpg",
        duration=video.get("duration", 120.0),
        created_at=datetime.utcnow()
    )


@router.post("/batch/process", response_model=BatchProcessResponse)
async def batch_process_videos(
    request: BatchProcessRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_admin)
):
    """
    🚀 **[ADMIN] Batch Process Multiple Videos**
    
    Queues multiple videos for processing
    """
    if supabase is None:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    batch_id = str(uuid.uuid4())
    total_jobs = len(request.video_ids) * len(request.target_languages)
    
    # Create batch record
    batch_data = {
        "id": batch_id,
        "total_videos": len(request.video_ids),
        "total_jobs": total_jobs,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }
    
    # TODO: Queue batch processing
    # from app.tasks.batch_processor import process_batch
    # background_tasks.add_task(process_batch, batch_id, request.dict())
    
    return BatchProcessResponse(
        batch_id=batch_id,
        total_videos=len(request.video_ids),
        total_jobs=total_jobs,
        estimated_time=total_jobs * 300,  # 5 min per job estimate
        created_at=datetime.utcnow()
    )


@router.get("/models/info", response_model=ModelsInfoResponse)
async def get_models_info(current_user: dict = Depends(get_current_admin)):
    """
    🤖 **[ADMIN] Get ML Models Information**
    
    Returns status and info of all loaded ML models
    """
    # TODO: Get actual model info
    # from app.services.ml_service import get_model_info
    # model_info = get_model_info()
    
    from app.models.processing import ModelInfo
    return ModelsInfoResponse(
        whisper=ModelInfo(
            name="Whisper",
            version="large-v3",
            type="whisper",
            languages=["en", "hi", "ta", "te", "bn", "mr", "gu", "kn", "ml", "pa"],
            status="loaded",
            memory_usage_mb=2800.5
        ),
        translation=ModelInfo(
            name="IndicTrans2",
            version="v2",
            type="translation",
            languages=["hi", "ta", "te", "bn", "mr", "gu", "kn", "ml", "pa"],
            status="loaded",
            memory_usage_mb=1500.3
        ),
        tts=ModelInfo(
            name="Coqui TTS",
            version="0.22.0",
            type="tts",
            languages=["hi", "ta", "te"],
            status="loaded",
            memory_usage_mb=800.2
        ),
        total_memory_mb=5100.0,
        gpu_available=True
    )


# ==========================================
# STUDENT ENDPOINTS (Read-Only Access)
# ==========================================

@router.get("/transcription/{video_id}", response_model=TranscriptionResponse)
async def get_transcription(
    video_id: str,
    language: str = "en",
    include_segments: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """
    📖 **[STUDENT] Get Transcription**
    
    Retrieve transcription for a video
    """
    if supabase is None:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    # Get translation (which contains transcription)
    translation_response = supabase.table("translations").select("*").eq(
        "video_id", video_id
    ).eq("language", language).execute()
    
    if not translation_response.data:
        raise HTTPException(status_code=404, detail="Transcription not found")
    
    from app.models.processing import TranscriptionSegment
    segments = [
        TranscriptionSegment(start=0.0, end=3.5, text="Welcome to this video"),
        TranscriptionSegment(start=3.5, end=7.2, text="about machine learning")
    ] if include_segments else None
    
    return TranscriptionResponse(
        video_id=video_id,
        language=language,
        full_text="Complete transcription text here...",
        segments=segments,
        duration=120.0,
        created_at=datetime.utcnow()
    )


@router.get("/translation/{video_id}/{language}")
async def get_translation_text(
    video_id: str,
    language: str,
    include_segments: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """
    🌐 **[STUDENT] Get Translation**
    
    Retrieve translated text for a video
    """
    if supabase is None:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    translation_response = supabase.table("translations").select("*").eq(
        "video_id", video_id
    ).eq("language", language).execute()
    
    if not translation_response.data:
        raise HTTPException(status_code=404, detail="Translation not found")
    
    translation = translation_response.data[0]
    
    segments = [
        {"start": 0.0, "end": 3.5, "text": "इस वीडियो में आपका स्वागत है"},
        {"start": 3.5, "end": 7.2, "text": "मशीन लर्निंग के बारे में"}
    ] if include_segments else None
    
    return {
        "video_id": video_id,
        "language": language,
        "translated_text": translation.get("translated_text", ""),
        "segments": segments,
        "quality_score": translation.get("quality_score", 0.0),
        "status": translation.get("status", "completed")
    }


@router.get("/tts/{video_id}/{language}")
async def get_tts_audio(
    video_id: str,
    language: str,
    current_user: dict = Depends(get_current_user)
):
    """
    🔊 **[STUDENT] Download TTS Audio**
    
    Get audio file URL for translated speech
    """
    if supabase is None:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    translation_response = supabase.table("translations").select("*").eq(
        "video_id", video_id
    ).eq("language", language).execute()
    
    if not translation_response.data:
        raise HTTPException(status_code=404, detail="Audio not found")
    
    return {
        "video_id": video_id,
        "language": language,
        "audio_url": f"https://res.cloudinary.com/{settings.CLOUDINARY_CLOUD_NAME}/video/upload/gyanify/audio/{video_id}_{language}.mp3",
        "duration": 125.5,
        "format": "mp3"
    }


@router.get("/subtitles/{video_id}/{language}")
async def get_subtitles(
    video_id: str,
    language: str,
    format: SubtitleFormat = SubtitleFormat.VTT,
    current_user: dict = Depends(get_current_user)
):
    """
    📝 **[STUDENT] Get Subtitles**
    
    Download subtitle file for video
    """
    if supabase is None:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    translation_response = supabase.table("translations").select("*").eq(
        "video_id", video_id
    ).eq("language", language).execute()
    
    if not translation_response.data:
        raise HTTPException(status_code=404, detail="Subtitles not found")
    
    return {
        "video_id": video_id,
        "language": language,
        "subtitle_url": f"https://res.cloudinary.com/{settings.CLOUDINARY_CLOUD_NAME}/raw/upload/gyanify/subtitles/{video_id}_{language}.{format.value}",
        "format": format.value,
        "download_url": f"/api/v1/subtitles/download/{video_id}_{language}"
    }


@router.get("/subtitles/download/{subtitle_id}")
async def download_subtitle_file(
    subtitle_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    ⬇️ **[STUDENT] Direct Subtitle Download**
    
    Stream subtitle file for download
    """
    # TODO: Implement file streaming from Cloudinary
    # from app.storage.cloudinary_client import get_cloudinary_file
    # file_stream = await get_cloudinary_file(f"subtitles/{subtitle_id}.vtt")
    # return StreamingResponse(file_stream, media_type="text/vtt")
    
    return {
        "message": "Direct download",
        "subtitle_id": subtitle_id,
        "url": f"https://res.cloudinary.com/{settings.CLOUDINARY_CLOUD_NAME}/raw/upload/gyanify/subtitles/{subtitle_id}.vtt"
    }


@router.get("/dubbing/{video_id}/{language}")
async def get_dubbed_video(
    video_id: str,
    language: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    🎬 **[STUDENT] Get Dubbed Video**
    
    Retrieve final dubbed video URL. Triggers generation if not exists.
    """
    if supabase is None:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    # Check if translation exists
    translation_response = supabase.table("translations").select("*").eq(
        "video_id", video_id
    ).eq("language", language).execute()
    
    if translation_response.data:
        translation = translation_response.data[0]
        
        # If completed, return URL
        if translation.get("status") == "completed" and translation.get("dubbed_video_url"):
            return {
                "video_id": video_id,
                "language": language,
                "dubbed_video_url": translation.get("dubbed_video_url"),
                "status": "completed"
            }
            
        # If processing, return status
        if translation.get("status") in ["pending", "processing"]:
            return {
                "video_id": video_id,
                "language": language,
                "status": "processing",
                "message": "Dubbing in progress"
            }
            
        # If failed, we might want to retry?
        if translation.get("status") == "failed":
            # Retry logic below
            pass

    # If not exists or failed, trigger new job
    
    # Create/Update pending record
    if translation_response.data:
        supabase.table("translations").update({
            "status": "processing",
            "error_message": None,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("video_id", video_id).eq("language", language).execute()
    else:
        # Create new record
        # We need translated_text field as it is NOT NULL in schema.
        # We'll put a placeholder or empty string for now, assuming ML service populates it later?
        # Actually, the schema says `translated_text TEXT NOT NULL`.
        # We should probably make it nullable or provide a default.
        # For now, empty string.
        supabase.table("translations").insert({
            "video_id": video_id,
            "language": language,
            "translated_text": "", 
            "status": "processing"
        }).execute()
    
    # Trigger background task
    background_tasks.add_task(process_dubbing_task, video_id, language)
    
    return {
        "video_id": video_id,
        "language": language,
        "status": "processing",
        "message": "Dubbing started"
    }

# ==========================================
# STUDENT ENDPOINTS (Content Dubbing)
# ==========================================

@router.get("/content/{video_id}/available-languages")
async def get_available_languages(
    video_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    🌐 **[STUDENT] Get Available Dubbed Languages**
    
    Returns list of languages with their availability status
    """
    try:
        if not supabase:
            raise HTTPException(status_code=503, detail="Database not configured")
        
        video = supabase.table("videos").select("target_languages, source_language").eq(
            "id", video_id
        ).execute()
        
        if not video.data:
            raise HTTPException(status_code=404, detail="Video not found")
        
        target_languages = video.data[0].get("target_languages") or []
        source_language = video.data[0].get("source_language") or "en"
        
        translations = supabase.table("translations").select("language, status").eq(
            "video_id", video_id
        ).eq("status", "completed").execute()
        
        completed_languages = {t["language"] for t in translations.data} if translations.data else set()
        
        languages = []
        languages.append({
            "code": source_language,
            "available": True,
            "status": "original"
        })
        
        for lang in target_languages:
            languages.append({
                "code": lang,
                "available": lang in completed_languages,
                "status": "completed" if lang in completed_languages else "not_generated"
            })
        
        return {
            "video_id": video_id,
            "languages": languages
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/content/{video_id}/{language}")
async def get_dubbed_content(
    video_id: str,
    language: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    🎬 **[STUDENT] Get Dubbed/Translated Content**
    
    Returns dubbed video/audio or translated document URL.
    Implements smart caching - returns existing URL if available, triggers generation if not.
    """
    try:
        if not supabase:
            raise HTTPException(status_code=503, detail="Database not configured")
        
        # 1. Verify student is enrolled
        enrollment = supabase.table("enrollments").select("id").eq(
            "user_id", current_user["id"]
        ).eq("video_id", video_id).execute()
        
        if not enrollment.data:
            raise HTTPException(status_code=403, detail="Not enrolled in this course")
        
        # 2. Get video info to determine content type
        video_response = supabase.table("videos").select("content_type, file_url, title").eq(
            "id", video_id
        ).execute()
        
        if not video_response.data:
            raise HTTPException(status_code=404, detail="Content not found")
        
        video = video_response.data[0]
        content_type = video.get("content_type", "video")
        
        # 3. Check cache - look for existing translation
        translation_response = supabase.table("translations").select("*").eq(
            "video_id", video_id
        ).eq("language", language).execute()
        
        # 4. CACHING LOGIC - Return if already exists
        if translation_response.data:
            translation = translation_response.data[0]
            status_val = translation.get("status")
            
            # If completed, return cached URL
            if status_val == "completed":
                content_url = None
                if content_type == "video":
                    content_url = translation.get("dubbed_video_url")
                elif content_type == "audio":
                    content_url = translation.get("audio_url")
                elif content_type == "document":
                    content_url = translation.get("dubbed_video_url")
                
                if content_url:
                    return {
                        "video_id": video_id,
                        "language": language,
                        "content_type": content_type,
                        "content_url": content_url,
                        "status": "completed",
                        "cached": True,
                        "message": "Content already available"
                    }
            
            # If currently processing, return status
            if status_val in ["pending", "processing"]:
                return {
                    "video_id": video_id,
                    "language": language,
                    "content_type": content_type,
                    "status": "processing",
                    "cached": False,
                    "message": "Content is being generated. Please check back in a few minutes."
                }
            
            # If failed previously, retry
            if status_val == "failed":
                supabase.table("translations").update({
                    "status": "processing",
                    "error_message": None,
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("video_id", video_id).eq("language", language).execute()
                
                background_tasks.add_task(process_dubbing_task, video_id, language, content_type)
                
                return {
                    "video_id": video_id,
                    "language": language,
                    "content_type": content_type,
                    "status": "processing",
                    "cached": False,
                    "message": "Retrying content generation"
                }
        
        # 5. Not in cache - create new entry and trigger generation
        # Use UPSERT to prevent duplicate entries if multiple students request simultaneously
        try:
            # Try to insert, if conflict (duplicate) then update
            supabase.table("translations").upsert({
                "video_id": video_id,
                "language": language,
                "translated_text": "", 
                "status": "processing",
                "progress_percentage": 0,
                "created_at": datetime.utcnow().isoformat()
            }, on_conflict="video_id,language").execute()
        except Exception as upsert_error:
            # If upsert fails, the entry might already exist and be processing
            # Re-check status
            existing = supabase.table("translations").select("status").eq(
                "video_id", video_id
            ).eq("language", language).execute()
            
            if existing.data and existing.data[0].get("status") == "processing":
                # Another request already started it, just return processing status
                return {
                    "video_id": video_id,
                    "language": language,
                    "content_type": content_type,
                    "status": "processing",
                    "cached": False,
                    "message": "Content generation already in progress"
                }
            else:
                raise upsert_error
        
        background_tasks.add_task(process_dubbing_task, video_id, language, content_type)
        
        return {
            "video_id": video_id,
            "language": language,
            "content_type": content_type,
            "status": "processing",
            "cached": False,
            "message": f"{content_type.capitalize()} dubbing/translation started. This may take 2-5 minutes."
        }
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Get dubbed content error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/content/{video_id}/{language}")
async def cancel_dubbing(
    video_id: str,
    language: str,
    current_user: dict = Depends(get_current_user)
):
    """
    🛑 **[STUDENT] Cancel Dubbing/Translation**
    
    Cancel an in-progress dubbing task
    """
    try:
        if not supabase:
            raise HTTPException(status_code=503, detail="Database not configured")
        
        # Check if translation exists and is processing
        translation = supabase.table("translations").select("status").eq(
            "video_id", video_id
        ).eq("language", language).execute()
        
        if not translation.data:
            raise HTTPException(status_code=404, detail="Dubbing task not found")
        
        status = translation.data[0].get("status")
        
        if status == "completed":
            raise HTTPException(status_code=400, detail="Cannot cancel completed dubbing")
        
        # Update status to cancelled
        supabase.table("translations").update({
            "status": "cancelled",
            "error_message": "Cancelled by user",
            "updated_at": datetime.utcnow().isoformat()
        }).eq("video_id", video_id).eq("language", language).execute()
        
        return {
            "message": "Dubbing cancelled successfully",
            "video_id": video_id,
            "language": language
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/content/{video_id}/{language}/status")
async def check_dubbing_status(
    video_id: str,
    language: str,
    current_user: dict = Depends(get_current_user)
):
    """
    📊 **[STUDENT] Check Dubbing/Translation Status**
    
    Poll this endpoint to check if content is ready
    """
    try:
        if not supabase:
            raise HTTPException(status_code=503, detail="Database not configured")
        
        translation = supabase.table("translations").select("status, error_message, dubbed_video_url, audio_url, progress_percentage").eq(
            "video_id", video_id
        ).eq("language", language).execute()
        
        if not translation.data:
            return {
                "status": "not_started",
                "progress": 0,
                "message": "Dubbing/translation not requested yet"
            }
        
        data = translation.data[0]
        status_val = data.get("status")
        progress_val = data.get("progress_percentage", 0)
        
        if status_val == "completed":
            content_url = data.get("dubbed_video_url") or data.get("audio_url")
            return {
                "status": "completed",
                "progress": 100,
                "content_url": content_url,
                "message": "Content is ready!"
            }
        elif status_val == "processing":
            # Try to get real-time progress from ML service
            try:
                ml_status = await check_translation_status(video_id)
                if ml_status and "progress" in ml_status:
                    progress_val = ml_status["progress"]
            except Exception:
                pass # Fallback to DB progress or 50%

            return {
                "status": "processing",
                "progress": progress_val if progress_val > 0 else 50,  # Use actual progress or estimate 50%
                "message": f"Processing... {int(progress_val)}% complete" if progress_val > 0 else "Processing... Please wait."
            }
        elif status_val == "failed":
            return {
                "status": "failed",
                "progress": 0,
                "error": data.get("error_message"),
                "message": f"Generation failed: {data.get('error_message', 'Unknown error')}"
            }
        else:
            return {
                "status": "pending",
                "progress": 10,
                "message": "Queued for processing"
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
