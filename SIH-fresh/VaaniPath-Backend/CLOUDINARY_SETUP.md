# 🎥 Cloudinary Setup Guide for Gyanify

## 📋 **Why Cloudinary?**

```
✅ Free Tier: 25 GB storage + 25 GB bandwidth/month
✅ Automatic video optimization & transcoding
✅ Global CDN (fast delivery worldwide)
✅ No egress/bandwidth fees (unlike Cloudflare R2)
✅ Built-in media management dashboard
✅ Video transformations (quality, format, thumbnails)
✅ Perfect for educational videos
```

---

## 🚀 **Step-by-Step Setup (15 minutes)**

### **Step 1: Create Account**

1. **Go to Cloudinary:**
   ```
   https://cloudinary.com/users/register_free
   ```

2. **Sign up:**
   - Name: Your Name
   - Email: your@email.com
   - Company: Gyanify (or your institution)
   - Role: Developer
   - Click "Sign Up for Free"

3. **Verify Email:**
   - Check inbox
   - Click verification link

---

### **Step 2: Get Credentials**

1. **Go to Dashboard:**
   ```
   https://cloudinary.com/console
   ```

2. **Copy Credentials (Top right):**
   ```
   ┌─────────────────────────────────────────┐
   │  Cloud name: your-cloud-name            │
   │  API Key: 123456789012345               │
   │  API Secret: [Click to reveal]          │
   └─────────────────────────────────────────┘
   ```

3. **Save These:**
   ```
   CLOUDINARY_CLOUD_NAME=your-cloud-name
   CLOUDINARY_API_KEY=123456789012345
   CLOUDINARY_API_SECRET=abcdef123456xyz789
   ```

---

### **Step 3: Configure Upload Presets (Optional)**

1. **Go to Settings:**
   ```
   Settings → Upload → Upload presets → Add upload preset
   ```

2. **Create Preset for Videos:**
   ```
   Preset name: gyanify_videos
   Signing Mode: Unsigned (for easier uploads)
   Folder: gyanify/videos/original
   
   Transformations:
   ✅ Quality: Auto
   ✅ Format: Auto (mp4)
   ✅ Video codec: h264
   ```

3. **Save Preset**

---

### **Step 4: Update Backend .env**

1. **Open .env file:**
   ```bash
   D:\backend\.env
   ```

2. **Add Cloudinary credentials:**
   ```env
   # Cloudinary Configuration
   CLOUDINARY_CLOUD_NAME=your-cloud-name
   CLOUDINARY_API_KEY=123456789012345
   CLOUDINARY_API_SECRET=abcdef123456xyz789
   ```

3. **Save file** (Ctrl+S)

---

### **Step 5: Install Cloudinary Package**

```bash
cd D:\backend
pip install cloudinary==1.36.0
```

Or update requirements:
```bash
pip install -r requirements.txt
```

---

### **Step 6: Test Upload**

1. **Start backend:**
   ```bash
   cd D:\backend
   uvicorn app.main:app --reload
   ```

2. **Test in Python (Optional):**
   ```python
   # Test script
   from app.storage.cloudinary_client import get_cloudinary_client
   
   client = get_cloudinary_client()
   
   # Test upload
   result = client.upload_video(
       file_path="test_video.mp4",
       public_id="test_upload",
       folder="gyanify/videos/test"
   )
   
   print(result)
   # Output: {'success': True, 'url': 'https://res.cloudinary.com/...'}
   ```

3. **Or test via API:**
   ```
   http://localhost:8000/docs
   POST /api/v1/videos/upload
   ```

---

## 📊 **Cloudinary Dashboard Tour**

### **1. Media Library:**
```
https://cloudinary.com/console/media_library

Here you'll see:
├── gyanify/
│   ├── videos/
│   │   ├── original/
│   │   │   └── video_123.mp4
│   │   └── dubbed/
│   │       ├── video_123_hi.mp4
│   │       └── video_123_ta.mp4
│   └── audio/
│       ├── video_123_hi.mp3
│       └── video_123_ta.mp3
```

### **2. Reports:**
```
Settings → Usage

Shows:
- Storage used: 2.5 GB / 25 GB
- Bandwidth: 1.2 GB / 25 GB (this month)
- Transformations: 500 / 25,000
```

### **3. Video URLs:**
```
Original:
https://res.cloudinary.com/your-cloud/video/upload/gyanify/videos/original/video_123.mp4

Dubbed (Hindi):
https://res.cloudinary.com/your-cloud/video/upload/gyanify/videos/dubbed/video_123_hi.mp4

With transformation (lower quality):
https://res.cloudinary.com/your-cloud/video/upload/q_auto:low/gyanify/videos/original/video_123.mp4
```

