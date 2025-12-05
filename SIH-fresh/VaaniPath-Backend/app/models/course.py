from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime

class CourseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    domain: str
    source_language: str = "en"
    target_languages: List[str]

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    domain: Optional[str] = None
    source_language: Optional[str] = None
    target_languages: Optional[List[str]] = None

class CourseResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    teacher_id: str
    teacher_name: Optional[str] = None
    domain: str
    source_language: str
    target_languages: List[str]
    created_at: datetime
    updated_at: Optional[datetime] = None
    total_videos: Optional[int] = 0
    total_duration: Optional[float] = 0

    @field_validator('target_languages', mode='before')
    def parse_target_languages(cls, v):
        if isinstance(v, str):
            try:
                import json
                return json.loads(v)
            except json.JSONDecodeError:
                return []
        return v

class CourseList(BaseModel):
    courses: List[CourseResponse]
    total: int
    page: int
    page_size: int

class CourseWithVideos(CourseResponse):
    videos: List[dict]  # Will contain VideoResponse objects
