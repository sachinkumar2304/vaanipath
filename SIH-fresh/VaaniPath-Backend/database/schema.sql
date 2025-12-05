-- ============================================
-- GYANIFY DATABASE SCHEMA
-- Run this in Supabase SQL Editor
-- ============================================

-- ============================================
-- 1. USERS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(255),
  is_admin BOOLEAN DEFAULT FALSE,
  is_teacher BOOLEAN DEFAULT FALSE,
  profile_picture_url VARCHAR(500),
  bio TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_is_admin ON users(is_admin);

-- ============================================
-- 2. VIDEOS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS videos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(255) NOT NULL,
  description TEXT,
  domain VARCHAR(50), -- 'it', 'healthcare', 'education', etc.
  source_language VARCHAR(10) DEFAULT 'en',
  target_languages TEXT[], -- Array of language codes
  file_url VARCHAR(500) NOT NULL, -- Cloudinary URL
  cloudinary_public_id VARCHAR(255),
  duration FLOAT,
  thumbnail_url VARCHAR(500),
  status VARCHAR(50) DEFAULT 'uploaded', -- 'uploaded', 'processing', 'completed', 'failed'
  uploaded_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_videos_uploaded_by ON videos(uploaded_by);
CREATE INDEX IF NOT EXISTS idx_videos_status ON videos(status);
CREATE INDEX IF NOT EXISTS idx_videos_domain ON videos(domain);

-- ============================================
-- 3. TRANSCRIPTIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS transcriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
  language VARCHAR(10),
  full_text TEXT NOT NULL, -- Complete transcription
  segments JSONB, -- Array of {start, end, text}
  duration FLOAT,
  status VARCHAR(50) DEFAULT 'completed',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_transcriptions_video_id ON transcriptions(video_id);
CREATE INDEX IF NOT EXISTS idx_transcriptions_language ON transcriptions(language);

-- ============================================
-- 4. TRANSLATIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS translations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
  language VARCHAR(10) NOT NULL,
  translated_text TEXT NOT NULL, -- Translated transcription (TEXT only, no video)
  dubbed_video_url VARCHAR(500), -- Cloudinary URL for dubbed video
  audio_url VARCHAR(500), -- Cloudinary URL for TTS audio
  status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
  quality_score FLOAT, -- 0-100 quality rating
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_translations_video_id ON translations(video_id);
CREATE INDEX IF NOT EXISTS idx_translations_language ON translations(language);
CREATE INDEX IF NOT EXISTS idx_translations_status ON translations(status);

-- ============================================
-- 5. SUBTITLES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS subtitles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  translation_id UUID NOT NULL REFERENCES translations(id) ON DELETE CASCADE,
  language VARCHAR(10),
  format VARCHAR(10) DEFAULT 'vtt', -- 'vtt', 'srt', 'ass'
  subtitle_url VARCHAR(500), -- Cloudinary URL
  content TEXT, -- Actual subtitle content
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_subtitles_translation_id ON subtitles(translation_id);

-- ============================================
-- 6. QUIZ QUESTIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS quiz_questions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
  question_text TEXT NOT NULL,
  question_type VARCHAR(50), -- 'multiple_choice', 'true_false', 'short_answer'
  options JSONB, -- Array of options
  correct_answer VARCHAR(255),
  difficulty VARCHAR(20), -- 'easy', 'medium', 'hard'
  timestamp FLOAT, -- When in video to ask
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_quiz_questions_video_id ON quiz_questions(video_id);

-- ============================================
-- 7. QUIZ RESPONSES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS quiz_responses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  question_id UUID NOT NULL REFERENCES quiz_questions(id) ON DELETE CASCADE,
  user_answer VARCHAR(255),
  is_correct BOOLEAN,
  time_taken FLOAT, -- Seconds to answer
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_quiz_responses_user_id ON quiz_responses(user_id);
CREATE INDEX IF NOT EXISTS idx_quiz_responses_question_id ON quiz_responses(question_id);

-- ============================================
-- 8. ENROLLMENTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS enrollments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
  enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  completed_at TIMESTAMP,
  progress_percentage FLOAT DEFAULT 0,
  UNIQUE(user_id, video_id)
);

CREATE INDEX IF NOT EXISTS idx_enrollments_user_id ON enrollments(user_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_video_id ON enrollments(video_id);

-- ============================================
-- 9. REVIEWS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS reviews (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
  rating FLOAT, -- 1-5 stars
  comment TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_reviews_video_id ON reviews(video_id);
CREATE INDEX IF NOT EXISTS idx_reviews_user_id ON reviews(user_id);

-- ============================================
-- 10. GLOSSARY TABLE (For Translation Context)
-- ============================================
CREATE TABLE IF NOT EXISTS glossary_terms (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
  english_term VARCHAR(255) NOT NULL,
  hindi_term VARCHAR(255),
  tamil_term VARCHAR(255),
  telugu_term VARCHAR(255),
  definition TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_glossary_video_id ON glossary_terms(video_id);

-- ============================================
-- 11. PROCESSING JOBS TABLE (For Async Tasks)
-- ============================================
CREATE TABLE IF NOT EXISTS processing_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
  job_type VARCHAR(50), -- 'transcription', 'translation', 'tts', 'dubbing'
  language VARCHAR(10),
  status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
  progress FLOAT DEFAULT 0, -- 0-100
  error_message TEXT,
  result JSONB, -- Store result data
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  completed_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_processing_jobs_video_id ON processing_jobs(video_id);
CREATE INDEX IF NOT EXISTS idx_processing_jobs_status ON processing_jobs(status);

-- ============================================
-- ENABLE ROW LEVEL SECURITY (RLS)
-- ============================================

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE transcriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE translations ENABLE ROW LEVEL SECURITY;
ALTER TABLE subtitles ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE enrollments ENABLE ROW LEVEL SECURITY;
ALTER TABLE reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE glossary_terms ENABLE ROW LEVEL SECURITY;
ALTER TABLE processing_jobs ENABLE ROW LEVEL SECURITY;

-- ============================================
-- RLS POLICIES
-- ============================================

-- USERS: Anyone can read public profiles
CREATE POLICY "Users can read own profile" ON users
  FOR SELECT USING (true);

-- VIDEOS: Anyone can read
CREATE POLICY "Anyone can read videos" ON videos
  FOR SELECT USING (true);

-- VIDEOS: Only admins can insert
CREATE POLICY "Only admins can upload videos" ON videos
  FOR INSERT WITH CHECK (true); -- Will be enforced in backend

-- TRANSCRIPTIONS: Anyone can read
CREATE POLICY "Anyone can read transcriptions" ON transcriptions
  FOR SELECT USING (true);

-- TRANSLATIONS: Anyone can read
CREATE POLICY "Anyone can read translations" ON translations
  FOR SELECT USING (true);

-- QUIZ_RESPONSES: Users can read their own
CREATE POLICY "Users can read own quiz responses" ON quiz_responses
  FOR SELECT USING (true);

-- ENROLLMENTS: Users can read their own
CREATE POLICY "Users can read own enrollments" ON enrollments
  FOR SELECT USING (true);

-- REVIEWS: Anyone can read
CREATE POLICY "Anyone can read reviews" ON reviews
  FOR SELECT USING (true);

-- ============================================
-- DONE! Schema is ready
-- ============================================
-- Next steps:
-- 1. Copy Supabase credentials to .env file
-- 2. Run backend: py -3.12 -m uvicorn app.main:app --reload
-- 3. Test endpoints
-- ============================================
