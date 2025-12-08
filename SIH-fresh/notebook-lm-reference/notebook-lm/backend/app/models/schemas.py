from pydantic import BaseModel
from typing import List, Optional


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str
    document_id: str


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str
    sources: Optional[List[str]] = None


class DocumentUploadResponse(BaseModel):
    """Response model for document upload"""
    document_id: str
    filename: str
    chunks_count: int
    message: str


class PodcastGenerationRequest(BaseModel):
    """Request model for podcast generation"""
    document_id: str
    duration: Optional[int] = 180  # Default 3 minutes


class PodcastGenerationResponse(BaseModel):
    """Response model for podcast generation"""
    audio_url: str
    duration: float
    transcript: str
    message: str
