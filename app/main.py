from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services import analyze_resume, continue_chat
from app.models import AnalyzeRequest, ResumeResponse, ChatRequest, ChatResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # Change to ['http://localhost:5173'] for security once frontend is ready
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

@app.post('/analyze', response_model=ResumeResponse)
async def analyze_endpoint(request: AnalyzeRequest):
    feedback, session_id = analyze_resume(request.resume, request.job_description)
    return ResumeResponse(feedback=feedback, session_id=session_id)

@app.post('/chat', response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    feedback = continue_chat(request.session_id, request.message)
    return ChatResponse(feedback=feedback)