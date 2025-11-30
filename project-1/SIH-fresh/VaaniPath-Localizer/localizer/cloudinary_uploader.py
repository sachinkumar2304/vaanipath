"""
Cloudinary uploader utility for VaaniPath-Localizer
Uploads generated videos directly to Cloudinary
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
    
    Args:
        file_path: Path to the video file
        video_id: Video ID for organizing
        language: Target language code
        content_type: 'video', 'audio', or 'document'
    
    Returns:
        Cloudinary URL or None if upload fails
    """
    try:
        # Initialize if not already done
        if not cloudinary.config().cloud_name:
            if not init_cloudinary():
                return None
        
        logger.info(f"📤 Uploading {file_path} to Cloudinary...")
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            file_path,
            resource_type='video',  # Even for audio
            public_id=f"dubbed/{content_type}/{video_id}/{language}",
            folder=f"gyanify/dubbed/{content_type}",
            overwrite=True,
            tags=["gyanify", "dubbed", language, content_type]
        )
        
        secure_url = result.get('secure_url')
        logger.info(f"✅ Upload successful: {secure_url}")
        
        return secure_url
        
    except Exception as e:
        logger.error(f"❌ Cloudinary upload failed: {e}")
        return None
