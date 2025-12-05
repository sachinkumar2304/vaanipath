from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class DoubtCreate(BaseModel):
    video_id: str
    question: str
    timestamp: Optional[float] = None

class DoubtResponse(BaseModel):
    id: str
    video_id: str
    user_id: str
    user_name: str
    question: str
    timestamp: Optional[float] = None
    upvotes: int = 0
    answer: Optional[str] = None
    answered_by: Optional[str] = None
    answered_at: Optional[datetime] = None
    created_at: datetime
    is_resolved: bool = False

class DoubtAnswer(BaseModel):
    answer: str

class DoubtsList(BaseModel):
    doubts: List[DoubtResponse]
    total: int
    page: int
    page_size: int
