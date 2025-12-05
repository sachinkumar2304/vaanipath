# ML Service Quick Start Guide

## Issue: Relative Import Error
The ML service has relative imports that prevent it from running directly.

## Solution Options:

### Option 1: Run as Python Module (RECOMMENDED)
```bash
cd d:\project-1\VaaniPath-Localizer
python -m localizer.api
```

### Option 2: Update PYTHONPATH
```bash
cd d:\project-1\VaaniPath-Localizer
set PYTHONPATH=%CD%
cd localizer
uvicorn api:app --host 0.0.0.0 --port 8001 --reload
```

### Option 3: Create Wrapper Script
Create `run_ml_service.py` in `VaaniPath-Localizer/` folder:

```python
import sys
import os
# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Now import and run
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "localizer.api:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
```

Then run:
```bash
cd d:\project-1\VaaniPath-Localizer
python run_ml_service.py
```

## Verify Service is Running

Once started, test:
```bash
curl http://localhost:8001/voices
```

Should return list of available voices.

## Integration with VaaniPath-Backend

After ML service is running:

1. Add to `.env`:
```env
ML_SERVICE_URL=http://localhost:8001
```

2. Video upload will automatically trigger translation

3. Translated videos will be stored in:
```
VaaniPath-Localizer/localizer/output/{video_id}/final_video.mp4
```

## For Production

- Deploy ML service separately (Docker container)
- Use environment variable for ML_SERVICE_URL
- Consider using message queue (Celery/RabbitMQ) for async processing
