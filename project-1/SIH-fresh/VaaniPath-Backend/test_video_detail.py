import requests

def test_video_detail_endpoint():
    video_id = "334828f7-e263-4f03-855d-85cca59c2954"
    
    # Login
    login_response = requests.post(
        "http://localhost:8000/api/v1/auth/login",
        json={"email": "test@example.com", "password": "password123"}
    )
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get video detail
    response = requests.get(f"http://localhost:8000/api/v1/videos/{video_id}", headers=headers)
    
    print("=== Video Detail Response ===")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nTitle: {data.get('title')}")
        print(f"file_url: {data.get('file_url')}")
        print(f"cloudinary_url: {data.get('cloudinary_url')}")
        print(f"status: {data.get('status')}")
        
        print("\n=== Full Response ===")
        import json
        print(json.dumps(data, indent=2))

if __name__ == "__main__":
    test_video_detail_endpoint()
