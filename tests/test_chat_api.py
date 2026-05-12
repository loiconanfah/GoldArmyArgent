from fastapi.testclient import TestClient
from api.main import app
import json

# Bypass auth for testing
from api.main import get_current_user
app.dependency_overrides[get_current_user] = lambda: {"id": "test_user_for_debugging", "email": "test@goldarmy.com"}

def test_chat():
    with TestClient(app) as client:
        payload = {
            "message": "",
            "cv_text": "Je suis un test sans vrai JSON.",
            "cv_filename": "CV_Test.pdf",
            "nb_results": 0,
            "location": "",
            "session_id": "test_123"
        }
        response = client.post("/api/chat", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    test_chat()
