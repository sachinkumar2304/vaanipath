import requests

def check_video_and_url():
    video_id = "334828f7-e263-4f03-855d-85cca59c2954"
    
    # Login
    login_response = requests.post(
        "http://localhost:8000/api/v1/auth/login",
        json={"email": "test@example.com", "password": "password123"}
    )
    
    if login_response.status_code != 200:
        print("Login failed")
        return
        
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get video details
    response = requests.get(f"http://localhost:8000/api/v1/videos/{video_id}", headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to get video: {response.status_code}")
        return
    
    data = response.json()
    
    print("=== VIDEO DETAILS ===")
    print(f"Title: {data.get('title')}")
    print(f"Content Type: {data.get('content_type')}")
    print(f"file_url: {data.get('file_url')}")
    print(f"\n=== TESTING CLOUDINARY URL ===")
    
    cloudinary_url = data.get('file_url')
    
    if not cloudinary_url:
        print("❌ NO URL FOUND!")
        return
    
    # Try to access the Cloudinary URL
    try:
        print(f"Testing URL: {cloudinary_url}")
        video_response = requests.head(cloudinary_url, timeout=10)
        print(f"Status: {video_response.status_code}")
        print(f"Content-Type: {video_response.headers.get('Content-Type')}")
        
        if video_response.status_code == 200:
            print("✅ Cloudinary URL is accessible!")
        else:
            print(f"❌ Cloudinary returned: {video_response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing Cloudinary: {e}")

if __name__ == "__main__":
    check_video_and_url()
