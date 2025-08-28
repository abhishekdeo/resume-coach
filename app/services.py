import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))

template = """
You are a resume coach. Compare the following resume with the job description.
- Assess fit
- Identify gaps
- Highlight strengths
- Provide 3 actionable tips

Resume:
{resume}

Job Description:
{job_description}
"""

prompt = ChatPromptTemplate.from_template(template)

def analyze_resume(resume: str, job_description: str) -> str:
    response = llm.invoke(prompt.format(resume=resume, job_description=job_description))
    return response.content
