from langchain_openai import ChatOpenAI
from langchain_community.llms.sagemaker_endpoint import SagemakerEndpoint
from langchain_community.llms.sagemaker_endpoint import ContentHandlerBase
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
import uuid
import os
import json
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()
chat_sessions = {}

class SageMakerContentHandler(ContentHandlerBase):
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, prompt: str, model_kwargs: dict) -> bytes:
        input_str = json.dumps({"inputs": prompt, "parameters": model_kwargs})
        return input_str.encode("utf-8")

    def transform_output(self, output: bytes) -> str:
        response_json = json.loads(output.read().decode("utf-8"))
        return response_json[0]["generated_text"]

def get_llm(model_type: str):
    if model_type == "openai":
        return ChatOpenAI(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.7
        )
    elif model_type == "llama2":
        return SagemakerEndpoint(
            endpoint_name="llama2-resume-coach",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            model_kwargs={"max_new_tokens": 512, "temperature": 0.7},
            content_handler=SageMakerContentHandler()
        )
    else:
        raise ValueError(f"Unsupported model type: {model_type}")

analyze_template = '''
You are a resume coach. Compare the following resume with the job description and provide a structured analysis:
- **Fit Assessment**: On a scale of 0-100, rate the candidate's fit and explain why.
- **Gaps Identified**: List specific skills, experiences, or qualifications missing from the resume that are required by the job description.
- **Strengths Highlighted**: Identify unique strengths or transferable skills that make the candidate a strong fit.
- **Actionable Tips**: Provide 3 actionable recommendations to improve the candidate's fit for the role.
- **ATS Keywords**: Suggest 5 keywords to optimize the resume for applicant tracking systems.
- **Career Path Suggestions**: If the fit is low, recommend alternative roles or steps to transition toward the target role.
- **Cover Letter Snippet**: Write a short, tailored cover letter paragraph (3-4 sentences) for this job.

Resume:
{resume}

Job Description:
{job_description}
'''

chat_template = '''
You are a resume coach. Based on the previous analysis and conversation history, respond to the user's query with actionable advice to improve their resume or job application strategy.

Conversation History:
{history}

User Query:
{query}
'''

def analyze_resume(resume: str, job_description: str, model_type: str = "openai") -> tuple[str, str]:
    session_id = str(uuid.uuid4())
    llm = get_llm(model_type)

    prompt = ChatPromptTemplate.from_messages([
        ("system", analyze_template),
        ("human", "Resume: {resume}\nJob Description: {job_description}")
    ])
    chain = prompt | llm
    feedback = chain.invoke({"resume": resume, "job_description": job_description}).content
    chat_sessions[session_id] = [HumanMessage(content=resume), AIMessage(content=feedback)]
    logger.debug(f"Session {session_id} created with history: {chat_sessions[session_id]}")
    return feedback, session_id

def continue_chat(session_id: str, message: str, model_type: str = "openai") -> str:
    if session_id not in chat_sessions:
        raise ValueError("Invalid session ID. Please analyze a resume first.")
    
    llm = get_llm(model_type)
    history = "\n".join([f"{msg.__class__.__name__}: {msg.content}" for msg in chat_sessions[session_id]])
    prompt = ChatPromptTemplate.from_template(chat_template)
    chain = prompt | llm
    response = chain.invoke({"history": history or "No prior analysis available", "query": message}).content
    chat_sessions[session_id].extend([HumanMessage(content=message), AIMessage(content=response)])
    logger.debug(f"Session {session_id} history: {history}")
    logger.debug(f"Updated session {session_id}: {chat_sessions[session_id]}")
    return response