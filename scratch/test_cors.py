import requests

url = "http://127.0.0.1:8000/api/auth/login"
headers = {
    "Origin": "http://localhost:5173",
    "Content-Type": "application/x-www-form-urlencoded"
}
data = {
    "username": "yayzoy@gmail.com",
    "password": "GoldArmy2026!"
}

print("Testing POST with localhost:5173 Origin...")
try:
    response = requests.post(url, headers=headers, data=data, timeout=5)
    print("Status Code:", response.status_code)
    print("Response Headers:")
    for k, v in response.headers.items():
        if "access-control" in k.lower():
            print(f"  {k}: {v}")
except Exception as e:
    print("Error:", e)

headers_ip = {
    "Origin": "http://127.0.0.1:5173",
    "Content-Type": "application/x-www-form-urlencoded"
}
print("\nTesting POST with 127.0.0.1:5173 Origin...")
try:
    response = requests.post(url, headers=headers_ip, data=data, timeout=5)
    print("Status Code:", response.status_code)
    print("Response Headers:")
    for k, v in response.headers.items():
        if "access-control" in k.lower():
            print(f"  {k}: {v}")
except Exception as e:
    print("Error:", e)
