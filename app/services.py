import os
import uuid
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from dotenv import load_dotenv

load_dotenv()

llm = None
chat_sessions = {}  # In-memory storage for conversation history (key: session_id, value: list of messages)

analyze_template = '''
You are a resume coach. Compare the following resume with the job description.
- Assess fit
- Identify gaps
- Highlight strengths
- Provide 3 actionable tips

Resume:
{resume}

Job Description:
{job_description}
'''

chat_template = '''
You are a resume coach. Use the full conversation history (including the original resume, job description, and previous feedback) to answer the user's question.
Conversation History:
{history}
User Question:
{message}
'''

analyze_prompt = ChatPromptTemplate.from_template(analyze_template)
chat_prompt = ChatPromptTemplate.from_template(chat_template)

def init_llm():
    global llm
    if llm is None:
        llm = ChatOpenAI(model='gpt-4o-mini', temperature=0, api_key=os.getenv('OPENAI_API_KEY'))

def get_llm():
    global llm
    if llm is None:
        init_llm()
    return llm

def analyze_resume(resume: str, job_description: str) -> tuple[str, str]:
    init_llm()  # Ensure LLM is ready
    session_id = str(uuid.uuid4())
    try:
        response = get_llm().invoke(analyze_prompt.format(resume=resume, job_description=job_description))
        feedback = response.content if response else 'No response from LLM.'

        # Initialize session history
        chat_sessions[session_id] = [
            SystemMessage(content="You are a resume coach."),
            HumanMessage(content=f"Resume: {resume}\nJob Description: {job_description}"),
            AIMessage(content=feedback)
        ]
        return feedback, session_id
    except Exception as e:
        return f"Error analyzing resume: {str(e)}", None

def continue_chat(session_id: str, message: str) -> str:
    init_llm()  # Ensure LLM is ready
    if session_id not in chat_sessions:
        return "Session not found. Please start with /analyze to create a new session."
    try:
        # Append the new user message
        chat_sessions[session_id].append(HumanMessage(content=message))

        # Build history string for the prompt
        history = "\n".join([f"{msg.type}: {msg.content}" for msg in chat_sessions[session_id]])

        # Invoke LLM with history
        response = get_llm().invoke(chat_prompt.format(history=history, message=message))
        feedback = response.content if response else 'No response from LLM.'

        # Append LLM response to history
        chat_sessions[session_id].append(AIMessage(content=feedback))
        return feedback
    except Exception as e:
        return f"Error in chat: {str(e)}"