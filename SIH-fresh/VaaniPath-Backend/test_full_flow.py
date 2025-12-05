#!/usr/bin/env python3
"""
Complete flow test: Signup -> Login -> Video Upload
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8001/api/v1"

print("=" * 70)
print("GYANIFY COMPLETE FLOW TEST")
print("=" * 70)

# Test 1: Signup
print("\n1️⃣  TESTING SIGNUP...")
print("-" * 70)

signup_data = {
    "email": f"testuser{int(time.time())}@example.com",
    "password": "Test@123",
    "full_name": "Test User",
    "is_admin": True
}

print(f"Email: {signup_data['email']}")
signup_response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
print(f"Status: {signup_response.status_code}")

if signup_response.status_code == 201:
    signup_result = signup_response.json()
    user_id = signup_result.get("id")
    print(f"✅ Signup Success!")
    print(f"   User ID: {user_id}")
    print(f"   Email: {signup_result.get('email')}")
else:
    print(f"❌ Signup Failed!")
    print(f"   Response: {signup_response.json()}")
    exit(1)

# Test 2: Login
print("\n2️⃣  TESTING LOGIN...")
print("-" * 70)

login_data = {
    "email": signup_data["email"],
    "password": signup_data["password"]
}

print(f"Email: {login_data['email']}")
login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
print(f"Status: {login_response.status_code}")

if login_response.status_code == 200:
    login_result = login_response.json()
    access_token = login_result.get("access_token")
    print(f"✅ Login Success!")
    print(f"   Token: {access_token[:50]}...")
else:
    print(f"❌ Login Failed!")
    print(f"   Response: {login_response.json()}")
    exit(1)

# Test 3: Video Upload
print("\n3️⃣  TESTING VIDEO UPLOAD...")
print("-" * 70)

# Create a proper test video file
test_video_path = "test_video.mp4"
print(f"Creating test video file: {test_video_path}")

# Import the video creator
import sys
sys.path.insert(0, '.')
from create_test_video import create_minimal_mp4
create_minimal_mp4(test_video_path)

print(f"Test video created: {test_video_path}")

# Upload video
headers = {
    "Authorization": f"Bearer {access_token}"
}

with open(test_video_path, "rb") as f:
    files = {
        "file": ("test_video.mp4", f, "video/mp4")
    }
    data = {
        "title": "Test Video Upload",
        "description": "Testing video upload functionality",
        "domain": "it",
        "source_language": "en",
        "target_languages": "hi,ta"
    }
    
    print("Uploading video...")
    upload_response = requests.post(
        f"{BASE_URL}/videos/upload",
        files=files,
        data=data,
        headers=headers
    )

print(f"Status: {upload_response.status_code}")

if upload_response.status_code == 201:
    upload_result = upload_response.json()
    video_id = upload_result.get("id")
    print(f"✅ Video Upload Success!")
    print(f"   Video ID: {video_id}")
    print(f"   Title: {upload_result.get('title')}")
    print(f"   File URL: {upload_result.get('file_url')[:80]}...")
    print(f"   Status: {upload_result.get('status')}")
else:
    print(f"❌ Video Upload Failed!")
    print(f"   Response: {upload_response.json()}")
    exit(1)

# Test 4: List Videos
print("\n4️⃣  TESTING LIST VIDEOS...")
print("-" * 70)

list_response = requests.get(
    f"{BASE_URL}/videos/",
    headers=headers
)

print(f"Status: {list_response.status_code}")

if list_response.status_code == 200:
    list_result = list_response.json()
    videos = list_result.get("videos", [])
    print(f"✅ List Videos Success!")
    print(f"   Total Videos: {len(videos)}")
    if videos:
        print(f"   First Video: {videos[0].get('title')}")
else:
    print(f"❌ List Videos Failed!")
    print(f"   Response: {list_response.json()}")

# Test 5: Get Video Details
print("\n5️⃣  TESTING GET VIDEO DETAILS...")
print("-" * 70)

get_response = requests.get(
    f"{BASE_URL}/videos/{video_id}",
    headers=headers
)

print(f"Status: {get_response.status_code}")

if get_response.status_code == 200:
    get_result = get_response.json()
    print(f"✅ Get Video Success!")
    print(f"   Video ID: {get_result.get('id')}")
    print(f"   Title: {get_result.get('title')}")
    print(f"   Status: {get_result.get('status')}")
else:
    print(f"❌ Get Video Failed!")
    print(f"   Response: {get_response.json()}")

print("\n" + "=" * 70)
print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
print("=" * 70)

# Cleanup
import os
os.remove(test_video_path)
print(f"\nCleaned up test file: {test_video_path}")
