from pydantic import BaseModel
from typing import Optional

class AnalyzeRequest(BaseModel):
    resume: Optional[str] = None  # Allow resume to be optional for PDF uploads
    job_description: Optional[str] = None  # Allow job_description to be optional for flexibility

class ResumeResponse(BaseModel):
    feedback: str
    session_id: Optional[str] = None  # Optional in case of errors

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    feedback: str