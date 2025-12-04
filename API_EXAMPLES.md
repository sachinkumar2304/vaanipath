# API Usage Examples

This document provides examples of how to use the Localisation Engine API.

## Base URL

```
http://localhost:8000
```

## Endpoints

### 1. Upload a File

Upload a video, audio, or document file for processing.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@video.mp4"
```

**Python Example:**
```python
import requests

url = "http://localhost:8000/api/upload"
files = {"file": open("video.mp4", "rb")}

response = requests.post(url, files=files)
print(response.json())
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "File uploaded successfully. Processing started."
}
```

### 2. Check Job Status

Check the status of a processing job.

**Request:**
```bash
curl "http://localhost:8000/api/status/550e8400-e29b-41d4-a716-446655440000"
```

**Python Example:**
```python
import requests

job_id = "550e8400-e29b-41d4-a716-446655440000"
url = f"http://localhost:8000/api/status/{job_id}"

response = requests.get(url)
print(response.json())
```

**Response (Processing):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "original_filename": "video.mp4",
  "file_type": "mp4",
  "created_at": "2024-01-01T12:00:00",
  "updated_at": null,
  "error_message": null,
  "metadata": null
}
```

**Response (Ready):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "ready_for_use",
  "original_filename": "video.mp4",
  "file_type": "mp4",
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:05:00",
  "error_message": null,
  "metadata": {
    "languages_processed": ["hi", "bn", "ta", "te", "kn", "ml", "or", "gu", "pa", "as"],
    "transcript_duration": 120.5,
    "transcript_language": "en"
  }
}
```

### 3. Get Playback for a Language

Get audio, video, and subtitles for a specific language. This will generate TTS and dubbed video on-demand if they don't exist.

**Request:**
```bash
curl "http://localhost:8000/api/play/550e8400-e29b-41d4-a716-446655440000/hi"
```

**Python Example:**
```python
import requests

job_id = "550e8400-e29b-41d4-a716-446655440000"
lang = "hi"  # Hindi
url = f"http://localhost:8000/api/play/{job_id}/{lang}"

response = requests.get(url)
data = response.json()
print(f"Audio URL: {data['audio_url']}")
print(f"Video URL: {data['video_url']}")
print(f"Subtitle VTT: {data['subtitle_vtt_url']}")
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "language": "hi",
  "audio_url": "/storage/jobs/550e8400-e29b-41d4-a716-446655440000/audio_tts/hi.wav",
  "video_url": "/storage/jobs/550e8400-e29b-41d4-a716-446655440000/dubbed_video/hi.mp4",
  "subtitle_vtt_url": "/storage/jobs/550e8400-e29b-41d4-a716-446655440000/subtitles/hi.vtt",
  "subtitle_srt_url": "/storage/jobs/550e8400-e29b-41d4-a716-446655440000/subtitles/hi.srt",
  "file_paths": {
    "audio": "storage/jobs/550e8400-e29b-41d4-a716-446655440000/audio_tts/hi.wav",
    "video": "storage/jobs/550e8400-e29b-41d4-a716-446655440000/dubbed_video/hi.mp4",
    "subtitle_vtt": "storage/jobs/550e8400-e29b-41d4-a716-446655440000/subtitles/hi.vtt",
    "subtitle_srt": "storage/jobs/550e8400-e29b-41d4-a716-446655440000/subtitles/hi.srt"
  }
}
```

### 4. List All Jobs

Get a list of all jobs.

**Request:**
```bash
curl "http://localhost:8000/api/status?skip=0&limit=10"
```

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "ready_for_use",
    "original_filename": "video.mp4",
    ...
  },
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "status": "processing",
    "original_filename": "audio.mp3",
    ...
  }
]
```

## Complete Workflow Example

```python
import requests
import time

BASE_URL = "http://localhost:8000"

# Step 1: Upload file
print("Uploading file...")
with open("video.mp4", "rb") as f:
    response = requests.post(f"{BASE_URL}/api/upload", files={"file": f})
    job_data = response.json()
    job_id = job_data["job_id"]
    print(f"Job ID: {job_id}")

# Step 2: Wait for processing
print("Waiting for processing...")
while True:
    response = requests.get(f"{BASE_URL}/api/status/{job_id}")
    status_data = response.json()
    
    if status_data["status"] == "ready_for_use":
        print("Processing complete!")
        break
    elif status_data["status"] == "error":
        print(f"Error: {status_data.get('error_message')}")
        break
    
    print(f"Status: {status_data['status']}")
    time.sleep(5)

# Step 3: Get Hindi version
print("Getting Hindi version...")
response = requests.get(f"{BASE_URL}/api/play/{job_id}/hi")
play_data = response.json()

print(f"Audio: {BASE_URL}{play_data['audio_url']}")
print(f"Video: {BASE_URL}{play_data['video_url']}")
print(f"Subtitles: {BASE_URL}{play_data['subtitle_vtt_url']}")

# Step 4: Download files
audio_url = f"{BASE_URL}{play_data['audio_url']}"
video_url = f"{BASE_URL}{play_data['video_url']}"

audio_response = requests.get(audio_url)
with open("output_hindi.wav", "wb") as f:
    f.write(audio_response.content)

video_response = requests.get(video_url)
with open("output_hindi.mp4", "wb") as f:
    f.write(video_response.content)

print("Files downloaded!")
```

## Supported Languages

Use these language codes in the `/play/{job_id}/{lang}` endpoint:

- `hi` - Hindi
- `bn` - Bengali
- `mr` - Marathi
- `ta` - Tamil
- `te` - Telugu
- `kn` - Kannada
- `ml` - Malayalam
- `or` - Odia
- `gu` - Gujarati
- `pa` - Punjabi
- `as` - Assamese
- `ks` - Kashmiri
- `sd` - Sindhi
- `kok` - Konkani
- `ne` - Nepali
- `sa` - Sanskrit
- `ur` - Urdu
- `si` - Sinhala
- `my` - Myanmar
- `th` - Thai
- `lo` - Lao
- `km` - Khmer

## Error Handling

The API returns standard HTTP status codes:

- `200` - Success
- `400` - Bad Request (invalid file type, unsupported language, etc.)
- `404` - Not Found (job not found, file not found)
- `500` - Internal Server Error

Example error response:
```json
{
  "detail": "Job is not ready yet. Current status: processing"
}
```



