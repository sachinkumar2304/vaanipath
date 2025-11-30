#!/usr/bin/env python3
"""
Test signup endpoint
"""
import requests
import json

url = "http://127.0.0.1:8001/api/v1/auth/signup"
data = {
    "email": "testuser999@example.com",
    "password": "Test@123",
    "full_name": "Test User",
    "is_admin": True
}

print("Testing signup endpoint...")
print(f"URL: {url}")
print(f"Data: {json.dumps(data, indent=2)}")
print("\n" + "="*60)

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
