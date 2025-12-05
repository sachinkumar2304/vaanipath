"""
ML Localizer Service Client
Integrates VaaniPath-Backend with VaaniPath-Localizer ML service
"""
import requests
import logging
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

# ML Service Configuration
ML_SERVICE_URL = getattr(settings, 'ML_SERVICE_URL', 'http://localhost:8001')


async def trigger_transcription(
    video_file_path: str,
    video_id: str,
    source_lang: str = 'en',
    course_id: str = 'education',
    mode: str = 'fast'
) -> Dict[str, Any]:
    """
    Trigger ML transcription service for a video
    """
    try:
        logger.info(f"Triggering ML transcription for video {video_id}")
        
        data = {
            'source': source_lang,
            'course_id': course_id,
            'job_id': video_id,
            'mode': mode
        }
        
        # If video_file_path is a URL (Cloudinary), we need to handle it.
        # The current ML service expects a file upload for /transcribe.
        # Ideally, ML service should accept URL.
        # For now, if it's a URL, we might need to download it or pass it if ML supports it.
        # The previous code assumed we could pass 'video_url' in data.
        # Let's assume we pass the URL and the ML service handles it (we might need to update ML service if it doesn't).
        # Wait, I checked api.py, /transcribe expects UploadFile.
        # So we MUST download the file from Cloudinary if we want to send it to ML service,
        # OR we update ML service to accept URL.
        # Given the constraints, let's try to send the URL if possible, but the API expects File.
        # Actually, in videos.py, we have the file object! 
        # But we already read it to upload to Cloudinary.
        # We can re-read it or seek(0) if it's a file-like object.
        # However, `videos.py` is async and `file` is UploadFile.
        
        # Let's update this client to accept `file_content` optionally?
        # Or better, let's update ML service to accept URL? 
        # Updating ML service to accept URL is cleaner but might be complex (download logic).
        # Let's stick to what we have: `videos.py` has the file.
        # But `videos.py` reads it.
        
        # Let's look at `videos.py` again. It reads `file_content = await file.read()`.
        # So we have the bytes.
        
        # But wait, `trigger_transcription` is called AFTER upload.
        # We can pass the `file_content` bytes to this function.
        
        pass 
    except Exception as e:
        logger.error(f"Transcription trigger failed: {e}")
        return {'success': False, 'error': str(e)}

async def trigger_transcription_with_content(
    file_content: bytes,
    filename: str,
    video_id: str,
    source_lang: str = 'en',
    course_id: str = 'education',
    mode: str = 'fast'
) -> Dict[str, Any]:
    try:
        logger.info(f"Triggering ML transcription for video {video_id}")
        
        files = {'file': (filename, file_content, 'video/mp4')}
        data = {
            'source': source_lang,
            'course_id': course_id,
            'job_id': video_id,
            'mode': mode
        }
        
        response = requests.post(
            f'{ML_SERVICE_URL}/upload',
            files=files,
            data=data,
            timeout=300
        )
        
        response.raise_for_status()
        result = response.json()
        
        return {
            'success': True,
            'job_id': video_id,
            'ml_job_id': result.get('job_id', video_id),
            'status': 'transcribing',
            'manifest_path': result.get('manifest_path')
        }
    except Exception as e:
        logger.error(f"Transcription trigger failed: {str(e)}")
        return {'success': False, 'error': str(e)}


async def trigger_translation(
    video_id: str,
    target_lang: str,
    translation_model: str = 'google',
    voice: Optional[str] = None
) -> Dict[str, Any]:
    """
    Trigger ML translation service for an existing job
    """
    try:
        logger.info(f"Triggering ML translation for video {video_id} to {target_lang}")
        
        payload = {
            'job_id': video_id,
            'target': target_lang,
            'translation_model': translation_model,
            'voice': voice
        }
        
        response = requests.post(
            f'{ML_SERVICE_URL}/translate',
            json=payload,
            timeout=600, # Long timeout for translation
            stream=True
        )
        
        response.raise_for_status()
        
        return {
            'success': True,
            'job_id': video_id,
            'status': 'completed',
            'content': response.content
        }
        
    except Exception as e:
        logger.error(f"ML translation failed: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'message': 'Translation failed'
        }


