from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.models.schemas import PodcastGenerationRequest, PodcastGenerationResponse
from app.core.config import settings
from app.services.vector_store import VectorStore
from app.services.podcast_service import PodcastService

router = APIRouter()

# Initialize services
vector_store = VectorStore(
    embedding_model=settings.embedding_model,
    vector_db_dir=settings.vector_db_dir
)

podcast_service = PodcastService(
    vector_store=vector_store,
    audio_output_dir=settings.audio_output_dir,
    groq_api_key=settings.groq_api_key,
    elevenlabs_api_key=settings.elevenlabs_api_key,
    ollama_base_url=settings.ollama_base_url,
    ollama_model=settings.ollama_model,
    max_duration=settings.max_podcast_duration
)


@router.post("/generate", response_model=PodcastGenerationResponse)
async def generate_podcast(request: PodcastGenerationRequest):
    """Generate a podcast from document content"""

    # Check if document exists
    if not vector_store.document_exists(request.document_id):
        raise HTTPException(
            status_code=404,
            detail=f"Document with ID {request.document_id} not found"
        )

    try:
        # Generate podcast
        audio_path, duration, transcript = podcast_service.create_podcast(
            document_id=request.document_id,
            target_duration=request.duration
        )

        return PodcastGenerationResponse(
            audio_url=f"/api/podcast/download/{request.document_id}",
            duration=duration,
            transcript=transcript,
            message="Podcast generated successfully"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating podcast: {str(e)}"
        )


@router.get("/download/{document_id}")
async def download_podcast(document_id: str):
    """Download generated podcast audio"""
    audio_file = settings.audio_output_dir / f"podcast_{document_id}.mp3"

    if not audio_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Podcast audio not found. Please generate the podcast first."
        )

    return FileResponse(
        path=str(audio_file),
        media_type="audio/mpeg",
        filename=f"podcast_{document_id}.mp3"
    )
