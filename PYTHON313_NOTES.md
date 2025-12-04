# Python 3.13 Installation Notes

If you're using Python 3.13, you may encounter some compatibility issues. This document provides solutions.

## Known Issues

### 1. TTS (Coqui TTS) - Not Available for Python 3.13

**Issue:** TTS package doesn't have pre-built wheels for Python 3.13.

**Solutions:**
- **Option 1:** Install from source (may require compilation)
  ```bash
  pip install git+https://github.com/coqui-ai/TTS.git
  ```
- **Option 2:** Use Python 3.11 or 3.12 for TTS functionality
- **Option 3:** Skip TTS - The system will use a fallback mode

**Impact:** TTS audio generation will be disabled, but all other features work.

### 2. Pydantic - Use Latest Version

**Issue:** Older pydantic versions (2.5.0) require Rust compilation for Python 3.13.

**Solution:** Use pydantic 2.12+ which has pre-built wheels:
```bash
pip install "pydantic>=2.12.0"
```

### 3. Some Packages May Require Compilation

**Issue:** Some packages may not have pre-built wheels for Python 3.13 yet.

**Solutions:**
- Install build tools (Windows: Visual Studio Build Tools)
- Use pre-built wheels when available
- Consider using Python 3.11 or 3.12 for better compatibility

## Recommended Setup for Python 3.13

```bash
# 1. Upgrade pip and build tools
pip install --upgrade pip setuptools wheel

# 2. Install core dependencies (these work with Python 3.13)
pip install fastapi uvicorn[standard] python-multipart sqlalchemy celery redis faster-whisper python-dotenv numpy scipy

# 3. Install pydantic (if not already installed)
pip install "pydantic>=2.12.0"

# 4. Skip TTS for now (or install from source)
# pip install git+https://github.com/coqui-ai/TTS.git

# 5. Install IndicTrans2 (optional)
git clone https://github.com/AI4Bharat/IndicTrans2.git
cd IndicTrans2
pip install -e .
cd ..
```

## What Works Without TTS

Even without TTS, the system provides:
- ✅ File upload
- ✅ Audio extraction
- ✅ Speech-to-text transcription
- ✅ Translation to 22 Indic languages
- ✅ Subtitle generation (VTT + SRT)
- ✅ Video dubbing (if you provide TTS audio files manually)

## Testing Without TTS

The system will automatically use a fallback TTS service that creates placeholder files. You can:

1. Upload a video
2. Wait for processing (transcription + translation)
3. Request playback - it will create placeholder audio files
4. Replace placeholder files with real TTS audio if needed

## Alternative: Use Docker

The Dockerfile uses Python 3.10, which has full compatibility:

```bash
docker build -t localisation-engine .
docker run -p 8000:8000 -v $(pwd)/storage:/app/storage localisation-engine
```

This ensures all dependencies work correctly.