async def trigger_localization(
    video_url: str,
    video_id: str,
    target_lang: str,
    source_lang: str = 'en',
    course_id: str = 'general'
) -> Dict[str, Any]:
    """
    Trigger full localization: Download video -> Upload to ML -> Transcribe -> Translate
    """
    try:
        logger.info(f"Starting full localization for {video_id} ({source_lang} -> {target_lang})")
        
        # 1. Download video from URL
        logger.info(f"Downloading video from {video_url}...")
        video_response = requests.get(video_url, stream=True)
        video_response.raise_for_status()
        
        # 2. Upload to ML Service
        # We use the /upload endpoint which handles everything
        files = {
            'file': (f"{video_id}.mp4", video_response.content, 'video/mp4')
        }
        data = {
            'source': source_lang,
            'target': target_lang,
            'course_id': course_id,
            'job_id': video_id,
            'mode': 'fast'
        }
        
        logger.info(f"Uploading to ML service...")
        response = requests.post(
            f'{ML_SERVICE_URL}/upload',
            files=files,
            data=data,
            timeout=1200  # 20 minutes timeout for full process
        )
        
        response.raise_for_status()
        
        # 🚀 NEW: ML service returns JSON with Cloudinary URL
        result = response.json()
        
        return {
            'success': True,
            'job_id': video_id,
            'status': 'completed',
            'cloudinary_url': result.get('cloudinary_url'),
            'transcript_original': result.get('transcript_original'),
            'transcript_translated': result.get('transcript_translated'),
            'message': result.get('message', 'Localization complete')
        }
        
    except Exception as e:
        logger.error(f"Localization failed: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'message': 'Localization failed'
        }


async def check_translation_status(job_id: str) -> Dict[str, Any]:
    """
    Check status of a translation job
    
    Args:
        job_id: Job identifier (usually video_id)
    
    Returns:
        Dict with job status and progress
    """
    try:
        response = requests.get(
            f'{ML_SERVICE_URL}/jobs/{job_id}/stats',
            timeout=30
        )
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.ConnectionError:
        return {'error': 'ML service unavailable'}
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        return {'error': str(e)}


async def get_translated_video_url(job_id: str) -> Optional[str]:
    """
    Get URL of translated video if ready
    
    Args:
        job_id: Job identifier
    
    Returns:
        URL string or None if not ready
    """
    try:
        # ML service stores output in localizer/output/{job_id}/final_video.mp4
        # You may need to copy this to Cloudinary or serve from ML service
        video_url = f'{ML_SERVICE_URL}/output/{job_id}/final_video.mp4'
        
        # Test if file exists
        response = requests.head(video_url, timeout=10)
        if response.status_code == 200:
            return video_url
        return None
        
    except Exception as e:
        logger.error(f"Failed to get video URL: {str(e)}")
        return None


async def get_subtitles_url(job_id: str, chunk_index: int = 0, format: str = 'srt') -> Optional[str]:
    """
    Get URL of subtitle file
    
    Args:
        job_id: Job identifier
        chunk_index: Chunk index (0 for single-pass processing)
        format: 'srt' or 'vtt'
    
    Returns:
        URL string or None
    """
    try:
        subtitle_url = f'{ML_SERVICE_URL}/output/{job_id}/tts/chunk_{chunk_index:04d}.{format}'
        response = requests.head(subtitle_url, timeout=10)
        if response.status_code == 200:
            return subtitle_url
        return None
    except Exception as e:
        logger.error(f"Failed to get subtitles: {str(e)}")
        return None


async def seed_voices(gender: str = 'male') -> Dict[str, Any]:
    """
    Seed TTS voices for India languages
    
    Args:
        gender: 'male' or 'female'
    
    Returns:
        Dict with seeding status
    """
    try:
        response = requests.post(
            f'{ML_SERVICE_URL}/voice/seed/india',
            params={'gender': gender},
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Voice seeding failed: {str(e)}")
        return {'error': str(e)}
