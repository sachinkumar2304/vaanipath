"""
Cloudinary uploader utility for VaaniPath-Localizer
Uploads generated videos directly to Cloudinary with organized folder structure
"""
import os
import cloudinary
import cloudinary.uploader
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def init_cloudinary():
    """Initialize Cloudinary with environment variables"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        cloudinary.config(
            cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
            api_key=os.getenv('CLOUDINARY_API_KEY'),
            api_secret=os.getenv('CLOUDINARY_API_SECRET')
        )
        logger.info("✅ Cloudinary configured successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to configure Cloudinary: {e}")
        return False

def upload_video_to_cloudinary(
    file_path: str,
    video_id: str,
    language: str,
    content_type: str = 'video'
) -> Optional[str]:
    """
    Upload video to Cloudinary and return URL
    
    Folder Structure:
    - gyanify/original/  → Original uploaded videos
    - gyanify/dubbed/    → Dubbed/translated videos
    - gyanify/audio/     → Audio-only files
    
    Args:
        file_path: Path to the video file
        video_id: Video ID for organizing
        language: Target language code
        content_type: 'original', 'video' (dubbed), or 'audio'
    
    Returns:
        Cloudinary URL or None if upload fails
    """
    try:
        # Initialize if not already done
        if not cloudinary.config().cloud_name:
            if not init_cloudinary():
                return None
        
        logger.info(f"📤 Uploading {file_path} to Cloudinary...")
        
        # Determine folder based on content type
        resource_type = 'video'
        if content_type == 'original':
            # Original videos: gyanify/original/{video_id}
            folder = "gyanify/original"
            public_id = f"gyanify/original/{video_id}"
            tags = ["gyanify", "original", language]
        elif content_type == 'audio':
            # Audio files: gyanify/audio/{video_id}_{language}
            folder = "gyanify/audio"
            public_id = f"gyanify/audio/{video_id}_{language}"
            tags = ["gyanify", "audio", language]
        elif content_type == 'subtitle':
            # Subtitle files: gyanify/subtitles/{video_id}_{language}
            folder = "gyanify/subtitles"
            public_id = f"gyanify/subtitles/{video_id}_{language}"
            tags = ["gyanify", "subtitle", language]
            resource_type = 'raw'
        else:  # dubbed video
            # Dubbed videos: gyanify/dubbed/{video_id}_{language}
            folder = "gyanify/dubbed"
            public_id = f"gyanify/dubbed/{video_id}_{language}"
            tags = ["gyanify", "dubbed", language]
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            file_path,
            resource_type=resource_type,  # Works for both video and audio
            public_id=public_id,
            folder=folder,
            overwrite=True,
            tags=tags
        )
        
        secure_url = result.get('secure_url')
        logger.info(f"✅ Upload successful: {secure_url}")
        logger.info(f"📁 Folder: {folder}")
        
        return secure_url
        
    except Exception as e:
        logger.error(f"❌ Cloudinary upload failed: {e}")
        return None
