# Python Version Requirements

## Summary

Based on your Python 3.12.0 installation, here's what works and what doesn't:

### ❌ TTS (Coqui TTS) - **NOT Compatible with Python 3.12**

**Requirement:** Python >= 3.9 and **< 3.12** (so Python 3.9, 3.10, or 3.11)

**Your Version:** Python 3.12.0 ❌

**Solution:**
- **Option 1:** Use Python 3.11 (recommended)
- **Option 2:** Use Docker (Python 3.10)
- **Option 3:** Wait for TTS to support Python 3.12+ (or use fallback mode)

### ⚠️ IndicTrans2 / IndicTransToolkit - **Requires C++ Build Tools**

**Requirement:** Python 3.12 is compatible, but needs Microsoft Visual C++ 14.0+ to compile

**Your Version:** Python 3.12.0 ✅ (compatible, but needs build tools)

**Solution:**
1. Install Microsoft Visual C++ Build Tools:
   - Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Install "Desktop development with C++" workload
   - Then run: `pip install IndicTransToolkit`

2. **Alternative:** Use HuggingFace models directly (avoids IndicTransToolkit compilation)

## Recommended Python Versions

### For Full Compatibility (TTS + IndicTrans2):

**Best Option: Python 3.11**
- ✅ TTS works
- ✅ IndicTrans2 works
- ✅ All dependencies compatible

**Second Best: Python 3.10**
- ✅ TTS works
- ✅ IndicTrans2 works
- ✅ Very stable

**Third Option: Python 3.9**
- ✅ TTS works
- ✅ IndicTrans2 works
- ⚠️ Older, but still supported

### Current Status with Python 3.12:

| Package | Status | Notes |
|---------|--------|-------|
| TTS | ❌ Not compatible | Requires Python < 3.12 |
| IndicTransToolkit | ⚠️ Needs C++ Build Tools | Python 3.12 OK, but needs compilation |
| Core packages | ✅ All working | FastAPI, Whisper, etc. |

## Quick Solutions

### Solution 1: Install Python 3.11 (Recommended)

1. Download Python 3.11: https://www.python.org/downloads/release/python-3110/
2. Install Python 3.11
3. Create new virtual environment:
   ```bash
   python3.11 -m venv venv311
   venv311\Scripts\activate  # Windows
   pip install -r requirements.txt
   pip install TTS
   pip install IndicTransToolkit  # Still needs C++ Build Tools
   ```

### Solution 2: Use Docker (Easiest)

```bash
docker-compose up -d
```

This uses Python 3.10 with all dependencies pre-built.

### Solution 3: Install C++ Build Tools (For IndicTrans2)

1. Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Install "Desktop development with C++"
3. Restart terminal
4. Run: `pip install IndicTransToolkit`

**Note:** TTS still won't work with Python 3.12 even with C++ Build Tools.

## What Works Now (Python 3.12)

✅ **Core System:**
- FastAPI
- Uvicorn
- SQLAlchemy
- Faster-Whisper (STT)
- PyTorch
- Transformers
- All other dependencies

✅ **Features:**
- File uploads
- Audio extraction
- Speech-to-text transcription
- Subtitle generation
- Job management

⚠️ **Using Fallbacks:**
- Translation (returns original text)
- TTS (creates placeholder files)

## Recommendation

**For best results, use Python 3.11:**
- Full TTS support
- Full IndicTrans2 support
- All features work

**Or use Docker:**
- No Python version management needed
- Everything pre-configured
- Python 3.10 with all dependencies


