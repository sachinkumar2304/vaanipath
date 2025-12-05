# 🚀 Supabase + Cloudflare R2 Setup Guide

## 📚 Kya Store Karenge?

### **Supabase (PostgreSQL Database):**
- ✅ User authentication & profiles
- ✅ Video metadata (title, description, duration, etc.)
- ✅ Translation status & data
- ✅ Quiz questions & sessions
- ✅ Student enrollments
- ✅ Review system data
- ✅ Processing job status
- ✅ Glossary terms

### **Cloudflare R2 (Object Storage):**
- ✅ Original uploaded videos
- ✅ Dubbed videos (Hindi, Tamil, Telugu)
- ✅ TTS audio files
- ✅ Subtitle files (.vtt, .srt)
- ✅ Video thumbnails

---

# 🗄️ PART 1: SUPABASE SETUP (15-20 minutes)

## Step 1: Supabase Account Banao

1. **Website par jao:**
   ```
   https://supabase.com
   ```

2. **Sign up karo:**
   - Click on **"Start your project"**
   - GitHub se sign up karo (recommended)
   - Ya email se bhi kar sakte ho

3. **Email verify karo:**
   - Inbox check karo
   - Verification link pe click karo

---

## Step 2: New Project Banao

1. **Dashboard me aao:**
   - https://app.supabase.com

2. **New Project button click karo**

3. **Project details bharo:**
   ```
   Organization: (Select your org)
   Name: Gyanify
   Database Password: [STRONG PASSWORD - NOTE YE DOWN!]
   Region: Mumbai (ap-south-1) ← India ke liye best
   Pricing Plan: Free
   ```

4. **Create new project** button click karo

5. **Wait karo 2-3 minutes** (project setup ho raha hai)

---

## Step 3: Database Schema Setup

1. **SQL Editor kholo:**
   - Left sidebar me **"SQL Editor"** pe click karo
   - **"New query"** button click karo

2. **Complete Schema Paste Karo:**
   - Neeche diye gaye **COMPLETE SQL** ko copy karo
   - SQL Editor me paste karo
   - **RUN** button click karo (Ctrl+Enter)

---

## 📝 Complete Database Schema (Copy This Entire Thing):

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (Supabase auth ko extend karta hai)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'student' CHECK (role IN ('student', 'teacher', 'admin')),
    phone VARCHAR(20),
    institution VARCHAR(255),
    preferred_language VARCHAR(10) DEFAULT 'en',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Videos table (metadata only, files in R2)
CREATE TABLE videos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    uploaded_by UUID REFERENCES users(id) ON DELETE CASCADE,
    original_language VARCHAR(10) DEFAULT 'en',
    duration FLOAT,
    r2_path VARCHAR(500) NOT NULL, -- Cloudflare R2 file path
    thumbnail_url VARCHAR(500),
    subject VARCHAR(100),
    difficulty_level VARCHAR(20) CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
    tags TEXT[], -- Array of tags
    view_count INTEGER DEFAULT 0,
    is_published BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Translations table (dubbed video metadata)
CREATE TABLE translations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
    language VARCHAR(10) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    transcription_text TEXT,
    translated_text TEXT,
    dubbed_video_url VARCHAR(500), -- R2 URL
    audio_url VARCHAR(500), -- TTS audio R2 URL
    subtitle_url VARCHAR(500), -- Subtitle file R2 URL
    quality_score FLOAT,
    processing_time INTEGER, -- seconds
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(video_id, language)
);

-- Enrollments (student-video relationship)
CREATE TABLE enrollments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES users(id) ON DELETE CASCADE,
    video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
    progress FLOAT DEFAULT 0, -- percentage
    last_watched_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(student_id, video_id)
);

-- Glossary (domain-specific translation terms)
CREATE TABLE glossary (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_term VARCHAR(255) NOT NULL,
    target_term VARCHAR(255) NOT NULL,
    source_language VARCHAR(10) DEFAULT 'en',
    target_language VARCHAR(10) NOT NULL,
    domain VARCHAR(100), -- e.g., 'machine_learning', 'biology'
    context TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(source_term, target_language, domain)
);

