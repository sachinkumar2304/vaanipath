import requests

def test_videos():
    url = "http://localhost:8000/api/v1/videos/?page=1&page_size=100"
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Videos endpoint working!")
            data = response.json()
            print(f"Total videos: {data.get('total')}")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_videos()
