"""
Comprehensive ML Service Integration Tests
"""
import requests
import time

def test_ml_service_health():
    """Test if ML service is running and responding"""
    print("=" * 60)
    print("1. Testing ML Service Health")
    print("=" * 60)
    
    try:
        response = requests.get("http://localhost:8001/docs")
        if response.status_code == 200:
            print("✅ ML Service is running on port 8001")
            return True
        else:
            print(f"❌ ML Service returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ML Service is not accessible: {e}")
        return False

def test_backend_ml_connection():
    """Test if backend can connect to ML service"""
    print("\n" + "=" * 60)
    print("2. Testing Backend → ML Service Connection")
    print("=" * 60)
    
    # Login first
    login_response = requests.post(
        "http://localhost:8000/api/v1/auth/login",
        json={"email": "test@example.com", "password": "password123"}
    )
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return False
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get a video that we can test with
    videos_response = requests.get(
        "http://localhost:8000/api/v1/videos/?page=1&page_size=5",
        headers=headers
    )
    
    if videos_response.status_code != 200 or not videos_response.json()['videos']:
        print("❌ No videos found for testing")
        return False
    
    video = videos_response.json()['videos'][0]
    video_id = video['id']
    video_title = video['title']
    
    print(f"📹 Testing with video: {video_title} (ID: {video_id})")
    
    # Check available languages
    try:
        lang_response = requests.get(
            f"http://localhost:8000/api/v1/processing/content/{video_id}/available-languages",
            headers=headers
        )
        
        if lang_response.status_code == 200:
            data = lang_response.json()
            print(f"✅ Backend connected to ML service")
            print(f"   Available languages: {len(data.get('languages', []))}")
            return True, video_id, headers
        else:
            print(f"❌ Failed to get available languages: {lang_response.status_code}")
            return False, None, None
    except Exception as e:
        print(f"❌ Error connecting to ML service: {e}")
        return False, None, None

def test_language_dubbing(video_id, headers):
    """Test dubbing/language switching"""
    print("\n" + "=" * 60)
    print("3. Testing Language Dubbing (Hindi)")
    print("=" * 60)
    
    try:
        # Request dubbing to Hindi
        dub_response = requests.post(
            f"http://localhost:8000/api/v1/processing/dub/{video_id}",
            headers=headers,
            json={"target_language": "hi"}
        )
        
        if dub_response.status_code == 200:
            data = dub_response.json()
            print(f"✅ Dubbing request accepted")
            print(f"   Status: {data.get('status')}")
            print(f"   Message: {data.get('message')}")
            
            # If cached, test the content URL
            if data.get('status') == 'completed' and data.get('content_url'):
                print(f"✅ Cached content found!")
                print(f"   URL: {data.get('content_url')}")
                return True
            elif data.get('status') == 'processing':
                print(f"⏳ Processing started (not cached)")
                return True
            
        else:
            print(f"❌ Dubbing request failed: {dub_response.status_code}")
            print(f"   Response: {dub_response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing dubbing: {e}")
        return False

def test_caching_mechanism(video_id, headers):
    """Test if caching works (second request should be instant)"""
    print("\n" + "=" * 60)
    print("4. Testing Caching Mechanism")
    print("=" * 60)
    
    try:
        # First request
        print("Making first dubbing request...")
        start_time = time.time()
        response1 = requests.post(
            f"http://localhost:8000/api/v1/processing/dub/{video_id}",
            headers=headers,
            json={"target_language": "hi"}
        )
        time1 = time.time() - start_time
        
        # Second request (should be cached)
        print("Making second dubbing request (should hit cache)...")
        start_time = time.time()
        response2 = requests.post(
            f"http://localhost:8000/api/v1/processing/dub/{video_id}",
            headers=headers,
            json={"target_language": "hi"}
        )
        time2 = time.time() - start_time
        
        if response2.status_code == 200:
            data = response2.json()
            if data.get('cached'):
                print(f"✅ Caching works!")
                print(f"   First request: {time1:.2f}s")
                print(f"   Second request: {time2:.2f}s (cached)")
                return True
            else:
                print(f"⚠️  Not cached (might be processing)")
        
        return False
    except Exception as e:
        print(f"❌ Error testing caching: {e}")
        return False

def run_all_tests():
    """Run all integration tests"""
    print("\n🧪 VaaniPath ML Localizer Integration Tests")
    print("=" * 60)
    
    # Test 1: ML Service Health
    if not test_ml_service_health():
        print("\n❌ ML Service is not running. Cannot proceed.")
        return
    
    # Test 2: Backend-ML Connection
    result = test_backend_ml_connection()
    if isinstance(result, tuple):
        success, video_id, headers = result
        if not success:
            print("\n❌ Backend cannot connect to ML service.")
            return
    else:
        print("\n❌ Backend connection test failed.")
        return
    
    # Test 3: Dubbing
    test_language_dubbing(video_id, headers)
    
    # Test 4: Caching
    test_caching_mechanism(video_id, headers)
    
    print("\n" + "=" * 60)
    print("✅ Testing Complete!")
    print("=" * 60)

if __name__ == "__main__":
    run_all_tests()
