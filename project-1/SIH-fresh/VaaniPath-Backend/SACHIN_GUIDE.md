# 🎯 Sachin Ke Liye - Personal Implementation Guide

## ✅ Aaj Kya Complete Hua (Day 1)

Bhai congratulations! 🎉 Backend ka pura foundation ready hai:

### Completed:
- ✅ FastAPI project structure
- ✅ Virtual environment setup
- ✅ All API endpoints (structure)
- ✅ Authentication system
- ✅ Database schema designed
- ✅ Configuration management
- ✅ Server running successfully
- ✅ All features included (Lip sync, Cultural adaptation, Review - sab kuch)

### What's Working Right Now:
- Server: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health check endpoint
- All routes registered (implementation pending)

---

## 📅 Day-wise Detailed Plan (Tumhare Liye)

### **Day 2: Database + Video Upload** (Tomorrow)

#### Morning (2-3 hours):
1. **Supabase Setup**
   ```
   - Go to https://supabase.com
   - Sign up (free tier)
   - Create new project: "gyanify-sih"
   - Wait 2-3 min for setup
   ```

2. **Run Database Schema**
   ```
   - Open Supabase dashboard
   - SQL Editor → New query
   - Copy entire `app/schemas/tables.sql` content
   - Run
   - Check if 9 tables created
   ```

3. **Update .env File**
   ```
   - Project Settings → API
   - Copy:
     * Project URL → SUPABASE_URL
     * anon public → SUPABASE_KEY
     * service_role → SUPABASE_SERVICE_KEY
   - Paste in .env file
   ```

#### Afternoon (3-4 hours):
4. **Implement Video Upload**

   File: `app/api/v1/endpoints/videos.py`
   
   ```python
   # Replace upload_video function with:
   
   @router.post("/upload", response_model=VideoResponse, status_code=status.HTTP_201_CREATED)
   async def upload_video(
       file: UploadFile = File(...),
       title: str = Form(...),
       description: Optional[str] = Form(None),
       domain: DomainType = Form(...),
       source_language: str = Form("en"),
       target_languages: str = Form(...),
       current_user: dict = Depends(get_current_admin)
   ):
       try:
           # 1. Validate file format
           ext = file.filename.split(".")[-1].lower()
           if ext not in settings.video_formats_list:
               raise HTTPException(400, "Invalid video format")
           
           # 2. Upload to Supabase Storage
           file_content = await file.read()
           file_path = f"videos/{uuid.uuid4()}.{ext}"
           
           supabase.storage.from_("videos").upload(
               file_path,
               file_content,
               {"content-type": file.content_type}
           )
           
           # 3. Get public URL
           file_url = supabase.storage.from_("videos").get_public_url(file_path)
           
           # 4. Create DB entry
           video_data = {
               "title": title,
               "description": description,
               "domain": domain,
               "source_language": source_language,
               "target_languages": target_languages.split(","),
               "status": "uploaded",
               "uploaded_by": current_user["id"],
               "file_url": file_url
           }
           
           response = supabase.table("videos").insert(video_data).execute()
           
           # 5. Trigger processing job (later)
           
           return response.data[0]
           
       except Exception as e:
           logger.error(f"Upload error: {e}")
           raise HTTPException(500, str(e))
   ```

5. **Test Upload**
   - Use http://localhost:8000/docs
   - First create admin user via /auth/signup
   - Login to get token
   - Try upload with token

---

### **Day 3-4: ASR (Whisper) Integration**

#### Setup Whisper:
```powershell
# Install
pip install openai-whisper

# Test download
python -c "import whisper; whisper.load_model('medium')"
```

#### Create ASR Service:

File: `app/services/asr_service.py`

```python
import whisper
import os
from app.config import settings

class ASRService:
    def __init__(self):
        self.model = None
    
    def load_model(self):
        if self.model is None:
            self.model = whisper.load_model(settings.WHISPER_MODEL_SIZE)
    
    def transcribe(self, video_path: str):
        self.load_model()
        
        result = self.model.transcribe(
            video_path,
            language="en",
            task="transcribe",
            verbose=False
        )
        
        return {
            "text": result["text"],
            "segments": result["segments"]  # Time-stamped
        }

asr_service = ASRService()
```

