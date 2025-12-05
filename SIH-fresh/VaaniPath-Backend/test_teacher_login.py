import requests
import json

def test_teacher_login():
    url = "http://localhost:8000/api/v1/auth/login"
    
    credentials = {
        "email": "newtutor@test.com",
        "password": "password123"
    }
    
    response = requests.post(url, json=credentials)
    
    print(f"Status Code: {response.status_code}\n")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Login Successful!\n")
        print("Full Response:")
        print(json.dumps(data, indent=2))
        
        if "user" in data:
            user = data["user"]
            print(f"\n=== User Data ===")
            print(f"is_teacher: {user.get('is_teacher')}")
            print(f"is_admin: {user.get('is_admin')}")
            print(f"user_type: {user.get('user_type')}")
    else:
        print(f"❌ Login Failed: {response.text}")

if __name__ == "__main__":
    test_teacher_login()
