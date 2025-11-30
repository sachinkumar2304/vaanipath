import requests

try:
    response = requests.get("http://localhost:8000/docs")
    print(f"Docs Status: {response.status_code}")
    
    response = requests.get("http://localhost:8000/api/v1/auth/me")
    print(f"Auth Me Status (No Token): {response.status_code}")
except Exception as e:
    print(f"Error: {e}")
