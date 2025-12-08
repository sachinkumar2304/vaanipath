from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import shutil

from app.models.schemas import DocumentUploadResponse
from app.core.config import settings
from app.services.pdf_processor import PDFProcessor
from app.services.vector_store import VectorStore

router = APIRouter()

# Initialize services
pdf_processor = PDFProcessor(
    chunk_size=settings.chunk_size,
    chunk_overlap=settings.chunk_overlap
)

vector_store = VectorStore(
    embedding_model=settings.embedding_model,
    vector_db_dir=settings.vector_db_dir
)


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a PDF document"""

    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Save uploaded file
    file_path = settings.upload_dir / file.filename

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process PDF
        document_id, chunks = pdf_processor.process_pdf(file_path)

        # Add to vector store
        chunks_count = vector_store.add_document(document_id, chunks)

        return DocumentUploadResponse(
            document_id=document_id,
            filename=file.filename,
            chunks_count=chunks_count,
            message="Document uploaded and processed successfully"
        )

    except Exception as e:
        # Clean up on error
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


@router.get("/documents/{document_id}/exists")
async def check_document_exists(document_id: str):
    """Check if a document exists in the vector store"""
    exists = vector_store.document_exists(document_id)
    return {"exists": exists, "document_id": document_id}
