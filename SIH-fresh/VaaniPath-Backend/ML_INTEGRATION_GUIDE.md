# 🤖 ML Integration Guide - For ML Team Member

## 👋 Introduction

Bhai, yeh guide tumhare liye hai! Backend sab ready hai, ab tum ML models integrate karo.

---

## 📁 File Structure

```
backend/
├── app/
│   ├── services/
│   │   └── ml_service.py        ← YOU WORK HERE! 🎯
│   ├── workers/
│   │   └── tasks.py              ← Celery tasks (create this)
│   └── api/v1/endpoints/
│       ├── translation.py        ← Calls your ML functions
│       ├── quiz.py               ← Calls your quiz generation
│       └── ...
├── models/                       ← Put your ML model files here
│   ├── whisper/
│   ├── indictrans2/
│   └── tts/
└── glossaries/                   ← Domain glossaries (JSON files)
    ├── it.json
    ├── healthcare.json
    └── ...
```

---

## 🎯 Your Main Task

**File to Edit:** `app/services/ml_service.py`

Yeh file me saare functions already defined hain with detailed docstrings.
Tumhe bas implementation add karna hai!

---

## 🚀 Step-by-Step Implementation

### Step 1: Setup Environment

```powershell
cd D:\backend
.\venv\Scripts\Activate.ps1

# Install ML dependencies
pip install torch torchaudio transformers
pip install openai-whisper
pip install TTS
pip install sacrebleu
pip install ffmpeg-python
```

### Step 2: Test Individual Functions

Start with one function at a time:

#### Example: Implement Audio Extraction

```python
# In ml_service.py

import ffmpeg

def extract_audio_from_video(video_path: str, output_audio_path: str) -> bool:
    """Extract audio from video file using FFmpeg"""
    try:
        ffmpeg.input(video_path).output(
            output_audio_path,
            acodec='pcm_s16le',
            ar='16000',
            ac=1
        ).run(overwrite_output=True)
        
        logger.info(f"Audio extracted successfully: {output_audio_path}")
        return True
        
    except Exception as e:
        logger.error(f"Audio extraction failed: {e}")
        return False
```

**Test it:**
```python
# Create a test file: test_ml.py
from app.services.ml_service import extract_audio_from_video

success = extract_audio_from_video(
    "path/to/video.mp4",
    "output/audio.wav"
)
print(f"Success: {success}")
```

---

### Step 3: Implement Whisper ASR

```python
import whisper
from app.config import settings

# Load model once (global)
_whisper_model = None

def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        _whisper_model = whisper.load_model(settings.WHISPER_MODEL_SIZE)
    return _whisper_model


def transcribe_audio(audio_path: str, source_language: str = "en") -> Dict[str, any]:
    """Transcribe audio to text using Whisper ASR"""
    try:
        model = get_whisper_model()
        
        result = model.transcribe(
            audio_path,
            language=source_language,
            task="transcribe",
            verbose=False
        )
        
        return {
            "text": result["text"],
            "segments": [
                {
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": seg["text"]
                }
                for seg in result["segments"]
            ],
            "language": result["language"],
            "duration": result["segments"][-1]["end"] if result["segments"] else 0
        }
        
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise
```

**Test it:**
```python
from app.services.ml_service import transcribe_audio

transcript = transcribe_audio("audio.wav", "en")
print(f"Transcript: {transcript['text']}")
print(f"Segments: {len(transcript['segments'])}")
```

---

### Step 4: Implement Translation (IndicTrans2)

```python
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Load models (global)
_translation_models = {}

def get_translation_model(source_lang: str, target_lang: str):
    """Load or get cached translation model"""
    key = f"{source_lang}_{target_lang}"
    
    if key not in _translation_models:
        model_name = settings.TRANSLATION_MODEL
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        
        _translation_models[key] = {
            "tokenizer": tokenizer,
            "model": model
        }
    
    return _translation_models[key]


def translate_text(
    text: str,
    source_language: str,
    target_language: str,
    domain: Optional[str] = None,
    glossary: Optional[Dict[str, str]] = None
) -> str:
    """Translate text using IndicTrans2"""
    try:
        # Get model
        mt = get_translation_model(source_language, target_language)
        tokenizer = mt["tokenizer"]
        model = mt["model"]
        
        # Apply glossary (pre-processing)
        processed_text = text
        if glossary:
            for source_term, target_term in glossary.items():
                # Simple replacement (you can make this smarter)
                processed_text = processed_text.replace(source_term, f"[GLOSS]{target_term}[/GLOSS]")
        
        # Tokenize
        inputs = tokenizer(processed_text, return_tensors="pt", padding=True)
        
        # Translate
        outputs = model.generate(**inputs, max_length=512)
        
        # Decode
        translated = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Post-process glossary markers
        translated = translated.replace("[GLOSS]", "").replace("[/GLOSS]", "")
        
        return translated
        
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        raise
```

