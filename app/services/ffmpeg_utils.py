"""FFmpeg utilities for audio/video processing."""
import subprocess
import os
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def check_ffmpeg_available() -> bool:
    """Check if FFmpeg is available in the system."""
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def extract_audio(
    input_path: Path,
    output_path: Path,
    sample_rate: int = 24000,
    channels: int = 1
) -> bool:
    """
    Extract audio from video/audio file and convert to mono WAV.
    
    Args:
        input_path: Path to input file
        output_path: Path to output WAV file
        sample_rate: Output sample rate (default 24000)
        channels: Number of channels (1 for mono)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # FFmpeg command to extract audio and convert to mono 24kHz WAV
        cmd = [
            "ffmpeg",
            "-i", str(input_path),
            "-vn",  # No video
            "-ac", str(channels),  # Audio channels
            "-ar", str(sample_rate),  # Sample rate
            "-y",  # Overwrite output file
            str(output_path)
        ]
        
        logger.info(f"Extracting audio: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        logger.info(f"Audio extraction successful: {output_path}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Error extracting audio: {str(e)}")
        return False


def merge_video_audio(
    video_path: Path,
    audio_path: Path,
    output_path: Path,
    video_codec: str = "copy"
) -> bool:
    """
    Merge video with new audio track using FFmpeg.
    
    Args:
        video_path: Path to video file (without audio or original)
        audio_path: Path to TTS audio file
        output_path: Path to output dubbed video
        video_codec: Video codec to use (default: copy for no re-encoding)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # FFmpeg command to merge video and audio
        cmd = [
            "ffmpeg",
            "-i", str(video_path),
            "-i", str(audio_path),
            "-c:v", video_codec,  # Copy video codec
            "-c:a", "aac",  # Audio codec
            "-shortest",  # Finish encoding when shortest input ends
            "-y",  # Overwrite output file
            str(output_path)
        ]
        
        logger.info(f"Merging video and audio: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        logger.info(f"Video merge successful: {output_path}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Error merging video: {str(e)}")
        return False


def remove_audio_from_video(
    input_path: Path,
    output_path: Path
) -> bool:
    """
    Remove audio track from video file.
    
    Args:
        input_path: Path to input video
        output_path: Path to output video without audio
    
    Returns:
        True if successful, False otherwise
    """
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            "ffmpeg",
            "-i", str(input_path),
            "-c:v", "copy",  # Copy video codec
            "-an",  # No audio
            "-y",
            str(output_path)
        ]
        
        logger.info(f"Removing audio from video: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        logger.info(f"Audio removal successful: {output_path}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Error removing audio: {str(e)}")
        return False


def get_video_duration(video_path: Path) -> Optional[float]:
    """
    Get video duration in seconds using FFprobe.
    
    Args:
        video_path: Path to video file
    
    Returns:
        Duration in seconds or None if error
    """
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(video_path)
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        duration = float(result.stdout.strip())
        return duration
        
    except (subprocess.CalledProcessError, ValueError) as e:
        logger.error(f"Error getting video duration: {str(e)}")
        return None

