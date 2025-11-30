from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class ReviewCreate(BaseModel):
    video_id: str
    rating: int
    comment: Optional[str] = None

class ReviewResponse(BaseModel):
    id: str
    video_id: str
    user_id: str
    user_name: str
    rating: int
    comment: Optional[str] = None
    created_at: datetime

class PendingReview(BaseModel):
    id: str
    content: str
    content_type: str
    submitted_by: str
    submitted_at: datetime
    status: str = "pending"

class ReviewStats(BaseModel):
    total_reviews: int
    average_rating: float
    rating_distribution: Dict[int, int]