---

## 🎯 **Usage in Backend**

### **Upload Original Video:**
```python
from app.storage.cloudinary_client import get_cloudinary_client

client = get_cloudinary_client()

# Upload
result = client.upload_video(
    file_path="/tmp/uploaded_video.mp4",
    public_id=video_id,
    folder="gyanify/videos/original"
)

# Save URL to database
video_url = result['url']
```

### **Upload Dubbed Video:**
```python
# After ML processing
result = client.upload_dubbed_video(
    file_path="/tmp/dubbed_hindi.mp4",
    video_id=video_id,
    language="hi"
)

# Save to database
dubbed_url = result['url']  # https://res.cloudinary.com/.../video_123_hi.mp4
```

### **Check if Video Exists:**
```python
exists = client.check_video_exists(f"{video_id}_hi")

if exists:
    # Play directly
    url = client.get_video_url(f"{video_id}_hi")
else:
    # Start dubbing process
    start_dubbing(video_id, "hi")
```

---

## 🔧 **Advanced Features**

### **1. Video Transformations:**
```python
# Get lower quality for mobile
mobile_url = client.get_video_url(
    public_id=video_id,
    transformation={
        'quality': 'auto:low',
        'fetch_format': 'auto'
    }
)

# Get thumbnail
thumbnail_url = f"https://res.cloudinary.com/{cloud_name}/video/upload/so_0/{video_id}.jpg"
```

### **2. Adaptive Bitrate Streaming:**
```python
# HLS streaming URL
hls_url = f"https://res.cloudinary.com/{cloud_name}/video/upload/sp_hd/{video_id}.m3u8"
```

### **3. Download Protection:**
```
In Cloudinary Dashboard:
Settings → Security → Restricted media types
Enable: Video
```

---

## 📊 **Free Tier Limits**

```
Storage: 25 GB
├── Videos (original): ~10 GB (20-25 videos @ 400MB each)
├── Dubbed videos: ~10 GB (on-demand dubbing)
└── Audio files: ~1 GB (200+ files @ 5MB each)

Bandwidth: 25 GB/month
├── Video views: ~100-150 views (250MB each)
└── Resets every month

Transformations: 25,000/month
├── Quality conversions
├── Format changes
└── Thumbnail generation

Notes:
- Enough for SIH demo (10-15 videos)
- For production, upgrade to $99/month (100 GB)
```

---

## ⚠️ **Important Notes**

### **1. Public IDs:**
```
Use video_id as public_id for easy tracking:

Original: video_123
Dubbed Hindi: video_123_hi
Dubbed Tamil: video_123_ta
Audio Hindi: video_123_hi (in audio folder)
```

### **2. Folder Structure:**
```
Keep organized:
gyanify/
├── videos/original/
├── videos/dubbed/
└── audio/
```

### **3. Deletion:**
```python
# Delete old videos to free space
client.delete_video("video_123_hi")
```

### **4. Monitoring:**
```
Check usage weekly:
Dashboard → Reports → Usage

Alert when:
- Storage > 20 GB (80%)
- Bandwidth > 20 GB (80%)
```

---

## 🚨 **Troubleshooting**

### **Error: "Invalid API key"**
```
Solution:
1. Check .env file has correct credentials
2. Restart backend server
3. Verify credentials in Cloudinary dashboard
```

### **Error: "Upload failed"**
```
Solution:
1. Check file size (max 100 MB on free tier)
2. Check file format (mp4, mov, avi supported)
3. Check internet connection
```

### **Error: "Storage limit exceeded"**
```
Solution:
1. Delete old test videos
2. Compress videos before upload
3. Use on-demand dubbing (don't pre-process)
```

---

## ✅ **Verification Checklist**

```
□ Cloudinary account created
□ Email verified
□ Credentials copied (cloud_name, api_key, api_secret)
□ .env file updated
□ cloudinary package installed
□ Backend restarted
□ Test upload successful
□ Video visible in Media Library
```

---

## 🎉 **Next Steps**

1. ✅ Cloudinary setup done
2. ⏳ Test video upload via API
3. ⏳ Verify video in dashboard
4. ⏳ Test dubbing flow
5. ⏳ Frontend integration

**Cloudinary ready to use!** 🚀

Need help? Check:
- Docs: https://cloudinary.com/documentation
- Support: https://support.cloudinary.com
