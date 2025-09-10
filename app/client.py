import requests
import os

BASE_URL = "http://127.0.0.1:8000"

def test_analyze_endpoint(pdf_path=None, resume_text=None, job_description=None):
    url = f"{BASE_URL}/analyze"
    if not job_description:
        job_description = "Looking for a Senior Backend Engineer with expertise in Python, AWS, and team leadership."
    
    try:
        if pdf_path:
            if not os.path.exists(pdf_path):
                print("Error: PDF file not found")
                return None
            with open(pdf_path, "rb") as file:
                files = {"file": (os.path.basename(pdf_path), file, "application/pdf")}
                data = {"job_description": job_description}
                response = requests.post(url, files=files, data=data)
        else:
            if not resume_text:
                print("Error: Resume text or PDF file must be provided")
                return None
            data = {
                "resume": resume_text,
                "job_description": job_description
            }
            response = requests.post(url, json=data)
        
        if response.status_code == 200:
            print("✅ /analyze Response:")
            print(response.json())
            return response.json().get("session_id")
        else:
            print("❌ /analyze Error:", response.status_code, response.json())
            return None
    except Exception as e:
        print("Exception:", str(e))
        return None

def test_chat_endpoint(session_id, message):
    url = f"{BASE_URL}/chat"
    data = {"session_id": session_id, "message": message}
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print("✅ /chat Response:")
            print(response.json())
        else:
            print("❌ /chat Error:", response.status_code, response.json())
    except Exception as e:
        print("Exception:", str(e))

if __name__ == "__main__":
    # Test with PDF file
    session_id = test_analyze_endpoint(pdf_path="sample_resume.pdf")
    
    # Test with text input (uncomment to use)
    # resume_text = "Experienced Python developer skilled in Django, FastAPI, SQL, and cloud deployments."
    # session_id = test_analyze_endpoint(resume_text=resume_text)
    
    # Test /chat endpoint if session_id is available
    if session_id:
        chat_message = "How can I improve the gaps you mentioned in my resume?"
        test_chat_endpoint(session_id, chat_message)