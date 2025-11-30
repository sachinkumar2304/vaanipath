import requests
import json

def test_video_url():
    video_id = "334828f7-e263-4f03-855d-85cca59c2954"
    
    # Login
    login_response = requests.post(
        "http://localhost:8000/api/v1/auth/login",
        json={"email": "test@example.com", "password": "password123"}
    )
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get video
    response = requests.get(f"http://localhost:8000/api/v1/videos/{video_id}", headers=headers)
    data = response.json()
    
    print("=== VIDEO URL TEST ===\n")
    print(f"Title: {data.get('title')}")
    print(f"file_url: {data.get('file_url')}")
    print(f"\nURL Present: {'✅ YES' if data.get('file_url') else '❌ NO'}")
    
    if data.get('file_url'):
        print(f"\n✅ SUCCESS! Video URL is now returned correctly!")
        print(f"URL: {data.get('file_url')}")
    else:
        print(f"\n❌ FAILED! URL is still None")

if __name__ == "__main__":
    test_video_url()
