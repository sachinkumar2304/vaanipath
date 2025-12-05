# ML Localizer Service Integration

##

 Overview
The VaaniPath-Localizer ML service handles video translation and localization. It runs as a separate microservice.

## Setup Instructions

### 1. Install Dependencies
```bash
cd d:\project-1\VaaniPath-Localizer\localizer
pip install -r requirements.txt
```

### 2. Configure Environment
Create `.env` file in `VaaniPath-Localizer/localizer/` with:
```env
# Add any required API keys for translation services
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json  # if using Google Translate
```

### 3. Run ML Service
```bash
cd d:\project-1\VaaniPath-Localizer\localizer
python api.py
```

This starts the ML service on **port 8001**.

### 4. Verify ML Service
```bash
curl http://localhost:8001/health
```

## How It Works

### Video Upload Flow:
1. Teacher uploads video to VaaniPath-Backend (port 8000)
2. Video saved to Cloudinary, metadata to Supabase
3. Backend triggers ML service: `POST /upload` to port 8001
4. ML service processes video:
   - Extracts audio
   - Transcribes (STT)
   - Translates to target languages
   - Synthesizes speech (TTS)
   - Creates localized video
5. ML service returns job_id
6. Backend stores job_id in database

### Student Playback Flow:
1. Student selects video and language
2. Backend checks if translation exists (job_id)
3. If yes: serves localized version from ML service
4. If no: triggers on-demand translation

## API Integration

### From VaaniPath-Backend to ML Service:

**Trigger Translation:**
```python
import requests

response = requests.post('http://localhost:8001/upload', files={
    'file': open('video.mp4', 'rb')
}, data={
    'source': 'en',
    'target': 'hi-IN',
    'course_id': 'education',
    'job_id': video_id,
    'mode': 'fast'
})
```

**Check Status:**
```python
response = requests.get(f'http://localhost:8001/jobs/{job_id}/stats')
```

**Get Translated Video:**
```python
response = requests.get(f'http://localhost:8001/output/{job_id}/final_video.mp4')
```

## Backend Changes Made

1. **New Endpoint:** `POST /api/v1/processing/trigger-translation`
   - Triggers ML service for a video
   - Stores job status in database

2. **New Endpoint:** `GET /api/v1/processing/status/{video_id}`
   - Check translation status

3. **Updated:** Video upload endpoint
   - Auto-triggers translation after upload (optional)

## Database Schema

Added to `videos` table:
- `ml_job_id`: String (stores ML service job ID)
- `translation_status`: String ('pending', 'processing', 'completed', 'failed')

## Notes

- ML service must be running on port 8001
- Translated videos stored in `VaaniPath-Localizer/localizer/output/`
- For production: Deploy ML service separately (Docker/cloud)
- Currently using file-based storage; can migrate to cloud storage later
