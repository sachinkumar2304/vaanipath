# Installation Guide

This guide provides detailed installation instructions for the Localisation Engine, including handling Python version compatibility issues.

## Python Version Compatibility

- **Python 3.10+** is recommended
- **Python 3.13+** may have compatibility issues with some packages (TTS)

## Step-by-Step Installation

### 1. System Dependencies

#### FFmpeg (Required)

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
- Download from https://ffmpeg.org/download.html
- Extract and add to PATH

Verify installation:
```bash
ffmpeg -version
```

### 2. Python Dependencies

#### Basic Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install core dependencies
pip install -r requirements.txt
```

#### Optional Dependencies

**For TTS (Text-to-Speech):**

If you're using Python 3.9-3.11:
```bash
pip install TTS
pip install torch torchaudio  # CPU version
```

If you're using Python 3.12+:
```bash
# Install TTS from source
pip install git+https://github.com/coqui-ai/TTS.git
pip install torch torchaudio
```

**For GPU support (NVIDIA):**
```bash
# Check CUDA version first
nvidia-smi

# Install PyTorch with CUDA support
# CUDA 11.8:
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1:
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**For Translation (IndicTrans2):**
```bash
git clone https://github.com/AI4Bharat/IndicTrans2.git
cd IndicTrans2
pip install -e .
cd ..
```

### 3. Verify Installation

Run the setup script:
```bash
python setup.py
```

This will check:
- Python version
- FFmpeg installation
- Create necessary directories

### 4. Test Installation

```bash
# Start the server
python run.py

# In another terminal, test the API
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy"}
```

## Troubleshooting

### TTS Installation Fails

**Problem:** `ERROR: No matching distribution found for TTS==0.20.0`

**Solutions:**
1. **Use Python 3.9-3.11** (recommended for TTS)
2. **Install from source:**
   ```bash
   pip install git+https://github.com/coqui-ai/TTS.git
   ```
3. **Skip TTS** - The system will work without TTS, but audio generation will be disabled

### IndicTrans2 Installation Fails

**Problem:** Import errors or model loading issues

**Solutions:**
1. Ensure you've cloned the repository correctly
2. Install dependencies:
   ```bash
   cd IndicTrans2
   pip install -r requirements.txt
   pip install -e .
   ```
3. **Skip IndicTrans2** - A fallback translator will be used (returns original text)

### FFmpeg Not Found

**Problem:** `FFmpeg is not available`

**Solutions:**
1. Verify FFmpeg is installed: `ffmpeg -version`
2. Add FFmpeg to PATH
3. On Windows, ensure `ffmpeg.exe` is accessible

### PyTorch Installation Issues

**Problem:** PyTorch installation fails or wrong version

**Solutions:**
1. Visit https://pytorch.org/get-started/locally/
2. Select your configuration (OS, Python version, CUDA version)
3. Use the provided pip command

### Faster-Whisper Installation Issues

**Problem:** Faster-Whisper fails to install

**Solutions:**
1. Ensure you have a C++ compiler (Windows: Visual Studio Build Tools)
2. Try installing dependencies first:
   ```bash
   pip install Cython numpy
   pip install faster-whisper
   ```

## Minimal Installation (Without Optional Features)

If you want to run the system without TTS and IndicTrans2:

```bash
# Install only core dependencies
pip install fastapi uvicorn sqlalchemy python-multipart faster-whisper

# The system will use fallback modes for missing features
```

## Docker Installation

If you prefer Docker:

```bash
# Build image
docker build -t localisation-engine .

# Run container
docker run -p 8000:8000 \
  -v $(pwd)/storage:/app/storage \
  localisation-engine
```

**Note:** Docker image uses Python 3.10, which is compatible with all dependencies.

## Production Deployment

For production, consider:

1. **Use Python 3.10 or 3.11** for best compatibility
2. **Install all optional dependencies** for full functionality
3. **Use Celery + Redis** for background processing
4. **Set up proper logging** and monitoring
5. **Configure environment variables** via `.env` file

## Getting Help

If you encounter issues:

1. Check the logs: `docker-compose logs` or application console
2. Verify Python version: `python --version`
3. Check FFmpeg: `ffmpeg -version`
4. Review error messages in job status endpoint
5. Ensure all system dependencies are installed



