from fastapi import APIRouter, HTTPException

from app.models.schemas import ChatRequest, ChatResponse
from app.core.config import settings
from app.services.vector_store import VectorStore
from app.services.rag_service import RAGService

router = APIRouter()

# Initialize services
vector_store = VectorStore(
    embedding_model=settings.embedding_model,
    vector_db_dir=settings.vector_db_dir
)

rag_service = RAGService(
    vector_store=vector_store,
    groq_api_key=settings.groq_api_key,
    ollama_base_url=settings.ollama_base_url,
    ollama_model=settings.ollama_model
)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the document using RAG"""

    # Check if document exists
    if not vector_store.document_exists(request.document_id):
        raise HTTPException(
            status_code=404,
            detail=f"Document with ID {request.document_id} not found"
        )

    try:
        # Generate answer
        answer, sources = rag_service.generate_answer(
            document_id=request.document_id,
            question=request.message,
            top_k=3
        )

        return ChatResponse(
            response=answer,
            sources=sources
        )

    except Exception as e:
        import traceback
        error_detail = f"Error generating response: {str(e)}\n{traceback.format_exc()}"
        print(f"❌ Chat error: {error_detail}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating response: {str(e)}"
        )
