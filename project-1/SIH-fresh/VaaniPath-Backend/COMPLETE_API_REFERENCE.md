# 🎯 Complete API Endpoints Reference

## 📚 Architecture Summary

**Supabase (PostgreSQL):**
- User authentication & management
- Video metadata storage
- Translation data & status
- Quiz questions & sessions
- Review system data
- Enrollment tracking

**Cloudflare R2 (Object Storage):**
- Original video files
- Dubbed video files
- Audio files (TTS output)
- Subtitle files
- Thumbnails

**ML Processing Pipeline:**
1. Whisper ASR → Speech to Text
2. IndicTrans2 → Translation
3. Coqui TTS → Text to Speech
4. FFmpeg → Lip Sync & Dubbing

---

## 🔐 Authentication Endpoints

### POST /api/v1/auth/signup
Register new user (student/teacher)

### POST /api/v1/auth/login
Login with email/password

### GET /api/v1/auth/me
Get current user profile

---

## 👨‍🏫 ADMIN ENDPOINTS (Teachers)

### 🎬 Video Management

#### POST /api/v1/videos/upload
Upload video to Cloudflare R2
- Stores file in R2
- Creates metadata entry in Supabase

#### POST /api/v1/videos/{video_id}/process
**Start Complete Video Processing Pipeline**
```json
{
  "target_languages": ["hi", "ta", "te"],
  "generate_quiz": true,
  "enable_lip_sync": true,
  "quiz_difficulty": "medium"
}
```
Triggers background job that:
1. Extracts audio
2. Transcribes with Whisper
3. Translates with IndicTrans2
4. Generates TTS audio
5. Creates dubbed video with lip sync
6. Generates quiz questions

#### GET /api/v1/videos/{video_id}/processing-status
**Check Processing Status**
Returns:
- Overall progress percentage
- Status of each stage (transcription, translation, TTS, dubbing)
- Estimated time remaining
- Error messages if any

---

### 🎤 Transcription (Whisper ASR)

#### POST /api/v1/transcription/generate
**Generate Transcription from Video**
```json
{
  "video_id": "uuid",
  "model_size": "medium",  // tiny, base, small, medium, large
  "language": "en"
}
```
Returns:
- Full transcription text
- Time-aligned segments
- Duration

---

### 🌐 Translation (IndicTrans2)

#### POST /api/v1/translation/start
**Start Translation Job**
```json
{
  "video_id": "uuid",
  "target_languages": ["hi", "ta", "te"]
}
```

#### GET /api/v1/translation/{job_id}/status
Check translation progress

#### GET /api/v1/translation/{job_id}/quality
Get quality metrics (BLEU score, etc.)

#### POST /api/v1/translation/glossary
**Add Domain-Specific Term**
```json
{
  "source_term": "Neural Network",
  "target_term": "तंत्रिका नेटवर्क",
  "language": "hi",
  "domain": "machine_learning"
}
```

#### GET /api/v1/translation/glossary/{language}?domain=machine_learning
Get all glossary terms for domain

---

### 🔊 Text-to-Speech (Coqui TTS)

#### POST /api/v1/tts/generate
**Generate TTS Audio**
```json
{
  "video_id": "uuid",
  "language": "hi",
  "voice_gender": "neutral",
  "speed": 1.0
}
```
Returns:
- Audio file URL (stored in R2)
- Duration

---

### 📝 Subtitle Generation

#### POST /api/v1/subtitles/generate
**Create Subtitle File**
```json
{
  "video_id": "uuid",
  "language": "hi",
  "format": "vtt"  // srt, vtt, ass
}
```
Returns subtitle file URL

---

### 🎥 Video Dubbing

#### POST /api/v1/dubbing/create
**Create Dubbed Video with Lip Sync**
```json
{
  "video_id": "uuid",
  "language": "hi",
  "enable_lip_sync": true
}
```
Uses FFmpeg to:
- Replace original audio
- Sync lip movements
- Generate final video

Returns dubbed video URL in R2

---

### 🚀 Batch Processing

#### POST /api/v1/batch/process
**Process Multiple Videos**
```json
{
  "video_ids": ["uuid1", "uuid2", "uuid3"],
  "target_languages": ["hi", "ta"],
  "generate_quiz": false
}
```
Queues batch job and returns batch_id

---

### ❓ Quiz Generation

#### POST /api/v1/quiz/generate
**Auto-Generate Quiz Questions**
```json
{
  "video_id": "uuid",
  "num_questions": 5,
  "difficulty": "medium"  // easy, medium, hard
}
```
Uses LLM to generate questions from transcription

#### POST /api/v1/quiz/questions
Manually add quiz question

#### PUT /api/v1/quiz/questions/{question_id}
Edit question

#### DELETE /api/v1/quiz/questions/{question_id}
Delete question

---

### ✅ Review System

#### GET /api/v1/review/pending?language=hi
**Get Pending Translations for Review**

#### POST /api/v1/review/submit
**Submit Review**
```json
{
  "translation_id": "uuid",
  "approved": true,
  "feedback": "Good translation",
  "corrections": null
}
```

#### GET /api/v1/review/history
Get review history

#### GET /api/v1/review/stats
Get review statistics

---

### 🤖 Model Information