---

### Step 5: Implement TTS (Coqui TTS)

```python
from TTS.api import TTS

_tts_models = {}

def get_tts_model(language: str):
    """Load or get cached TTS model"""
    if language not in _tts_models:
        # Select appropriate model for language
        model_name = settings.TTS_MODEL
        _tts_models[language] = TTS(model_name)
    
    return _tts_models[language]


def generate_speech(
    text: str,
    language: str,
    output_audio_path: str,
    voice_gender: str = "neutral",
    speed: float = 1.0
) -> bool:
    """Generate speech from text using TTS"""
    try:
        tts = get_tts_model(language)
        
        tts.tts_to_file(
            text=text,
            file_path=output_audio_path,
            language=language,
            speed=speed
        )
        
        logger.info(f"Speech generated: {output_audio_path}")
        return True
        
    except Exception as e:
        logger.error(f"TTS generation failed: {e}")
        return False
```

---

### Step 6: Implement Quiz Generation

```python
import spacy
import random

# Load NLP model
_nlp = None

def get_nlp_model():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp


def generate_quiz_questions(
    transcript: str,
    video_duration: float,
    num_questions: int = 5,
    difficulty: str = "medium",
    language: str = "en"
) -> List[Dict]:
    """Auto-generate quiz questions from transcript"""
    try:
        nlp = get_nlp_model()
        doc = nlp(transcript)
        
        questions = []
        
        # Extract named entities for MCQ
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        
        # Extract key sentences
        sentences = [sent.text for sent in doc.sents if len(sent.text.split()) > 5]
        
        for i in range(min(num_questions, len(sentences))):
            sentence = sentences[i]
            
            # Simple question generation (you can use T5/GPT for better results)
            question = {
                "question_text": f"What is discussed in: '{sentence[:50]}...'?",
                "question_type": "multiple_choice",
                "options": [
                    "Option A - Correct",
                    "Option B - Incorrect",
                    "Option C - Incorrect",
                    "Option D - Incorrect"
                ],
                "correct_answer": "Option A - Correct",
                "difficulty": difficulty,
                "timestamp": (video_duration / num_questions) * i,
                "explanation": f"This is covered in the segment around {int((video_duration / num_questions) * i)}s"
            }
            
            questions.append(question)
        
        return questions
        
    except Exception as e:
        logger.error(f"Quiz generation failed: {e}")
        return []
```

---

### Step 7: Complete Pipeline Integration

```python
def process_video_translation(
    video_id: str,
    video_path: str,
    target_language: str,
    domain: str,
    enable_lip_sync: bool = True,
    glossary: Optional[Dict[str, str]] = None,
    progress_callback: Optional[callable] = None
) -> Dict[str, str]:
    """Complete end-to-end video translation pipeline"""
    
    try:
        logger.info(f"Starting translation pipeline for video {video_id}")
        
        # Create temp directory
        temp_dir = settings.TEMP_DIR / video_id
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Step 1: Extract audio (5%)
        if progress_callback:
            progress_callback(5, "Extracting audio")
        
        audio_path = temp_dir / "audio.wav"
        if not extract_audio_from_video(video_path, str(audio_path)):
            raise Exception("Audio extraction failed")
        
        # Step 2: Transcribe (25%)
        if progress_callback:
            progress_callback(25, "Transcribing audio")
        
        transcript_data = transcribe_audio(str(audio_path))
        
        # Save transcript
        transcript_path = temp_dir / "transcript.txt"
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(transcript_data["text"])
        
        # Step 3: Translate (50%)
        if progress_callback:
            progress_callback(50, "Translating content")
        
        translated_segments = translate_segments(
            transcript_data["segments"],
            "en",  # Source language
            target_language,
            domain,
            glossary
        )
        
        # Save translated text
        translated_path = temp_dir / f"translated_{target_language}.txt"
        with open(translated_path, 'w', encoding='utf-8') as f:
            f.write("\n".join([seg["text"] for seg in translated_segments]))
        
        # Step 4: Generate TTS (70%)
        if progress_callback:
            progress_callback(70, "Generating speech")
        
        tts_audio_path = temp_dir / f"audio_{target_language}.mp3"
        full_text = " ".join([seg["text"] for seg in translated_segments])
        generate_speech(full_text, target_language, str(tts_audio_path))
        
        # Step 5: Generate subtitles (85%)
        if progress_callback:
            progress_callback(85, "Generating subtitles")
        
        subtitle_path = temp_dir / f"subtitles_{target_language}.srt"
        generate_subtitles(translated_segments, str(subtitle_path))
        
        # Step 6: Lip sync (90%, optional)
        video_url = None
        if enable_lip_sync:
            if progress_callback:
                progress_callback(90, "Synchronizing lips")
            
            synced_video_path = temp_dir / f"video_{target_language}.mp4"
            if synchronize_lip_movement(
                video_path,
                str(tts_audio_path),
                str(synced_video_path)
            ):
                video_url = str(synced_video_path)
        
        # Step 7: Calculate quality (95%)
        if progress_callback:
            progress_callback(95, "Calculating quality")
        
        quality = calculate_translation_quality(
            transcript_data["text"],
            full_text
        )
        
        # Step 8: Done (100%)
        if progress_callback:
            progress_callback(100, "Completed")
        
        # Return file paths (these will be uploaded to R2 by the endpoint)
        return {
            "transcript_url": str(transcript_path),
            "translated_text_url": str(translated_path),
            "audio_url": str(tts_audio_path),
            "subtitle_url": str(subtitle_path),
            "video_url": video_url,
            "quality_score": quality.get("overall", 0)
        }
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise
```

