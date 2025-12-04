"""Video merging service using FFmpeg."""
import logging
from pathlib import Path
from app.services.ffmpeg_utils import merge_video_audio, remove_audio_from_video, file_exists

logger = logging.getLogger(__name__)


def create_dubbed_video(
    original_video_path: Path,
    tts_audio_path: Path,
    output_path: Path,
    remove_original_audio: bool = True
) -> bool:
    """
    Create dubbed video by merging original video with TTS audio.
    
    Args:
        original_video_path: Path to original video file
        tts_audio_path: Path to TTS audio file
        output_path: Path to save dubbed video
        remove_original_audio: Whether to remove original audio first
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Check if files exist
        if not file_exists(original_video_path):
            logger.error(f"Original video not found: {original_video_path}")
            return False
        
        if not file_exists(tts_audio_path):
            logger.error(f"TTS audio not found: {tts_audio_path}")
            return False
        
        # If we need to remove original audio, create a temporary video without audio
        if remove_original_audio:
            temp_video_path = original_video_path.parent / f"temp_no_audio_{original_video_path.name}"
            
            if not file_exists(temp_video_path):
                logger.info("Removing original audio from video...")
                if not remove_audio_from_video(original_video_path, temp_video_path):
                    logger.error("Failed to remove audio from video")
                    return False
            
            video_to_merge = temp_video_path
        else:
            video_to_merge = original_video_path
        
        # Merge video and audio
        logger.info(f"Merging video and TTS audio: {output_path}")
        success = merge_video_audio(video_to_merge, tts_audio_path, output_path)
        
        # Clean up temporary file if created
        if remove_original_audio and temp_video_path.exists():
            try:
                temp_video_path.unlink()
            except Exception as e:
                logger.warning(f"Could not delete temporary file: {str(e)}")
        
        return success
        
    except Exception as e:
        logger.error(f"Error creating dubbed video: {str(e)}")
        return False



