from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    answer: str
    sources: List[str] = []

class ChatHistoryItem(BaseModel):
    id: int
    session_id: str
    message: str
    response: str
    
    class Config:
        from_attributes = True

class UserRegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class UserLoginRequest(BaseModel):
    username: str
    password: str

class AuthResponse(BaseModel):
    user_id: int
    username: str
    message: str

from datetime import datetime

class DocumentResponse(BaseModel):
    id: int
    filename: str
    upload_date: datetime
    
    class Config:
        from_attributes = True



