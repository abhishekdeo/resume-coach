from pydantic import BaseModel
from typing import Optional

class AnalyzeRequest(BaseModel):
    resume: str
    job_description: str

class ResumeResponse(BaseModel):
    feedback: str
    session_id: Optional[str] = None  # Optional in case of errors

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    feedback: str