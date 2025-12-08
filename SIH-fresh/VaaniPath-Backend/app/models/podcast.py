from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PodcastCreate(BaseModel):
    title: str
    description: Optional[str] = None
    language: str
    audio_url: str
    duration: Optional[float] = None
    transcript: Optional[str] = None

class PodcastResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    language: str
    audio_url: str
    created_at: datetime
    duration: Optional[float] = None