-- Quiz Questions
CREATE TABLE quiz_questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    options JSONB NOT NULL, -- {"A": "option1", "B": "option2", ...}
    correct_answer VARCHAR(10) NOT NULL,
    explanation TEXT,
    difficulty VARCHAR(20) CHECK (difficulty IN ('easy', 'medium', 'hard')),
    points INTEGER DEFAULT 10,
    language VARCHAR(10) DEFAULT 'en',
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Quiz Sessions (student attempts)
CREATE TABLE quiz_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES users(id) ON DELETE CASCADE,
    video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
    score INTEGER DEFAULT 0,
    total_questions INTEGER NOT NULL,
    correct_answers INTEGER DEFAULT 0,
    time_taken INTEGER, -- seconds
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- User Answers
CREATE TABLE user_answers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES quiz_sessions(id) ON DELETE CASCADE,
    question_id UUID REFERENCES quiz_questions(id) ON DELETE CASCADE,
    selected_answer VARCHAR(10) NOT NULL,
    is_correct BOOLEAN NOT NULL,
    answered_at TIMESTAMP DEFAULT NOW()
);

-- Reviews (human review for translation quality)
CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    translation_id UUID REFERENCES translations(id) ON DELETE CASCADE,
    reviewer_id UUID REFERENCES users(id),
    status VARCHAR(20) CHECK (status IN ('approved', 'rejected', 'needs_revision')),
    feedback TEXT,
    corrections JSONB, -- Suggested changes
    reviewed_at TIMESTAMP DEFAULT NOW()
);

-- Processing Jobs (ML pipeline tracking)
CREATE TABLE processing_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
    target_language VARCHAR(10) NOT NULL,
    stage VARCHAR(50) DEFAULT 'transcribing',
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    progress INTEGER DEFAULT 0, -- 0-100
    enable_lip_sync BOOLEAN DEFAULT true,
    generate_quiz BOOLEAN DEFAULT false,
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Cultural Adaptations (context-aware translations)
CREATE TABLE cultural_adaptations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
    language VARCHAR(10) NOT NULL,
    original_phrase TEXT NOT NULL,
    adapted_phrase TEXT NOT NULL,
    context TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_videos_uploaded_by ON videos(uploaded_by);
CREATE INDEX idx_videos_created_at ON videos(created_at DESC);
CREATE INDEX idx_translations_video_id ON translations(video_id);
CREATE INDEX idx_translations_status ON translations(status);
CREATE INDEX idx_enrollments_student_id ON enrollments(student_id);
CREATE INDEX idx_enrollments_video_id ON enrollments(video_id);
CREATE INDEX idx_quiz_questions_video_id ON quiz_questions(video_id);
CREATE INDEX idx_quiz_sessions_student_id ON quiz_sessions(student_id);
CREATE INDEX idx_processing_jobs_video_id ON processing_jobs(video_id);
CREATE INDEX idx_processing_jobs_status ON processing_jobs(status);

-- Updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_videos_updated_at BEFORE UPDATE ON videos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_translations_updated_at BEFORE UPDATE ON translations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert demo admin user (password will be hashed in backend)
INSERT INTO users (email, full_name, role, is_active) VALUES 
('admin@gyanify.com', 'Admin User', 'admin', true),
('teacher@gyanify.com', 'Demo Teacher', 'teacher', true),
('student@gyanify.com', 'Demo Student', 'student', true);
```

---

## Step 4: API Keys Copy Karo

1. **Settings pe jao:**
   - Left sidebar me **"Settings"** click karo
   - **"API"** section select karo

2. **Copy karo ye 3 cheezein:**
   ```
   Project URL: https://xxxxx.supabase.co
   anon public key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   service_role key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... (secret!)
   ```

3. **IMPORTANT:** 
   - `service_role` key ko **SECRET** rakho
   - Yeh key full database access deti hai

---

## Step 5: Backend .env File Update Karo

1. **File kholo:**
   ```
   D:\backend\.env
   ```

2. **Supabase credentials add karo:**
   ```env
   # Supabase Configuration
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # anon key
   SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # service_role key

   # JWT Settings
   SECRET_KEY=your-super-secret-key-change-this-in-production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

