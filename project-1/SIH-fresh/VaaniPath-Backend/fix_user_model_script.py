import os

if os.path.exists("app/models/user.py"):
    os.remove("app/models/user.py")

content = """from pydantic import BaseModel, EmailStr
from typing import Optional, Union
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    is_admin: bool = False
    is_teacher: bool = False

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: str
    created_at: Union[datetime, str, None] = None
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[str] = None

class TutorCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class TutorResponse(BaseModel):
    id: str
    email: str
    full_name: str
    is_teacher: bool = True
    created_at: str
    temporary_password: str
"""
with open("app/models/user.py", "w") as f:
    f.write(content)
