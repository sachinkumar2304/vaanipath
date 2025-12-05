# ✅ GYANIFY SETUP CHECKLIST

## **PHASE 1: SUPABASE SETUP** (30 minutes)

### Step 1: Create Supabase Project
- [ ] Go to https://supabase.com
- [ ] Sign up / Login
- [ ] Create new project named "gyanify"
- [ ] Select region: Asia Pacific (Singapore)
- [ ] Wait for project to be ready (5-10 min)

### Step 2: Get Credentials
- [ ] Go to Settings → API
- [ ] Copy Project URL → `SUPABASE_URL`
- [ ] Copy anon public key → `SUPABASE_KEY`
- [ ] Copy service_role key → `SUPABASE_SERVICE_KEY`

### Step 3: Update .env File
```bash
# Open d:\backend\.env and add:
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
- [ ] SUPABASE_URL added
- [ ] SUPABASE_KEY added
- [ ] SUPABASE_SERVICE_KEY added

### Step 4: Create Database Schema
- [ ] Open Supabase → SQL Editor
- [ ] Create new query
- [ ] Copy entire content from `d:\backend\database\schema.sql`
- [ ] Paste in SQL Editor
- [ ] Click **Run** button
- [ ] Wait for execution (should see ✅ success)

### Step 5: Verify Tables Created
- [ ] Go to Supabase → Table Editor
- [ ] Check all 11 tables exist:
  - [ ] users
  - [ ] videos
  - [ ] transcriptions
  - [ ] translations
  - [ ] subtitles
  - [ ] quiz_questions
  - [ ] quiz_responses
  - [ ] enrollments
  - [ ] reviews
  - [ ] glossary_terms
  - [ ] processing_jobs

---

## **PHASE 2: BACKEND SETUP** (15 minutes)

### Step 6: Verify Backend Running
- [ ] Terminal: `py -3.12 -m uvicorn app.main:app --reload`
- [ ] Check logs for: `✅ Supabase client initialized successfully`
- [ ] If error, check `.env` file credentials

### Step 7: Test Endpoints
- [ ] Open Postman or browser
- [ ] Go to: http://localhost:8000/docs
- [ ] You should see Swagger UI with all endpoints

### Step 8: Test Video Upload
- [ ] Use Swagger UI or Postman
- [ ] POST `/api/v1/videos/upload`
- [ ] Upload a test video file
- [ ] Should get response with:
  - [ ] `file_url` (Cloudinary)
  - [ ] `duration` (from Cloudinary)
  - [ ] `status: "uploaded"`

### Step 9: Verify in Supabase
- [ ] Go to Supabase → Table Editor
- [ ] Click **videos** table
- [ ] You should see your uploaded video with:
  - [ ] file_url (Cloudinary URL)
  - [ ] cloudinary_public_id
  - [ ] duration
  - [ ] status: "uploaded"
  - [ ] created_at timestamp

---

## **PHASE 3: CLOUDINARY VERIFICATION** (5 minutes)

### Step 10: Check Cloudinary
- [ ] Go to https://cloudinary.com/console
- [ ] Click **Media Library**
- [ ] Navigate to **gyanify/videos** folder
- [ ] You should see uploaded video file
- [ ] Click to verify it plays

---

## **PHASE 4: ARCHITECTURE VERIFICATION** (10 minutes)

### Step 11: Verify Data Flow
```
✅ Video Upload
   ↓
✅ Cloudinary Storage (file_url)
   ↓
✅ Supabase Metadata (videos table)
   ↓
⏭️ Next: Transcription (Whisper)
```

### Step 12: Check Current Status
- [ ] Backend: ✅ Running
- [ ] Cloudinary: ✅ Storing videos
- [ ] Supabase: ✅ Storing metadata
- [ ] Database: ✅ Schema created
- [ ] Tables: ✅ All 11 tables ready

---

## **PHASE 5: NEXT STEPS** (After this checklist)

### Immediate Next (This Week)
1. [ ] Implement transcription endpoint (Whisper)
2. [ ] Implement translation endpoint (IndianLLM)
3. [ ] Implement TTS endpoint (Text-to-Speech)
4. [ ] Setup Celery task queue

### Short Term (Next Week)
1. [ ] Connect frontend to API
2. [ ] Add progress tracking
3. [ ] Implement quiz system
4. [ ] Add user authentication

### Medium Term (2-3 Weeks)
1. [ ] Add ML model integration
2. [ ] Implement batch processing
3. [ ] Add error handling & logging
4. [ ] Create comprehensive tests

---

## **TROUBLESHOOTING**

### Problem: "Supabase credentials not found"
**Solution:**
1. Check `.env` file has all 3 credentials
2. Restart backend server
3. Check credentials are copied correctly (no extra spaces)

### Problem: "Connection refused"
**Solution:**
1. Check internet connection
2. Verify Supabase project is active
3. Try accessing Supabase dashboard directly

### Problem: "Table already exists"
**Solution:**
- This is normal! Schema.sql uses `IF NOT EXISTS`
- You can run it multiple times safely

### Problem: Video not appearing in Supabase
**Solution:**
1. Check backend logs for errors
2. Verify Cloudinary upload succeeded (check response)
3. Check Supabase credentials in `.env`
4. Try uploading again

### Problem: "RLS policy violation"
**Solution:**
- This is expected, RLS is working
- Backend handles authentication
- No action needed

---

## **QUICK COMMANDS**

### Start Backend
```bash
cd d:\backend
py -3.12 -m uvicorn app.main:app --reload
```

### Check Logs
```bash
# Terminal will show logs automatically
# Look for ✅ or ❌ messages
```

### Test API
```bash
# Browser
http://localhost:8000/docs

# Postman
POST http://localhost:8000/api/v1/videos/upload
```

### Access Supabase
```
https://supabase.com/dashboard
→ Select "gyanify" project
→ Table Editor / SQL Editor
```

---

## **FINAL CHECKLIST**

- [ ] Supabase project created
- [ ] Credentials in `.env`
- [ ] Database schema created
- [ ] All 11 tables exist
- [ ] Backend running
- [ ] Video upload working
- [ ] Cloudinary storing files
- [ ] Supabase storing metadata
- [ ] No errors in logs
- [ ] Ready for next phase ✅

---

**Status**: Ready to proceed with ML integration!

**Next**: Implement transcription endpoint with Whisper model
