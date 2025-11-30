from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class TranslationRequest(BaseModel):
    text: str
    source_language: str
    target_language: str

class TranslationResponse(BaseModel):
    translated_text: str
    source_language: str
    target_language: str
    confidence: Optional[float] = None

class GlossaryCreate(BaseModel):
    source_term: str
    target_term: str
    source_language: str
    target_language: str
    domain: Optional[str] = None

class GlossaryTerm(BaseModel):
    id: str
    source_term: str
    target_term: str
    source_language: str
    target_language: str
    domain: Optional[str] = None
    created_at: datetime

class QualityMetrics(BaseModel):
    accuracy: float
    fluency: float
    consistency: float
    overall_score: float
