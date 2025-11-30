# VaaniPath Localizer - API Documentation

Complete API reference with all endpoints, parameters, and supported languages.

## Base URL
`http://localhost:8000`

## Quick Start
`bash
# Upload and localize a video
curl -X POST "http://localhost:8000/upload" -F "file=@video.mp4" -F "source=en" -F "target=mr" -o output.mp4
`

## Endpoints

### 1. POST /upload
Upload and localize video in one step.

**Parameters:**
- file (required): Video file
- source: Source language (default: en)
- target: Target language (default: hi)
- mode: fast or accurate (default: fast)
- voice: male, female, or voice name
- course_id: Course identifier
- job_id: Custom job ID

**Returns:** Localized video file (MP4)

### 2. POST /jobs/start
Start job for existing file on server.

**Body (JSON):**
`json
{
  "input_path": "/path/to/video.mp4",
  "source": "en",
  "target": "hi",
  "job_id": "job123",
  "course_id": "course456",
  "mode": "fast"
}
`

### 3. GET /jobs/{job_id}/manifest
Get job details and results.

### 4. GET /jobs/{job_id}/chunks
List all processed chunks.

### 5. GET /jobs/{job_id}/chunks/{index}
Get specific chunk details.

### 6. POST /jobs/resynthesize
Regenerate TTS audio (useful after editing translations).

**Body (JSON):**
`json
{
  "job_id": "demo_job",
  "finalize": true,
  "voice": "female"
}
`

### 7. POST /jobs/finalize
Generate final video from chunks.

### 8. GET /jobs/{job_id}/stats
Get job statistics.

### 9. GET /captions/{job_id}?format=srt
Download captions (SRT or VTT format).

### 10. GET /voices?lang=hi
List available TTS voices.

### 11. GET /voice/{lang}
Get configured voice for language.

### 12. PUT /voice/{lang}
Set voice for language.

**Body (JSON):**
`json
{"gender": "male"}
`
or
`json
{"voice": "hi-IN-MadhurNeural"}
`

### 13. POST /voice/seed/india?gender=male
Auto-configure voices for Indian languages.

**PowerShell:**
`powershell
Invoke-WebRequest -Method POST -Uri "http://localhost:8000/voice/seed/india?gender=male"
`

### 14. POST /feedback
Submit feedback for a job.

## Language Codes

### Major Indian Languages (Google Translate)
| Language | Code | Translation | TTS |
|----------|------|-------------|-----|
| Hindi | hi, hi-IN |  Google |  edge-tts + gTTS |
| Marathi | mr, mr-IN |  Google |  edge-tts + gTTS |
| Bengali | bn, bn-IN |  Google |  edge-tts + gTTS |
| Tamil | ta, ta-IN |  Google |  edge-tts + gTTS |
| Telugu | te, te-IN |  Google |  edge-tts + gTTS |
| Gujarati | gu, gu-IN |  Google |  edge-tts + gTTS |
| Kannada | kn, kn-IN |  Google |  edge-tts + gTTS |
| Malayalam | ml, ml-IN |  Google |  edge-tts + gTTS |
| Punjabi | pa, pa-IN |  Google |  edge-tts + gTTS |
| Odia | or, or-IN |  Google |  gTTS |
| Assamese | as, as-IN |  Google |  gTTS |
| Nepali | ne |  Google |  gTTS |
| Sanskrit | sa, sa-IN |  Google |  via Hindi |
| Sindhi | sd |  Google |  via Urdu |
| Urdu | ur, ur-IN |  Google |  edge-tts + gTTS |

### Regional Languages (Gemini Translation Required)
**Note:** These languages require Gemini API for translation. Set GEMINI_API_KEY environment variable.

| Language | Code | Translation | TTS | Notes |
|----------|------|-------------|-----|-------|
| Bodo | brx |  Gemini |  via Hindi | Requires GEMINI_API_KEY |
| Dogri | doi |  Gemini |  via Hindi | Requires GEMINI_API_KEY |
| Haryanvi | bgc |  Gemini |  via Hindi | Requires GEMINI_API_KEY |
| Kashmiri | ks |  Gemini |  via Urdu | Requires GEMINI_API_KEY |
| Konkani | gom |  Gemini |  via Hindi | Requires GEMINI_API_KEY |
| Maithili | mai |  Gemini |  via Hindi | Requires GEMINI_API_KEY |
| Manipuri (Meitei) | mni |  Gemini |  via Hindi | Requires GEMINI_API_KEY |
| Santali | sat |  Gemini |  via Hindi | Requires GEMINI_API_KEY |
| Marwari | mwr |  Gemini |  via Hindi | Requires GEMINI_API_KEY |
| Bhojpuri | bho |  Gemini + rules |  via Hindi | Dialectal approximation |

### International Languages
English (en), Spanish (es), French (fr), German (de), Chinese (zh), Japanese (ja), and 100+ more via Google Translate.

## Translation Models
- **google** (default): No setup required, supports 100+ languages
- **gemini**: Better quality for Indian languages. Set GEMINI_API_KEY

**Automatic Fallback:** If Google Translate doesn't support a language well (e.g., Bodo, Dogri), the system automatically uses Gemini translation.

## Processing Modes
- **fast**: Quick processing, good quality (tiny Whisper model)
- **accurate**: Slower, best quality (base/small Whisper model)

## Environment Variables
- **GEMINI_API_KEY** (required for regional languages): Google Gemini API key
- GEMINI_MODEL: Model name (default: gemini-2.5-flash)

## Example Workflow
`bash
# Set Gemini API key (required for regional languages)
export GEMINI_API_KEY="your-api-key-here"

# 1. Upload video (with Gemini language)
curl -X POST "http://localhost:8000/upload" -F "file=@video.mp4" -F "source=en" -F "target=brx" -o output.mp4

# 2. Check status
curl "http://localhost:8000/jobs/job_001/stats"

# 3. Get manifest
curl "http://localhost:8000/jobs/job_001/manifest"

# 4. Download captions
curl "http://localhost:8000/captions/job_001?format=srt" -o captions.zip
`

## Error Codes
- 200: Success
- 400: Bad request (missing parameters)
- 404: Job/chunk not found
- 500: Server error (check logs)

## Support
GitHub: https://github.com/Zaidusyy/VaaniPath-Localizer