3. **Save karo** (Ctrl+S)

---

## Step 6: Test Karo Database Connection

1. **Backend server restart karo:**
   ```powershell
   cd D:\backend
   uvicorn app.main:app --reload
   ```

2. **Browser me jao:**
   ```
   http://localhost:8000/docs
   ```

3. **Test signup endpoint:**
   - `/api/v1/auth/signup` expand karo
   - **Try it out** click karo
   - Body me dalo:
   ```json
   {
     "email": "test@example.com",
     "password": "Test@1234",
     "full_name": "Test User",
     "role": "student"
   }
   ```
   - **Execute** click karo
   - Response me `200 OK` aana chahiye

4. **Supabase me verify karo:**
   - Supabase dashboard → **Table Editor**
   - **users** table select karo
   - Tumhara test user dikh jayega!

---

# ☁️ PART 2: CLOUDFLARE R2 SETUP (15-20 minutes)

## Step 1: Cloudflare Account Banao

1. **Website pe jao:**
   ```
   https://dash.cloudflare.com/sign-up
   ```

2. **Sign up karo:**
   - Email aur password se
   - Email verify karo

3. **Dashboard me login karo:**
   ```
   https://dash.cloudflare.com
   ```

---

## Step 2: R2 Enable Karo

1. **Left sidebar me:**
   - **"R2"** option dhundo
   - Click karo

2. **Enable R2:**
   - **"Purchase R2"** button click karo
   - Free plan select karo (10GB free)
   - Payment method add karo (credit card - free plan ke liye bhi zaruri)
   - **Confirm** karo

3. **R2 dashboard khul jayega**

---

## Step 3: Bucket Banao

1. **Create bucket button click karo**

2. **Bucket configuration:**
   ```
   Bucket name: gyanify-videos
   Location: APAC (Asia-Pacific) ← India ke paas
   Storage class: Standard
   ```

3. **Create bucket** click karo

4. **Bucket ban gaya!** ✅

---

## Step 4: API Token Generate Karo

1. **R2 dashboard me:**
   - **"Manage R2 API Tokens"** button click karo

2. **Create API token:**
   - **"Create API token"** click karo

3. **Token configuration:**
   ```
   Token name: gyanify-backend
   Permissions: 
     ✅ Object Read & Write
   TTL: Forever (ya 1 year)
   Buckets: 
     ✅ Apply to specific buckets only
     Select: gyanify-videos
   ```

4. **Create API token** button click karo

