from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class ProcessingStage(str, Enum):
    UPLOAD = "upload"
    TRANSCRIPTION = "transcription"
    TRANSLATION = "translation"
    TTS = "tts"
    DUBBING = "dubbing"
    COMPLETE = "complete"
    FAILED = "failed"
    TRANSCRIBING = "transcription" # Alias for backward compatibility if needed
    COMPLETED = "complete"

class SubtitleFormat(str, Enum):
    VTT = "vtt"
    SRT = "srt"

class ModelSize(str, Enum):
    TINY = "tiny"
    BASE = "base"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"

class VideoProcessRequest(BaseModel):
    source_language: str = "en"
    target_languages: List[str]
    generate_subtitles: bool = True
    use_lip_sync: bool = True
    enable_lip_sync: bool = True # Alias
    generate_quiz: bool = False

class ProcessingStatusResponse(BaseModel):
    video_id: str
    overall_status: ProcessingStage
    progress_percentage: float
    stages: Dict[str, Dict[str, str | int | float]]
    estimated_time_remaining: Optional[int] = None

class TranscriptionRequest(BaseModel):
    video_id: str
    language: str = "en"
    model_size: ModelSize = ModelSize.MEDIUM

class TTSRequest(BaseModel):
    video_id: str
    text: str
    language: str
    voice_id: Optional[str] = None
    voice_gender: str = "female"

class SubtitleRequest(BaseModel):
    video_id: str
    language: str
    format: SubtitleFormat = SubtitleFormat.VTT

class DubbingRequest(BaseModel):
    video_id: str
    language: str
    use_lip_sync: bool = True
    enable_lip_sync: bool = True

class BatchProcessRequest(BaseModel):
    video_ids: List[str]
    target_languages: List[str]

class TranscriptionSegment(BaseModel):
    start: float
    end: float
    text: str
    confidence: Optional[float] = None

class TranscriptionResponse(BaseModel):
    video_id: str
    language: str
    full_text: str
    text: Optional[str] = None # Alias
    segments: Optional[List[TranscriptionSegment]] = None
    duration: float
    created_at: datetime

class TTSResponse(BaseModel):
    video_id: str
    language: str
    audio_url: str
    duration: float
    created_at: datetime

class SubtitleResponse(BaseModel):
    id: str
    video_id: str
    language: str
    format: str
    subtitle_url: str
    created_at: datetime

class DubbingResponse(BaseModel):
    video_id: str
    language: str
    dubbed_video_url: str
    thumbnail_url: Optional[str] = None
    duration: float
    created_at: datetime

class BatchProcessResponse(BaseModel):
    batch_id: str
    total_videos: int
    total_jobs: int
    estimated_time: int
    created_at: datetime

class ModelInfo(BaseModel):
    name: str
    version: str
    type: str
    languages: List[str]
    status: str
    memory_usage_mb: float

class ModelsInfoResponse(BaseModel):
    whisper: ModelInfo
    translation: ModelInfo
    tts: ModelInfo
    total_memory_mb: float
    gpu_available: bool
