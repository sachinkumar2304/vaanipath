# Quick Start Guide

Get the Localisation Engine up and running in minutes.

## Prerequisites

1. **Python 3.10+**
2. **FFmpeg** - [Installation Guide](https://ffmpeg.org/download.html)
3. **Git** (for cloning IndicTrans2)

## Installation Steps

### 1. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg python3-pip python3-venv
```

**macOS:**
```bash
brew install ffmpeg python3
```

**Windows:**
- Download FFmpeg from https://ffmpeg.org/download.html
- Add to PATH

### 2. Clone and Setup

```bash
# Navigate to project directory
cd Chirags-Localisation-engine

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Install IndicTrans2 (Optional but Recommended)

```bash
git clone https://github.com/AI4Bharat/IndicTrans2.git
cd IndicTrans2
pip install -e .
cd ..
```

**Note:** Models will be downloaded automatically on first use (~2GB).

### 4. Run Setup Script

```bash
python setup.py
```

This will:
- Check Python version
- Check FFmpeg installation
- Create necessary directories

### 5. Start the Server

```bash
# Option 1: Using run.py
python run.py

# Option 2: Using uvicorn directly
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## Quick Test

### 1. Upload a Video

```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@test_video.mp4"
```

Save the `job_id` from the response.

### 2. Check Status

```bash
curl "http://localhost:8000/api/status/{job_id}"
```

Wait until status is `ready_for_use`.

### 3. Get Hindi Version

```bash
curl "http://localhost:8000/api/play/{job_id}/hi"
```

This will generate TTS audio and dubbed video on-demand.

## Docker Quick Start

### Using Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Using Docker

```bash
# Build image
docker build -t localisation-engine .

# Run container
docker run -p 8000:8000 \
  -v $(pwd)/storage:/app/storage \
  localisation-engine
```

## GPU Support

### For NVIDIA GPUs

1. Install NVIDIA Docker runtime:
```bash
# Follow instructions at: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html
```

2. Update `docker-compose.yml`:
```yaml
services:
  api:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

3. Update code to use GPU:
   - In `app/workers/process_upload.py`: Change `device="cpu"` to `device="cuda"`
   - In `app/routes/play.py`: Change `device="cpu"` to `device="cuda"`

## Configuration

### Environment Variables

Create a `.env` file:

```env
STORAGE_ROOT=./storage
DATABASE_URL=sqlite:///./localisation_engine.db
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Using Celery (Optional)

For production, use Celery with Redis:

```bash
# Install Redis
sudo apt-get install redis-server

# Start Redis
redis-server

# Start Celery worker (in separate terminal)
celery -A app.workers.process_upload worker --loglevel=info
```

## Troubleshooting

### FFmpeg not found
- Ensure FFmpeg is installed: `ffmpeg -version`
- Add to PATH if needed

### Models not loading
- Check internet connection (models download on first use)
- Ensure sufficient disk space (~5GB for all models)
- Check logs for specific errors

### Translation not working
- Ensure IndicTrans2 is installed
- Check model directory path
- Fallback translator will be used if IndicTrans2 unavailable

### TTS not working
- Ensure Coqui TTS is installed: `pip install TTS`
- Check GPU availability if using GPU mode
- Fallback TTS will create placeholder files

## Next Steps

- Read [README.md](README.md) for detailed documentation
- Check [API_EXAMPLES.md](API_EXAMPLES.md) for API usage examples
- Create a `glossary.json` file for domain-specific terms (see `glossary.example.json`)

## Support

For issues or questions:
1. Check the logs: `docker-compose logs` or application console
2. Review error messages in job status
3. Check that all dependencies are installed correctly



