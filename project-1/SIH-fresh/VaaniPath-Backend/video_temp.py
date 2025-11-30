from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class VideoStatus(str, Enum):
    """Video processing status"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    TRANSCRIBING = "transcribing"
    TRANSLATING = "translating"
    GENERATING_AUDIO = "generating_audio"
    LIP_SYNCING = "lip_syncing"
    REVIEW_PENDING = "review_pending"
    COMPLETED = "completed"
    FAILED = "failed"


class DomainType(str, Enum):
    """Course domain types"""
    IT = "it"
    HEALTHCARE = "healthcare"
    CONSTRUCTION = "construction"
    MANUFACTURING = "manufacturing"
    AGRICULTURE = "agriculture"
    HOSPITALITY = "hospitality"
    AUTOMOTIVE = "automotive"
    RETAIL = "retail"
    OTHER = "other"


class VideoUpload(BaseModel):
    """Video upload request"""
    title: str
    description: Optional[str] = None
    domain: DomainType
    source_language: str = "en"
    target_languages: List[str]


class VideoResponse(BaseModel):
    """Video response model"""
    id: str
    title: str
    description: Optional[str]
    domain: DomainType
    source_language: str
    target_languages: List[str]
    status: VideoStatus
    uploaded_by: str
    file_url: str
    duration: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class VideoProgress(BaseModel):
    """Video processing progress"""
    video_id: str
    status: VideoStatus
    progress_percentage: int
    current_step: str
    estimated_time_remaining: Optional[int] = None  # in seconds
    error_message: Optional[str] = None


class TranslatedVideo(BaseModel):
    """Translated video output"""
    id: str
    original_video_id: str
    language: str
    video_url: str
    subtitle_url: Optional[str] = None
    audio_url: Optional[str] = None
    quality_score: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class VideoList(BaseModel):
    """Paginated video list"""
    videos: List[VideoResponse]
    total: int
    page: int
    page_size: int
