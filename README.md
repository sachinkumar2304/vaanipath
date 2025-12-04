# Localisation Engine

A complete, production-ready Multilingual Localisation Engine built with FastAPI that processes videos, generates transcripts, translates to 22 Indic languages, and provides on-demand TTS and video dubbing.

## Features

- ✅ Video/Audio upload and processing
- ✅ Speech-to-Text using Whisper (Faster-Whisper or WhisperX)
- ✅ Translation to 22 Indic languages using IndicTrans2
- ✅ Glossary support for domain-specific terms
- ✅ Subtitle generation (VTT + SRT) for all languages
- ✅ On-demand Text-to-Speech using Coqui TTS (XTTS)
- ✅ On-demand video dubbing using FFmpeg
- ✅ Caching of generated TTS and dubbed videos
- ✅ Local filesystem storage
- ✅ Background job processing

## Architecture

```
localisation_engine/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── routes/                 # API endpoints
│   │   ├── upload.py          # File upload endpoint
│   │   ├── play.py            # On-demand playback endpoint
│   │   └── status.py          # Job status endpoint
│   ├── workers/                # Background workers
│   │   └── process_upload.py  # Processing pipeline
│   ├── services/              # Core services
│   │   ├── ffmpeg_utils.py    # FFmpeg operations
│   │   ├── stt_whisper.py     # Whisper STT
│   │   ├── translate_indictrans.py  # IndicTrans2 translation
│   │   ├── glossary.py        # Glossary processing
│   │   ├── tts_coqui.py       # Coqui TTS
│   │   └── merge_video.py     # Video merging
│   ├── utils/
│   │   └── storage.py         # Storage utilities
│   └── db/
│       ├── models.py          # Database models
│       └── database.py        # Database connection
├── storage/                    # Local storage
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Pipeline

### 1. Upload (POST /api/upload)
- Accepts video/audio/document files
- Saves file locally
- Creates job entry
- Starts background processing

### 2. Initial Processing (Background)
- Extract audio from video
- Generate transcript using Whisper
- Translate to all 22 Indic languages
- Apply glossary replacements
- Generate subtitles (VTT + SRT) for all languages
- Mark job as "ready_for_use"

### 3. On-Demand Playback (GET /api/play/{job_id}/{lang})
- Check if TTS audio exists → generate if not
- Check if dubbed video exists → generate if not
- Return file paths/URLs

## Installation

### Prerequisites

1. **Python 3.10+**
2. **FFmpeg** - Install from [ffmpeg.org](https://ffmpeg.org/download.html)
   ```bash
   # Ubuntu/Debian
   sudo apt-get install ffmpeg
   
   # macOS
   brew install ffmpeg
   
   # Windows
   # Download from https://ffmpeg.org/download.html
   ```

3. **IndicTrans2** - Install separately (see below)

### Setup

1. **Clone and install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install TTS (Coqui TTS) - Optional:**
   
   **For Python 3.9-3.11:**
   ```bash
   pip install TTS
   ```
   
   **For Python 3.12+:**
   ```bash
   # Install from source
   pip install git+https://github.com/coqui-ai/TTS.git
   ```
   
   **Note:** If TTS installation fails, the system will use a fallback mode. TTS is only needed for on-demand audio generation.

3. **Install PyTorch (if using TTS):**
   
   **CPU version:**
   ```bash
   pip install torch torchaudio
   ```
   
   **GPU version (CUDA):**
   ```bash
   # CUDA 11.8
   pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
   
   # CUDA 12.1
   pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

4. **Install IndicTrans2 (Optional but Recommended):**
   ```bash
   git clone https://github.com/AI4Bharat/IndicTrans2.git
   cd IndicTrans2
   pip install -e .
   ```
   
   Or use the pre-trained models:
   ```python
   # Models will be downloaded automatically on first use
   # Model directory: ai4bharat/indictrans2-en-indic-1B
   ```
   
   **Note:** If IndicTrans2 is not installed, a fallback translator will be used.

3. **Initialize storage:**
   ```bash
   mkdir -p storage/jobs storage/uploads
   ```

