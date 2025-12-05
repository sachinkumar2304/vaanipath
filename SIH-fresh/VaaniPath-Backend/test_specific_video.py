import requests

def test_specific_video():
    video_id = "334828f7-e263-4f03-855d-85cca59c2954"  # From the URL in screenshot
    url = f"http://localhost:8000/api/v1/videos/{video_id}"
    
    # First get auth token
    login_response = requests.post(
        "http://localhost:8000/api/v1/auth/login",
        json={"email": "test@example.com", "password": "password123"}
    )
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return
        
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get specific video
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Video Title: {data.get('title')}")
            print(f"Cloudinary URL: {data.get('file_url')}")
            print(f"Status: {data.get('status')}")
            print(f"Content Type: {data.get('content_type')}")
            
            if not data.get('file_url'):
                print("\n⚠️ WARNING: Video has no file_url in database!")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_specific_video()