#### Create Celery Task:

File: `app/workers/tasks.py`

```python
from celery import Celery
from app.config import settings
from app.services.asr_service import asr_service
import logging

celery_app = Celery(
    "gyanify",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

@celery_app.task
def process_video_asr(video_id: str, video_url: str):
    """Background task for ASR"""
    try:
        logger.info(f"Starting ASR for video {video_id}")
        
        # Download video locally
        # ... download code ...
        
        # Transcribe
        result = asr_service.transcribe(video_path)
        
        # Save to Supabase
        # ... save transcript ...
        
        logger.info(f"ASR complete for {video_id}")
        return {"status": "success", "video_id": video_id}
        
    except Exception as e:
        logger.error(f"ASR error: {e}")
        return {"status": "failed", "error": str(e)}
```

---

### **Day 5-6: Translation (IndicTrans2)**

#### Install IndicTrans2:
```powershell
pip install transformers sentencepiece torch
```

#### Create Translation Service:

File: `app/services/translation_service.py`

```python
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from app.config import settings

class TranslationService:
    def __init__(self):
        self.tokenizer = None
        self.model = None
    
    def load_model(self):
        if self.model is None:
            self.tokenizer = AutoTokenizer.from_pretrained(
                settings.TRANSLATION_MODEL
            )
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                settings.TRANSLATION_MODEL
            )
    
    def translate(self, text: str, target_lang: str):
        self.load_model()
        
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        )
        
        outputs = self.model.generate(**inputs)
        translated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return translated

translation_service = TranslationService()
```

---

### **Day 7-8: TTS (Text-to-Speech)**

#### Install Coqui TTS:
```powershell
pip install TTS
```

#### Create TTS Service:

File: `app/services/tts_service.py`

```python
from TTS.api import TTS
import os

class TTSService:
    def __init__(self):
        self.tts = None
    
    def load_model(self):
        if self.tts is None:
            self.tts = TTS("tts_models/multilingual/multi-dataset/your_tts")
    
    def generate_audio(self, text: str, language: str, output_path: str):
        self.load_model()
        
        self.tts.tts_to_file(
            text=text,
            language=language,
            file_path=output_path
        )
        
        return output_path

tts_service = TTSService()
```

---

### **Day 9: Lip Sync + Video Processing**

#### Install FFmpeg:
```powershell
# Download from: https://ffmpeg.org/download.html
# Add to PATH
```

#### Install Python FFmpeg:
```powershell
pip install ffmpeg-python moviepy
```

#### Create Video Service:

File: `app/services/video_service.py`

```python
import ffmpeg
from moviepy.editor import VideoFileClip, AudioFileClip

class VideoService:
    def combine_audio_video(self, video_path: str, audio_path: str, output_path: str):
        """Replace video audio with translated audio"""
        video = VideoFileClip(video_path)
        audio = AudioFileClip(audio_path)
        
        # Adjust audio speed if needed for lip sync
        if audio.duration > video.duration:
            audio = audio.speedx(audio.duration / video.duration)
        
        final = video.set_audio(audio)
        final.write_videofile(output_path)
        
        return output_path

video_service = VideoService()
```

---

### **Day 10: Cultural Adaptation**

#### Create Cultural Adapter:

File: `app/services/cultural_adapter.py`

```python
import yaml
from typing import Dict

class CulturalAdapter:
    def __init__(self):
        self.rules = self.load_rules()
    
    def load_rules(self):
        # Load from YAML
        # Format: {pattern: {hi: replacement, ta: replacement}}
        return {}
    
    def adapt(self, text: str, language: str, domain: str):
        """Apply cultural adaptations"""
        adapted = text
        
        # Apply domain-specific examples
        # Apply regional references
        # Apply polite forms
        
        return adapted

cultural_adapter = CulturalAdapter()
```

