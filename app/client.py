import requests

BASE_URL = "http://127.0.0.1:8000"

# Test /analyze endpoint
analyze_payload = {
    "resume": "Experienced Python developer skilled in Django, FastAPI, SQL, and cloud deployments.",
    "job_description": "Looking for a Senior Backend Engineer with expertise in Python, AWS, and team leadership."
}

print("Testing /analyze endpoint...")
analyze_response = requests.post(f"{BASE_URL}/analyze", json=analyze_payload)

if analyze_response.status_code == 200:
    print("✅ /analyze Response:")
    print(analyze_response.json())
    session_id = analyze_response.json().get("session_id")
else:
    print("❌ /analyze Error:", analyze_response.status_code, analyze_response.text)
    session_id = None

# Test /chat endpoint if session_id is available
if session_id:
    chat_payload = {
        "session_id": session_id,
        "message": "How can I improve the gaps you mentioned in my resume?"
    }
    print("\nTesting /chat endpoint...")
    chat_response = requests.post(f"{BASE_URL}/chat", json=chat_payload)
    if chat_response.status_code == 200:
        print("✅ /chat Response:")
        print(chat_response.json())
    else:
        print("❌ /chat Error:", chat_response.status_code, chat_response.text)