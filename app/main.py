from fastapi import FastAPI
from app.models import ResumeRequest, ResumeResponse
from app.services import analyze_resume

app = FastAPI(title="Resume Coach API")

@app.post("/analyze", response_model=ResumeResponse)
def analyze_resume_api(request: ResumeRequest):
    analysis = analyze_resume(request.resume, request.job_description)
    return ResumeResponse(analysis=analysis)
