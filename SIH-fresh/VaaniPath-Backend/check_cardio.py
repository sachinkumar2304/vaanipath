import requests

def check_cardio_video():
    # Login
    login_response = requests.post(
        "http://localhost:8000/api/v1/auth/login",
        json={"email": "test@example.com", "password": "password123"}
    )
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get all videos to find Cardio
    response = requests.get("http://localhost:8000/api/v1/videos/?page=1&page_size=100", headers=headers)
    
    if response.status_code == 200:
        videos = response.json()['videos']
        cardio_videos = [v for v in videos if 'cardio' in v.get('title', '').lower()]
        
        print(f"Found {len(cardio_videos)} Cardio video(s)\n")
        
        for video in cardio_videos:
            print(f"Title: {video.get('title')}")
            print(f"ID: {video.get('id')}")
            print(f"file_url: {video.get('file_url')}")
            print(f"content_type: {video.get('content_type')}")
            print(f"status: {video.get('status')}")
            print("---")

if __name__ == "__main__":
    check_cardio_video()
