import requests

response = requests.post(
    "http://localhost:8000/api/auth/login",
    data={"username": "yayzoy@gmail.com", "password": "password123"} # Mock password
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
