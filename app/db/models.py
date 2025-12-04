"""Database models for the localisation engine."""
from sqlalchemy import Column, String, Integer, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.db.database import Base


class JobStatus(str, enum.Enum):
    """Job processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    READY_FOR_USE = "ready_for_use"
    ERROR = "error"
    COMPLETED = "completed"


class Job(Base):
    """Job model for tracking video processing."""
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    original_filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # mp4, mkv, mp3, wav, pdf, docx, txt
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    error_message = Column(String, nullable=True)
    metadata = Column(JSON, nullable=True)  # Store additional info like duration, languages processed, etc.
    
    def to_dict(self):
        """Convert job to dictionary."""
        return {
            "id": self.id,
            "original_filename": self.original_filename,
            "file_type": self.file_type,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "error_message": self.error_message,
            "metadata": self.metadata
        }



