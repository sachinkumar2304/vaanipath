import requests

def test_login():
    url = "http://localhost:8000/api/v1/auth/login"
    payload = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Login Successful!")
            token = response.json().get("access_token")
            if token:
                print("✅ Token received")
                
                # Verify /me endpoint
                headers = {"Authorization": f"Bearer {token}"}
                me_response = requests.get("http://localhost:8000/api/v1/auth/me", headers=headers)
                print(f"Me Endpoint Status: {me_response.status_code}")
                print(f"Me Response: {me_response.json()}")
            else:
                print("❌ No token in response")
        else:
            print("❌ Login Failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_login()
