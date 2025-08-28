import requests

API_URL = "http://127.0.0.1:8000/analyze"

sample_payload = {
    "resume": "Experienced Python developer skilled in Django, FastAPI, SQL, and cloud deployments.",
    "job_description": "Looking for a Senior Backend Engineer with expertise in Python, AWS, and team leadership."
}

response = requests.post(API_URL, json=sample_payload)

if response.status_code == 200:
    print("✅ API Response:")
    print(response.json())
else:
    print("❌ Error:", response.status_code, response.text)
