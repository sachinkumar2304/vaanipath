from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    is_admin: bool = False

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    user_type: str = "student"
    is_teacher: bool = False
    is_admin: bool = False
    avatar_url: Optional[str] = None
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Tutor Models
class TutorCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    bio: Optional[str] = None
    expertise: Optional[List[str]] = []

class TutorResponse(BaseModel):
    id: str
    email: str
    full_name: str
    bio: Optional[str] = None
    expertise: Optional[List[str]] = []
    created_at: datetime
    is_approved: bool = False
