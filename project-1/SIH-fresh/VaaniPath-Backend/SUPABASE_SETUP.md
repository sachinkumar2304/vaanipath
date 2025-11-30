# 🚀 SUPABASE SETUP GUIDE - GYANIFY

## **STEP 1: Create Supabase Project**

### A. Go to Supabase
1. Open browser: https://supabase.com
2. Click **Sign Up** (or Login if you have account)
3. Create account with GitHub or email

### B. Create New Project
1. Click **New Project**
2. Fill details:
   - **Project Name**: `gyanify`
   - **Database Password**: Create strong password (save it!)
   - **Region**: `Asia Pacific (Singapore)` (best for India)
3. Click **Create New Project**
4. Wait 5-10 minutes for project to be ready

### C. Get Your Credentials
Once project is ready:

1. Go to **Settings** → **API**
2. Copy these values:
   ```
   Project URL: https://xxxxx.supabase.co
   anon public: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   service_role: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

3. Open `.env` file in backend folder
4. Add these values:
   ```bash
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

---

## **STEP 2: Create Database Schema**

### A. Open SQL Editor
1. In Supabase dashboard, click **SQL Editor** (left sidebar)
2. Click **New Query**

### B. Copy & Run Schema
1. Open file: `database/schema.sql` (in backend folder)
2. Copy ALL the SQL code
3. Paste in Supabase SQL Editor
4. Click **Run** button (or Ctrl+Enter)
5. Wait for execution to complete

**Expected Output:**
```
✅ All tables created successfully
✅ Indexes created
✅ RLS policies enabled
```

---

## **STEP 3: Verify Setup**

### A. Check Tables in Supabase
1. Go to **Table Editor** (left sidebar)
2. You should see these tables:
   - ✅ users
   - ✅ videos
   - ✅ transcriptions
   - ✅ translations
   - ✅ subtitles
   - ✅ quiz_questions
   - ✅ quiz_responses
   - ✅ enrollments
   - ✅ reviews
   - ✅ glossary_terms
   - ✅ processing_jobs

### B. Test Connection from Backend
1. Open terminal in backend folder
2. Run:
   ```bash
   py -3.12 -m uvicorn app.main:app --reload
   ```

3. Check logs for:
   ```
   ✅ Supabase client initialized successfully
   ```

---

## **STEP 4: Database Schema Overview**

### **Users Table**
```
- id (UUID) - Primary key
- email (VARCHAR) - Unique email
- password_hash (VARCHAR) - Hashed password
- full_name (VARCHAR) - User name
- is_admin (BOOLEAN) - Admin flag
- is_teacher (BOOLEAN) - Teacher flag
- profile_picture_url (VARCHAR) - Avatar URL
- bio (TEXT) - User bio
- created_at, updated_at (TIMESTAMP)
```

### **Videos Table**
```
- id (UUID) - Primary key
- title (VARCHAR) - Video title
- description (TEXT) - Video description
- domain (VARCHAR) - Category (it, healthcare, etc.)
- source_language (VARCHAR) - Original language (en, hi, etc.)
- target_languages (TEXT[]) - Languages to translate to
- file_url (VARCHAR) - Cloudinary video URL ⭐
- cloudinary_public_id (VARCHAR) - Cloudinary ID
- duration (FLOAT) - Video duration in seconds
- thumbnail_url (VARCHAR) - Thumbnail from Cloudinary
- status (VARCHAR) - uploaded, processing, completed, failed
- uploaded_by (UUID) - Reference to users table
- created_at, updated_at (TIMESTAMP)
```

### **Transcriptions Table**
```
- id (UUID) - Primary key
- video_id (UUID) - Reference to videos
- language (VARCHAR) - Language of transcription
- full_text (TEXT) - Complete transcription text ⭐
- segments (JSONB) - Array of {start, end, text}
- duration (FLOAT) - Video duration
- status (VARCHAR) - completed, failed
- created_at, updated_at (TIMESTAMP)
```

### **Translations Table**
```
- id (UUID) - Primary key
- video_id (UUID) - Reference to videos
- language (VARCHAR) - Target language
- translated_text (TEXT) - Translated transcription ⭐
- dubbed_video_url (VARCHAR) - Cloudinary dubbed video URL
- audio_url (VARCHAR) - Cloudinary TTS audio URL
- status (VARCHAR) - pending, processing, completed, failed
- quality_score (FLOAT) - 0-100 quality rating
- created_at, updated_at (TIMESTAMP)
```

### **Other Tables**
- **subtitles**: Stores subtitle files (VTT, SRT, ASS format)
- **quiz_questions**: Quiz questions for videos
- **quiz_responses**: User answers to quiz questions
- **enrollments**: Track which users enrolled in which videos
- **reviews**: User reviews and ratings
- **glossary_terms**: Translation glossary for context
- **processing_jobs**: Track async ML processing jobs

---

## **STEP 5: Data Flow**

```
User Upload Video
    ↓
Backend validates file
    ↓
Upload to Cloudinary ⭐
    ↓
Save metadata to Supabase (videos table)
    ↓
Create processing job
    ↓
Transcribe (Whisper) → Save to Supabase (transcriptions table)
    ↓
Translate → Save to Supabase (translations table)
    ↓
Generate TTS → Upload to Cloudinary ⭐
    ↓
Save audio URL to Supabase (translations table)
    ↓
Generate subtitles → Upload to Cloudinary ⭐
    ↓
Save subtitle URL to Supabase (subtitles table)
    ↓
Done! ✅
```

---

## **STEP 6: Storage Strategy**

### **Cloudinary (Large Files)**
- ✅ Original video files
- ✅ Dubbed video files
- ✅ TTS audio files
- ✅ Subtitle files
- ✅ Thumbnails

### **Supabase (Metadata & Text)**
- ✅ Video metadata (title, duration, etc.)
- ✅ Transcription text
- ✅ Translated text
- ✅ User data
- ✅ Quiz responses
- ✅ URLs pointing to Cloudinary files

---

## **STEP 7: Test Endpoints**

### **Test Video Upload**
```bash
curl -X POST http://localhost:8000/api/v1/videos/upload \
  -F "file=@video.mp4" \
  -F "title=Test Video" \
  -F "domain=it" \
  -F "source_language=en" \
  -F "target_languages=hi,ta" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **Check Supabase**
1. Go to **Table Editor**
2. Click **videos** table
3. You should see your uploaded video with:
   - ✅ file_url (Cloudinary)
   - ✅ cloudinary_public_id
   - ✅ duration
   - ✅ status: "uploaded"

---

## **TROUBLESHOOTING**

### **"Supabase credentials not found"**
- Check `.env` file has SUPABASE_URL and SUPABASE_KEY
- Restart backend server

### **"Connection refused"**
- Check internet connection
- Verify Supabase project is active
- Check credentials are correct

### **"RLS policy violation"**
- This is normal, RLS is working
- Backend will handle authentication

### **"Table already exists"**
- This is fine, schema.sql uses `IF NOT EXISTS`
- You can run it multiple times safely

---

## **NEXT STEPS**

1. ✅ Supabase project created
2. ✅ Database schema created
3. ✅ Credentials added to .env
4. ⏭️ **Next**: Implement transcription endpoint
5. ⏭️ **Then**: Implement translation endpoint
6. ⏭️ **Then**: Connect frontend

---

## **USEFUL LINKS**

- Supabase Dashboard: https://supabase.com/dashboard
- Supabase Docs: https://supabase.com/docs
- SQL Editor: In your Supabase project → SQL Editor
- Table Editor: In your Supabase project → Table Editor

---

**Questions?** Check logs in terminal for detailed error messages!
