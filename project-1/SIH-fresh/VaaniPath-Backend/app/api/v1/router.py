from fastapi import APIRouter
from app.api.v1.endpoints import auth, admin, teacher, videos, processing, translation, review, quiz, doubts, courses, enrollments
from app.features.community.routes import communities, posts, competitions, gyan_points

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(teacher.router, prefix="/teacher", tags=["teacher"])
api_router.include_router(videos.router, prefix="/videos", tags=["videos"])
api_router.include_router(processing.router, prefix="/processing", tags=["processing"])
api_router.include_router(translation.router, prefix="/translation", tags=["translation"])
api_router.include_router(review.router, prefix="/reviews", tags=["reviews"])
api_router.include_router(quiz.router, prefix="/quiz", tags=["quiz"])
api_router.include_router(doubts.router, prefix="/doubts", tags=["doubts"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
api_router.include_router(enrollments.router, prefix="/enrollments", tags=["enrollments"])

# Community Feature Routes
api_router.include_router(communities.router, prefix="/community", tags=["community"])
api_router.include_router(posts.router, prefix="/community", tags=["community"])
api_router.include_router(competitions.router, prefix="/community", tags=["community"])
api_router.include_router(gyan_points.router, prefix="/community", tags=["community"])