---

## 🧪 Testing Your Implementation

### Create Test Script: `test_ml_pipeline.py`

```python
from app.services.ml_service import process_video_translation

def progress_callback(percent, message):
    print(f"[{percent}%] {message}")

# Test with a sample video
result = process_video_translation(
    video_id="test-123",
    video_path="path/to/test/video.mp4",
    target_language="hi",  # Hindi
    domain="it",
    enable_lip_sync=False,  # Start with False for faster testing
    glossary={"Python": "पायथन", "variable": "चर"},
    progress_callback=progress_callback
)

print("\n✅ Translation Complete!")
print(f"Transcript: {result['transcript_url']}")
print(f"Audio: {result['audio_url']}")
print(f"Quality: {result['quality_score']}")
```

Run it:
```powershell
python test_ml_pipeline.py
```

---

## 📊 Performance Optimization Tips

### 1. Model Caching
```python
# Load models once, reuse multiple times
_models_cache = {}

def get_model(model_name):
    if model_name not in _models_cache:
        _models_cache[model_name] = load_model(model_name)
    return _models_cache[model_name]
```

### 2. Batch Processing
```python
# Process multiple segments together
def translate_segments_batch(segments, batch_size=32):
    results = []
    for i in range(0, len(segments), batch_size):
        batch = segments[i:i+batch_size]
        results.extend(model.translate_batch(batch))
    return results
```

### 3. GPU Usage
```python
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)
```

---

## 🐛 Debugging Tips

### Enable Detailed Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Save Intermediate Results
```python
# Save after each step for debugging
import json

with open("debug_transcript.json", "w") as f:
    json.dump(transcript_data, f, indent=2)
```

### Test Individual Functions
```python
# Don't test the whole pipeline at once!
# Test each function separately first

# Test 1: Audio extraction
extract_audio_from_video("test.mp4", "test.wav")

# Test 2: Transcription
transcript = transcribe_audio("test.wav")

# Test 3: Translation
translated = translate_text(transcript["text"], "en", "hi")
```

---

## 📝 Checklist for ML Team

```
Phase 1: Basic Setup (Day 1)
□ Install dependencies
□ Test FFmpeg
□ Load Whisper model
□ Test audio extraction + transcription

Phase 2: Translation (Day 2-3)
□ Load IndicTrans2 model
□ Test simple translation
□ Implement glossary support
□ Test with different languages

Phase 3: TTS (Day 4)
□ Load TTS model
□ Test speech generation
□ Test with different languages
□ Optimize audio quality

Phase 4: Advanced Features (Day 5-7)
□ Implement lip sync (optional first)
□ Subtitle generation
□ Quiz auto-generation
□ Quality metrics

Phase 5: Integration (Day 8-10)
□ Complete pipeline function
□ Error handling
□ Progress callbacks
□ Performance optimization
```

---

## 🤝 Integration with Backend

Once you implement functions in `ml_service.py`, they automatically work with:

✅ `/api/v1/translation/start` - Calls your pipeline
✅ `/api/v1/quiz/video/{id}/generate` - Calls quiz generation
✅ Background Celery tasks - Process videos async

**You don't need to touch endpoint files!** Just implement `ml_service.py`

---

## 💬 Need Help?

**Questions to Ask:**
- "Whisper model kaise load karein?"
- "IndicTrans2 ke liye best practices?"
- "GPU memory kam hai, optimize kaise karein?"

**Debugging:**
- Check logs in `logs/app.log`
- Test individual functions first
- Use small test videos initially

---

## ✅ Summary

**Your Job:**
1. Open `app/services/ml_service.py`
2. Implement functions one by one
3. Test each function separately
4. Integrate into complete pipeline
5. Done! 🎉

**Backend handles:**
- API endpoints ✅
- Database ✅
- File storage ✅
- Authentication ✅
- Job queue ✅

**Tumhara focus:** ML models ko integrate karna! 💪

---

**Good luck bhai! Koi doubt ho to pooch lena!** 🚀
