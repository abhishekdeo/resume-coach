from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from app.services import analyze_resume, continue_chat
from app.models import ResumeResponse, ChatRequest, ChatResponse
import PyPDF2
import io
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def preprocess_form_data(
    resume_file: UploadFile = File(None),
    resume_text: str = Form(None, min_length=0),
    job_description: str = Form(None, min_length=0),
    job_file: UploadFile = File(None),
    model_type: str = Form("openai")
):
    logger.debug(f"Raw inputs - resume_file: {resume_file}, type: {type(resume_file)}")
    logger.debug(f"Raw inputs - job_file: {job_file}, type: {type(job_file)}")
    logger.debug(f"Raw inputs - resume_text: {resume_text}, job_description: {job_description}, model_type: {model_type}")
    
    # Convert empty file inputs to None
    resume_file = None if resume_file and not resume_file.filename else resume_file
    job_file = None if job_file and not job_file.filename else job_file
    
    return {
        "resume_file": resume_file,
        "resume_text": resume_text,
        "job_description": job_description,
        "job_file": job_file,
        "model_type": model_type
    }

@app.post("/analyze", response_model=ResumeResponse)
async def analyze_endpoint(form_data: dict = Depends(preprocess_form_data)):
    try:
        resume_content = ""
        job_description_content = form_data["job_description"] or ""

        # Log processed form data
        logger.debug(f"Processed form data: {form_data}")

        # Handle resume input (PDF or string)
        if form_data["resume_file"]:
            if not form_data["resume_file"].filename.endswith(".pdf"):
                raise HTTPException(status_code=400, detail="Resume must be a PDF file")
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(await form_data["resume_file"].read()))
            for page in pdf_reader.pages:
                resume_content += page.extract_text() or ""
        elif form_data["resume_text"] is not None and form_data["resume_text"].strip():
            resume_content = form_data["resume_text"]
        else:
            raise HTTPException(status_code=400, detail="Resume (file or text) is required")

        # Handle job description input (PDF or string)
        if form_data["job_file"]:
            if not form_data["job_file"].filename.endswith(".pdf"):
                raise HTTPException(status_code=400, detail="Job description must be a PDF file")
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(await form_data["job_file"].read()))
            for page in pdf_reader.pages:
                job_description_content += page.extract_text() or ""
        elif form_data["job_description"] is not None and form_data["job_description"].strip():
            job_description_content = form_data["job_description"]
        else:
            raise HTTPException(status_code=400, detail="Job description (file or text) is required")

        if not resume_content.strip():
            raise HTTPException(status_code=400, detail="Resume content is empty or unreadable")
        if not job_description_content.strip():
            raise HTTPException(status_code=400, detail="Job description content is empty or unreadable")

        feedback, session_id = analyze_resume(resume_content, job_description_content, form_data["model_type"])
        return ResumeResponse(feedback=feedback, session_id=session_id)
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, model_type: str = Query("openai")):
    try:
        feedback = continue_chat(request.session_id, request.message, model_type)
        return ChatResponse(feedback=feedback)
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")