---

### **Day 11: Glossary + Review System**

Already structured - just implement database CRUD.

---

### **Day 12: Testing + Demo Prep**

1. Create 3 sample videos
2. Test full pipeline
3. Prepare demo script
4. Fix bugs

---

## 🛠️ Useful Code Snippets

### 1. Supabase File Upload:
```python
from supabase import create_client

supabase = create_client(url, key)

# Upload
supabase.storage.from_("bucket").upload("path", file_bytes)

# Get URL
url = supabase.storage.from_("bucket").get_public_url("path")
```

### 2. JWT Token:
```python
from app.core.security import create_access_token

token = create_access_token(data={"sub": user_id})
```

### 3. Background Task:
```python
from app.workers.tasks import process_video_asr

# Trigger
task = process_video_asr.delay(video_id, video_url)

# Check status
task.ready()
task.result
```

---

## 🚨 Common Errors & Solutions

### 1. Import Error
```
Solution: Make sure venv activated
.\venv\Scripts\Activate.ps1
```

### 2. Supabase Error
```
Solution: Check .env credentials
Test connection: python -c "from app.db.supabase_client import supabase; print(supabase)"
```

### 3. GPU Not Found
```
Solution: Check USE_GPU in .env
Or install CUDA if you have NVIDIA GPU
```

### 4. FFmpeg Not Found
```
Solution: Install FFmpeg
Add to PATH
Test: ffmpeg -version
```

---

## 📝 Testing Checklist

### Before Each Feature:
- [ ] Write endpoint
- [ ] Test in Swagger UI
- [ ] Check database entry
- [ ] Check logs
- [ ] Test error cases

### Full Pipeline Test:
1. Upload video
2. Check ASR output
3. Check translation
4. Check TTS generation
5. Check final video
6. Verify quality

---

## 🎯 Demo Day Strategy

### What to Show (8-10 min):

1. **Intro** (1 min)
   - Problem statement
   - Our solution

2. **Live Demo** (5 min)
   - Upload 2-min video
   - Show real-time progress
   - Display translated versions (3 languages)
   - Play side-by-side comparison
   - Show quiz questions

3. **Features Highlight** (2 min)
   - Domain glossary
   - Cultural adaptation examples
   - Quality metrics
   - Review system

4. **Architecture** (1 min)
   - Tech stack slide
   - Scalability
   - Future scope

### Pre-Demo Checklist:
- [ ] 3 sample videos ready (IT, Healthcare, Construction)
- [ ] All translations pre-generated
- [ ] Live upload tested
- [ ] Backup plan if internet fails
- [ ] PowerPoint ready
- [ ] Team roles assigned

---

## 💡 Pro Tips

1. **GPU Usage**: 
   - Use for Whisper Medium
   - Use for TTS
   - CPU ok for IndicTrans2 (smaller model)

2. **Performance**:
   - Cache loaded models
   - Use Redis for queue
   - Process in background

3. **Quality**:
   - Human review for demo videos
   - Pre-load glossaries
   - Test with domain experts

4. **Backup**:
   - Save all outputs
   - Version control (Git)
   - Daily backups

---

## 📞 When Stuck

### Debug Process:
1. Check logs: `logs/app.log`
2. Check Supabase tables
3. Test individual functions
4. Use print statements
5. Ask ChatGPT/Claude

### Resources:
- FastAPI: https://fastapi.tiangolo.com
- Whisper: https://github.com/openai/whisper
- IndicTrans2: https://github.com/AI4Bharat/IndicTrans2
- Supabase: https://supabase.com/docs

---

## ✅ Today's Summary

**Completed**:
- Project structure ✅
- Server running ✅
- All endpoints planned ✅
- Database schema ready ✅

**Next**: Database setup + Video upload

**Time**: ~10-12 days to complete

**Status**: On track! 🚀

---

**Yaad Rahe**: 
- Daily commit karo Git pe
- Test karte jao
- Documentation update karte jao
- Team ko sync mein rakho

**All the best bhai!** 💪🔥