4. **Run the application:**
   ```bash
   # Development
   uvicorn app.main:app --reload
   
   # Production
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

## Docker Setup

### Using Docker Compose (Recommended)

```bash
docker-compose up -d
```

This starts:
- API server on port 8000
- Celery worker for background processing
- Redis for task queue

### Using Docker

```bash
docker build -t localisation-engine .
docker run -p 8000:8000 -v $(pwd)/storage:/app/storage localisation-engine
```

## GPU Support

### For Whisper STT:
```python
# In app/services/stt_whisper.py, change:
stt_service = WhisperSTT(model_size="base", device="cuda")
```

### For Coqui TTS:
```python
# In app/routes/play.py, change:
tts_service = get_tts_service(device="cuda")
```

### Docker with GPU:
```yaml
# Add to docker-compose.yml:
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

## API Usage

### 1. Upload a File

```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@video.mp4"
```

Response:
```json
{
  "job_id": "uuid-here",
  "status": "pending",
  "message": "File uploaded successfully. Processing started."
}
```

### 2. Check Job Status

```bash
curl "http://localhost:8000/api/status/{job_id}"
```

Response:
```json
{
  "id": "uuid-here",
  "status": "ready_for_use",
  "original_filename": "video.mp4",
  "metadata": {
    "languages_processed": ["hi", "bn", "ta", ...],
    "transcript_duration": 120.5
  }
}
```

### 3. Get Playback for Language

```bash
curl "http://localhost:8000/api/play/{job_id}/hi"
```

Response:
```json
{
  "job_id": "uuid-here",
  "language": "hi",
  "audio_url": "/storage/jobs/{job_id}/audio_tts/hi.wav",
  "video_url": "/storage/jobs/{job_id}/dubbed_video/hi.mp4",
  "subtitle_vtt_url": "/storage/jobs/{job_id}/subtitles/hi.vtt",
  "subtitle_srt_url": "/storage/jobs/{job_id}/subtitles/hi.srt"
}
```

## Supported Languages

The system supports translation to 22 Indic languages:

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

## Glossary

Create a `glossary.json` file with domain-specific terms:

```json
{
  "AI": {
    "hi": "कृत्रिम बुद्धिमत्ता",
    "bn": "কৃত্রিম বুদ্ধিমত্তা",
    "ta": "செயற்கை நுண்ணறிவு"
  },
  "Machine Learning": {
    "hi": "मशीन लर्निंग",
    "ta": "இயந்திரக் கற்பித்தல்"
  }
}
```

Load it in `app/workers/process_upload.py`:
```python
glossary_path = Path("glossary.json")
if glossary_path.exists():
    glossary_processor.load_glossary(glossary_path)
```

## Storage Structure

```
storage/
  jobs/
    <job_id>/
      original/
        input.mp4
        audio.wav
      transcripts/
        base/
          transcript.json
          transcript.vtt
          transcript.srt
      translations/
        hi.json
        bn.json
        ...
      subtitles/
        hi.vtt
        hi.srt
        ...
      audio_tts/
        hi.wav
        bn.wav
        ...
      dubbed_video/
        hi.mp4
        bn.mp4
        ...
```

## Configuration

Set environment variables:

```bash
# Storage
STORAGE_ROOT=./storage

# Database
DATABASE_URL=sqlite:///./localisation_engine.db

# Celery (if using)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## Troubleshooting

### FFmpeg not found
- Ensure FFmpeg is installed and in PATH
- Check with: `ffmpeg -version`

### IndicTrans2 import error
- Install IndicTrans2 separately
- Ensure models are downloaded

### TTS/STT models not loading
- Check GPU availability: `nvidia-smi`
- Use CPU mode if GPU unavailable
- Ensure sufficient disk space for models

### Celery worker not processing
- Check Redis is running: `redis-cli ping`
- Check worker logs: `docker-compose logs worker`

## Performance Tips

1. **Use GPU** for faster STT and TTS processing
2. **Use Faster-Whisper** instead of standard Whisper for better performance
3. **Pre-warm models** by loading them at startup
4. **Use Celery** with multiple workers for parallel processing
5. **Cache models** in memory to avoid reloading

## License

MIT License

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

