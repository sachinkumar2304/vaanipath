from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime

class EnrollmentCreate(BaseModel):
    course_id: str

class VideoProgress(BaseModel):
    completed: bool = False
    watched_duration: float = 0.0
    last_watched_at: Optional[datetime] = None

class EnrollmentProgress(BaseModel):
    video_id: str
    completed: bool = False
    watched_duration: float = 0.0

class EnrollmentResponse(BaseModel):
    id: str
    student_id: str
    course_id: str
    enrolled_at: datetime
    progress: Optional[Dict[str, dict]] = {}  # {video_id: {completed, watched_duration}}
    # Computed fields
    course_title: Optional[str] = None
    course_thumbnail: Optional[str] = None
    total_videos: Optional[int] = 0
    completed_videos: Optional[int] = 0
    progress_percentage: Optional[float] = 0.0

class EnrollmentList(BaseModel):
    enrollments: List[EnrollmentResponse]
    total: int
