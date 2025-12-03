import httpx
import base64
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class RoadmapRequest(BaseModel):
    current_skills: str
    goal: str
    language: str

@router.post("/roadmap")
async def generate_roadmap(request: RoadmapRequest):
    """
    Generate a personalized career roadmap using the external AI service.
    Proxies the request to n8n webhook with secure credentials.
    """
    # Hardcoded credentials as per instructions (in production, use env vars)
    username = "Gyanify"
    password = "Gyanify123"
    
    # Create Basic Auth header
    auth_string = f"{username}:{password}"
    auth_bytes = auth_string.encode('ascii')
    base64_bytes = base64.b64encode(auth_bytes)
    base64_auth = base64_bytes.decode('ascii')
    
    url = "https://zaiddd.app.n8n.cloud/webhook/8be78b34-dbc8-418a-83b0-044991ac14c2"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {base64_auth}"
    }
    
    payload = {
        "current-skills": request.current_skills,
        "goal": request.goal,
        "language": request.language
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers, timeout=60.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"AI Service Error: {e.response.text}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

class PodcastRequest(BaseModel):
    text: str
    language: str = "english"

@router.post("/generate-podcast")
async def generate_podcast(request: PodcastRequest):
    """
    Generate a podcast from text using the Localizer service.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8001/podcast/generate",
                json=request.dict(),
                timeout=300.0  # Long timeout for audio generation
            )
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Podcast Service Error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
