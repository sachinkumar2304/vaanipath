#!/usr/bin/env python3
"""
Download a small sample video for testing
"""
import urllib.request

# Download a small sample video from a public source
url = "https://commondatastorage.googleapis.com/gtv-videos-library/sample/ForBiggerBlazes.mp4"
output_file = "sample_video.mp4"

print(f"Downloading sample video from {url}...")
print("This may take a moment...")

try:
    urllib.request.urlretrieve(url, output_file)
    print(f"✅ Downloaded: {output_file}")
    
    # Check file size
    import os
    size = os.path.getsize(output_file)
    print(f"   File size: {size / (1024*1024):.2f} MB")
except Exception as e:
    print(f"❌ Download failed: {e}")
    print("Using local test video instead...")
