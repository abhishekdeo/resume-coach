from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from app.services import analyze_resume, continue_chat
from app.models import AnalyzeRequest, ResumeResponse, ChatRequest, ChatResponse
import PyPDF2
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173'],  # Updated for frontend security
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

@app.post('/analyze', response_model=ResumeResponse)
async def analyze_endpoint(request: AnalyzeRequest = None, file: UploadFile = File(None), job_description: str = Form(None), job_file: UploadFile = File(None)):
    if file and not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported for resume")
    if job_file and not job_file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported for job description")
    
    try:
        resume_text = ""
        job_description_text = job_description or ""
        
        # Handle JSON payload (text-based resume and job description)
        if request:
            resume_text = request.resume if request.resume else ""
            job_description_text = request.job_description if request.job_description else job_description_text
        
        # Handle resume PDF
        if file:
            contents = await file.read()
            pdf_file = io.BytesIO(contents)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            resume_text = ""
            for page in pdf_reader.pages:
                resume_text += page.extract_text() or ""
            if not resume_text.strip():
                raise HTTPException(status_code=400, detail="No text could be extracted from the resume PDF")
        
        # Handle job description PDF
        if job_file:
            contents = await job_file.read()
            pdf_file = io.BytesIO(contents)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            job_description_text = ""
            for page in pdf_reader.pages:
                job_description_text += page.extract_text() or ""
            if not job_description_text.strip():
                raise HTTPException(status_code=400, detail="No text could be extracted from the job description PDF")
        
        # Validate inputs
        if not resume_text or not job_description_text:
            raise HTTPException(status_code=400, detail="Both resume and job description are required")
        
        feedback, session_id = analyze_resume(resume_text, job_description_text)
        return ResumeResponse(feedback=feedback, session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post('/chat', response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    feedback = continue_chat(request.session_id, request.message)
    return ChatResponse(feedback=feedback)