from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1.router import api_router
from app.core.security_middleware import (
    limiter,
    security_headers_middleware,
    request_logging_middleware,
    rate_limit_exceeded_handler
)
from slowapi.errors import RateLimitExceeded
import logging

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    description="AI-Powered Multilingual Content Localization Engine for Skill Courses"
)

# Add rate limiter state
app.state.limiter = limiter

# Add rate limit exceeded handler
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Security Middleware (MUST be first)
app.middleware("http")(security_headers_middleware)
app.middleware("http")(request_logging_middleware)

# CORS Middleware (Production: restrict to specific domains)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:8081",
        "http://127.0.0.1:8081",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
        # TODO: In production, replace with:
        # "https://vaanipath.com",
        # "https://www.vaanipath.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Include Community Feature Routes
from app.features.community.routes import communities, competitions, gyan_points, posts

app.include_router(communities.router, prefix="/api/v1/communities", tags=["communities"])
app.include_router(competitions.router, prefix="/api/v1/competitions", tags=["competitions"])
app.include_router(gyan_points.router, prefix="/api/v1/gyan-points", tags=["gyan-points"])
app.include_router(posts.router, prefix="/api/v1/posts", tags=["posts"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Gyanify Localization Engine API",
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
