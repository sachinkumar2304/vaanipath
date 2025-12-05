-- Supabase Database Schema for Gyanify Localization Engine

-- =================================
-- Users Table
-- =================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);

-- =================================
-- Videos Table
-- =================================
CREATE TABLE IF NOT EXISTS videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    domain VARCHAR(100) NOT NULL,
    source_language VARCHAR(10) DEFAULT 'en',
    target_languages TEXT[], -- Array of language codes
    status VARCHAR(50) DEFAULT 'uploaded',
    uploaded_by UUID REFERENCES users(id),
    file_url TEXT NOT NULL,
    duration FLOAT, -- Duration in seconds
    thumbnail_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_videos_status ON videos(status);
CREATE INDEX idx_videos_domain ON videos(domain);
CREATE INDEX idx_videos_uploaded_by ON videos(uploaded_by);

-- =================================
-- Translations Table
-- =================================
CREATE TABLE IF NOT EXISTS translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
    language VARCHAR(10) NOT NULL,
    status VARCHAR(50) DEFAULT 'processing',
    transcript_url TEXT,
    translated_text_url TEXT,
    audio_url TEXT,
    subtitle_url TEXT,
    video_url TEXT,
    quality_score FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(video_id, language)
);

CREATE INDEX idx_translations_video_id ON translations(video_id);
CREATE INDEX idx_translations_language ON translations(language);
CREATE INDEX idx_translations_status ON translations(status);

-- =================================
-- Enrollments Table (Student Course Enrollment)
-- =================================
CREATE TABLE IF NOT EXISTS enrollments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
    enrolled_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    progress INTEGER DEFAULT 0, -- Percentage (0-100)
    last_watched_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(user_id, video_id)
);

CREATE INDEX idx_enrollments_user_id ON enrollments(user_id);
CREATE INDEX idx_enrollments_video_id ON enrollments(video_id);

-- =================================
-- Glossary Table
-- =================================
CREATE TABLE IF NOT EXISTS glossary (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    term VARCHAR(255) NOT NULL,
    domain VARCHAR(100) NOT NULL,
    translations JSONB NOT NULL, -- {"hi": "term", "ta": "term"}
    context TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_glossary_domain ON glossary(domain);
CREATE INDEX idx_glossary_term ON glossary(term);

-- =================================
-- Quiz Questions Table
-- =================================
CREATE TABLE IF NOT EXISTS quiz_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL,
    options JSONB, -- Array of options for MCQ
    correct_answer TEXT NOT NULL,
    difficulty VARCHAR(20) DEFAULT 'medium',
    timestamp FLOAT, -- Video timestamp reference
    explanation TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_quiz_questions_video_id ON quiz_questions(video_id);

-- =================================
-- Quiz Sessions Table
-- =================================
CREATE TABLE IF NOT EXISTS quiz_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    score INTEGER,
    total_questions INTEGER,
    correct_answers INTEGER
);

CREATE INDEX idx_quiz_sessions_user_id ON quiz_sessions(user_id);
CREATE INDEX idx_quiz_sessions_video_id ON quiz_sessions(video_id);

-- =================================
-- User Answers Table
-- =================================
CREATE TABLE IF NOT EXISTS user_answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES quiz_sessions(id) ON DELETE CASCADE,
    question_id UUID REFERENCES quiz_questions(id) ON DELETE CASCADE,
    user_answer TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    answered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_user_answers_session_id ON user_answers(session_id);

-- =================================
-- Reviews Table
-- =================================
CREATE TABLE IF NOT EXISTS reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    translation_id UUID REFERENCES translations(id) ON DELETE CASCADE,
    reviewer_id UUID REFERENCES users(id),
    approved BOOLEAN NOT NULL,
    feedback TEXT,
    corrections JSONB,
    reviewed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_reviews_translation_id ON reviews(translation_id);
CREATE INDEX idx_reviews_reviewer_id ON reviews(reviewer_id);

-- =================================
-- Processing Jobs Table
-- =================================
CREATE TABLE IF NOT EXISTS processing_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
    job_type VARCHAR(50) NOT NULL, -- 'asr', 'translation', 'tts', 'lip_sync'
    status VARCHAR(50) DEFAULT 'queued',
    progress INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_processing_jobs_video_id ON processing_jobs(video_id);
CREATE INDEX idx_processing_jobs_status ON processing_jobs(status);

-- =================================
-- Cultural Adaptations Table
-- =================================
CREATE TABLE IF NOT EXISTS cultural_adaptations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_text TEXT NOT NULL,
    target_language VARCHAR(10) NOT NULL,
    adapted_text TEXT NOT NULL,
    adaptation_type VARCHAR(50), -- 'example', 'idiom', 'regional_reference'
    confidence FLOAT,
    domain VARCHAR(100),
    approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_cultural_adaptations_language ON cultural_adaptations(target_language);
CREATE INDEX idx_cultural_adaptations_domain ON cultural_adaptations(domain);

-- =================================
-- Update Triggers
-- =================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_videos_updated_at BEFORE UPDATE ON videos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_translations_updated_at BEFORE UPDATE ON translations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_glossary_updated_at BEFORE UPDATE ON glossary
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
