from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import documents, chat, podcast

app = FastAPI(
    title="NotebookLM Clone API",
    description="API for RAG-based document chat and podcast generation",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(podcast.router, prefix="/api/podcast", tags=["podcast"])


@app.get("/")
async def root():
    """API health check"""
    return {
        "message": "NotebookLM Clone API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}