#### GET /api/v1/models/info
**Get ML Models Status**
Returns:
- Whisper model info (version, languages, memory usage)
- IndicTrans2 model info
- TTS model info
- GPU availability
- Total memory usage

---

### 📊 Admin Dashboard

#### GET /api/v1/admin/stats
Platform statistics

#### GET /api/v1/admin/users
All users list

#### GET /api/v1/admin/videos
All videos with processing status

#### POST /api/v1/admin/users/{user_id}/toggle-status
Enable/disable user

---

## 👨‍🎓 STUDENT ENDPOINTS

### 📺 Video Access

#### GET /api/v1/videos
List enrolled videos

#### GET /api/v1/videos/{video_id}
Get video details with all available languages

#### POST /api/v1/videos/{video_id}/enroll
Enroll in video course

---

### 📖 Transcription & Translation

#### GET /api/v1/transcription/{video_id}?language=en&include_segments=true
**Get Transcription**
Returns original transcription

#### GET /api/v1/translation/{video_id}/{language}?include_segments=true
**Get Translation**
Returns translated text with segments

---

### 🔊 Audio & Video

#### GET /api/v1/tts/{video_id}/{language}
**Download TTS Audio**
Returns audio file URL

#### GET /api/v1/dubbing/{video_id}/{language}
**Get Dubbed Video**
Returns final video URL with lip sync

---

### 📝 Subtitles

#### GET /api/v1/subtitles/{video_id}/{language}?format=vtt
**Get Subtitles**
Returns subtitle file URL

#### GET /api/v1/subtitles/download/{subtitle_id}
**Direct Download**
Streams subtitle file

---

### 🎮 Quiz System

#### GET /api/v1/quiz/video/{video_id}/questions?language=en
**Get Quiz Questions**

#### POST /api/v1/quiz/start/{video_id}
**Start Quiz Session**

#### POST /api/v1/quiz/answer
**Submit Answer**
```json
{
  "session_id": "uuid",
  "question_id": "uuid",
  "selected_option": "A"
}
```

#### POST /api/v1/quiz/complete/{session_id}
**Complete Quiz**

#### GET /api/v1/quiz/session/{session_id}/results
**Get Quiz Results**

#### GET /api/v1/quiz/leaderboard/{video_id}?limit=10
**View Leaderboard**

---

## 🔄 Complete Processing Flow

### Admin Side:
```
1. Upload Video → R2 Storage + Supabase metadata
2. Start Processing → Trigger ML Pipeline
3. Monitor Status → Check progress
4. Review Translation → Quality check
5. Approve & Publish → Make available to students
```

### ML Pipeline (Background):
```
1. Extract Audio from Video
2. Whisper ASR → Transcription
3. IndicTrans2 → Translation
4. Coqui TTS → Generate Speech
5. FFmpeg → Lip Sync + Dubbing
6. Upload to R2 → Update Supabase
7. Generate Quiz Questions (optional)
```

### Student Side:
```
1. Browse Videos → See available courses
2. Enroll in Video → Get access
3. Watch Dubbed Video → In preferred language
4. View Subtitles → Optional
5. Take Quiz → Test understanding
6. View Results → Check score
```

---

## 🎯 Total Endpoints Count

**Admin (Teachers):** 25 endpoints
- Video Processing: 3
- Transcription: 1
- Translation: 5
- TTS: 1
- Subtitles: 1
- Dubbing: 1
- Batch: 1
- Quiz: 4
- Review: 4
- Models: 1
- Admin: 4

**Students:** 13 endpoints
- Videos: 3
- Transcription: 1
- Translation: 1
- Audio: 1
- Dubbing: 1
- Subtitles: 2
- Quiz: 7

**Authentication:** 3 endpoints

**TOTAL: 41 endpoints** ✅

---

## 🗄️ Database Tables (Supabase)

1. **users** - Authentication & profiles
2. **videos** - Video metadata
3. **translations** - Translation data & status
4. **enrollments** - Student enrollments
5. **glossary** - Domain-specific terms
6. **quiz_questions** - Quiz questions
7. **quiz_sessions** - Quiz attempts
8. **user_answers** - Quiz responses
9. **reviews** - Translation reviews
10. **processing_jobs** - ML job tracking
11. **cultural_adaptations** - Cultural context

---

## 📦 Storage Structure (Cloudflare R2)

```
gyanify-videos/
├── uploads/
│   └── {video_id}_original.mp4
├── dubbed/
│   └── {video_id}_{language}.mp4
├── audio/
│   └── {video_id}_{language}.mp3
├── subtitles/
│   └── {video_id}_{language}.vtt
└── thumbnails/
    └── {video_id}_thumb.jpg
```

---

## 🚀 Quick Start for Developers

### 1. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 2. Environment Variables
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key
R2_ACCOUNT_ID=your_r2_account_id
R2_ACCESS_KEY_ID=your_access_key
R2_SECRET_ACCESS_KEY=your_secret_key
R2_BUCKET_NAME=gyanify-videos
```

### 3. Test API
Visit: http://localhost:8000/docs

---

## 📝 Notes

- All endpoints except `/auth/signup` and `/auth/login` require JWT token
- Admin endpoints require `role=teacher`
- Student endpoints require `role=student`
- Mock mode works without database (for testing)
- ML processing runs in background (Celery tasks)
- Files stored in R2 with CDN URLs
- Database handles metadata & relationships