5. **IMPORTANT - Copy these NOW (won't show again!):**
   ```
   Access Key ID: xxxxxxxxxxxxxxxxxxxxx
   Secret Access Key: yyyyyyyyyyyyyyyyyyyyyyyyyyyy
   ```

6. **Download karo ya note down karo** (ek baar hi dikhega!)

---

## Step 5: Account ID Copy Karo

1. **R2 dashboard pe:**
   - Right side me **"Account ID"** dikhega
   - Copy karo: `1234567890abcdef`

---

## Step 6: Backend .env Update Karo

1. **File kholo:**
   ```
   D:\backend\.env
   ```

2. **R2 credentials add karo:**
   ```env
   # Cloudflare R2 Configuration
   R2_ACCOUNT_ID=1234567890abcdef
   R2_ACCESS_KEY_ID=xxxxxxxxxxxxxxxxxxxxx
   R2_SECRET_ACCESS_KEY=yyyyyyyyyyyyyyyyyyyyyyyyyyyy
   R2_BUCKET_NAME=gyanify-videos
   R2_PUBLIC_URL=https://pub-xxxxx.r2.dev  # Optional - custom domain
   ```

3. **Save karo** (Ctrl+S)

---

## Step 7: Test R2 Upload

1. **Backend server restart karo:**
   ```powershell
   cd D:\backend
   uvicorn app.main:app --reload
   ```

2. **Swagger UI me jao:**
   ```
   http://localhost:8000/docs
   ```

3. **Login karo pehle:**
   - `/api/v1/auth/login` endpoint use karo
   - Token copy karo

4. **Authorize karo:**
   - Swagger UI top-right me **"Authorize"** button
   - Token paste karo: `Bearer your-token-here`
   - **Authorize** click karo

5. **Test video upload:**
   - `/api/v1/videos/upload` endpoint expand karo
   - **Try it out** click karo
   - File select karo (koi bhi small video - 10MB max for test)
   - Title/description bharo
   - **Execute** click karo

6. **R2 me verify karo:**
   - Cloudflare R2 dashboard → **gyanify-videos** bucket
   - **uploads/** folder me file dikhni chahiye

---

# 📁 R2 Folder Structure

Tumhare bucket me yeh structure banega:

```
gyanify-videos/
├── uploads/
│   └── {video_id}_original.mp4
├── dubbed/
│   ├── {video_id}_hi.mp4
│   ├── {video_id}_ta.mp4
│   └── {video_id}_te.mp4
├── audio/
│   ├── {video_id}_hi.mp3
│   ├── {video_id}_ta.mp3
│   └── {video_id}_te.mp3
├── subtitles/
│   ├── {video_id}_hi.vtt
│   ├── {video_id}_ta.vtt
│   └── {video_id}_te.vtt
└── thumbnails/
    └── {video_id}_thumb.jpg
```

---

# ✅ Final Checklist

## Supabase:
- [ ] Account banaya
- [ ] Project "Gyanify" banaya
- [ ] SQL schema run kiya (11 tables)
- [ ] API keys copy kiye
- [ ] .env me credentials add kiye
- [ ] Signup endpoint test kiya
- [ ] Supabase Table Editor me data verify kiya

## Cloudflare R2:
- [ ] Account banaya
- [ ] R2 enabled (payment method added)
- [ ] Bucket "gyanify-videos" banaya
- [ ] API token generate kiya
- [ ] Account ID copy kiya
- [ ] .env me credentials add kiye
- [ ] Video upload test kiya
- [ ] R2 bucket me file verify kiya

---

# 🔥 Complete .env File Template

```env
# Application Settings
APP_NAME=Gyanify
DEBUG=True
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Supabase Configuration
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.yyyyy

# JWT Settings
SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Cloudflare R2 Configuration
R2_ACCOUNT_ID=1234567890abcdef
R2_ACCESS_KEY_ID=xxxxxxxxxxxxxxxxxxxxx
R2_SECRET_ACCESS_KEY=yyyyyyyyyyyyyyyyyyyyyyyyyyyy
R2_BUCKET_NAME=gyanify-videos

# Redis Configuration (Optional - for now)
REDIS_URL=redis://localhost:6379

# Celery Configuration (Optional - for now)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

---

# 🚨 Common Issues & Solutions

## Issue 1: Supabase connection failed
**Error:** `could not connect to server`
**Solution:** 
- Check SUPABASE_URL correct hai
- Internet connection check karo
- Firewall/antivirus check karo

## Issue 2: R2 upload failed
**Error:** `SignatureDoesNotMatch`
**Solution:**
- Access keys sahi copy kiye?
- Account ID sahi hai?
- Bucket name exact match karta hai?

## Issue 3: SQL schema error
**Error:** `relation already exists`
**Solution:**
- Tables already ban gaye hain
- DROP TABLE commands run karo pehle
- Ya naya project banao

---

# 🎉 Next Steps

1. ✅ Database setup done
2. ✅ Storage setup done
3. 🔄 Frontend integration (API calls)
4. 🔄 ML model integration (Whisper, IndicTrans2, TTS)
5. 🔄 Testing end-to-end

**Koi problem aaye toh batao!** 💪
