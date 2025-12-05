-- =====================================================
-- Quiz and Doubts Feature Database Setup
-- Run this SQL in Supabase SQL Editor
-- =====================================================

-- 1. Create doubts table
CREATE TABLE IF NOT EXISTS public.doubts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    video_id UUID NOT NULL REFERENCES public.videos(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    lecture_number INTEGER DEFAULT 1,
    subject VARCHAR(255) DEFAULT 'General',
    answer TEXT,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'answered')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    answered_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT doubts_user_fk FOREIGN KEY (user_id) REFERENCES public.users(id),
    CONSTRAINT doubts_video_fk FOREIGN KEY (video_id) REFERENCES public.videos(id)
);

-- 2. Create quiz_questions table (if not exists)
CREATE TABLE IF NOT EXISTS public.quiz_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID NOT NULL REFERENCES public.videos(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) DEFAULT 'multiple_choice',
    options TEXT[] NOT NULL,
    correct_answer TEXT NOT NULL,
    difficulty VARCHAR(50) DEFAULT 'medium',
    points INTEGER DEFAULT 10,
    timestamp FLOAT,
    explanation TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT quiz_questions_video_fk FOREIGN KEY (video_id) REFERENCES public.videos(id)
);

-- 3. Create quiz_sessions table (if not exists)
CREATE TABLE IF NOT EXISTS public.quiz_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    video_id UUID NOT NULL REFERENCES public.videos(id) ON DELETE CASCADE,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    total_questions INTEGER NOT NULL,
    correct_answers INTEGER DEFAULT 0,
    score INTEGER DEFAULT 0,
    CONSTRAINT quiz_sessions_user_fk FOREIGN KEY (user_id) REFERENCES public.users(id),
    CONSTRAINT quiz_sessions_video_fk FOREIGN KEY (video_id) REFERENCES public.videos(id)
);

-- 4. Create user_answers table (if not exists)
CREATE TABLE IF NOT EXISTS public.user_answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES public.quiz_sessions(id) ON DELETE CASCADE,
    question_id UUID NOT NULL REFERENCES public.quiz_questions(id) ON DELETE CASCADE,
    user_answer TEXT NOT NULL,
    is_correct BOOLEAN DEFAULT FALSE,
    answered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT user_answers_session_fk FOREIGN KEY (session_id) REFERENCES public.quiz_sessions(id),
    CONSTRAINT user_answers_question_fk FOREIGN KEY (question_id) REFERENCES public.quiz_questions(id)
);

-- 5. Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_doubts_user_id ON public.doubts(user_id);
CREATE INDEX IF NOT EXISTS idx_doubts_video_id ON public.doubts(video_id);
CREATE INDEX IF NOT EXISTS idx_doubts_status ON public.doubts(status);
CREATE INDEX IF NOT EXISTS idx_quiz_questions_video_id ON public.quiz_questions(video_id);
CREATE INDEX IF NOT EXISTS idx_quiz_sessions_user_id ON public.quiz_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_quiz_sessions_video_id ON public.quiz_sessions(video_id);
CREATE INDEX IF NOT EXISTS idx_user_answers_session_id ON public.user_answers(session_id);

-- 6. Enable Row Level Security (RLS)
ALTER TABLE public.doubts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quiz_questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quiz_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_answers ENABLE ROW LEVEL SECURITY;

-- 7. RLS Policies for doubts
-- Students can create and view their own doubts
CREATE POLICY "Users can create their own doubts"
    ON public.doubts FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view their own doubts"
    ON public.doubts FOR SELECT
    USING (auth.uid() = user_id);

-- Teachers can view and update doubts for their videos
CREATE POLICY "Teachers can view doubts for their videos"
    ON public.doubts FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.videos v
            WHERE v.id = doubts.video_id
            AND v.uploaded_by = auth.uid()
        )
    );

CREATE POLICY "Teachers can update doubts for their videos"
    ON public.doubts FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.videos v
            WHERE v.id = doubts.video_id
            AND v.uploaded_by = auth.uid()
        )
    );

-- 8. RLS Policies for quiz_questions
-- Teachers can manage questions for their videos
CREATE POLICY "Teachers can manage quiz questions for their videos"
    ON public.quiz_questions FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.videos v
            WHERE v.id = quiz_questions.video_id
            AND v.uploaded_by = auth.uid()
        )
    );

-- Students can view quiz questions
CREATE POLICY "Users can view quiz questions"
    ON public.quiz_questions FOR SELECT
    USING (true);

-- 9. RLS Policies for quiz_sessions
-- Users can manage their own quiz sessions
CREATE POLICY "Users can manage their own quiz sessions"
    ON public.quiz_sessions FOR ALL
    USING (auth.uid() = user_id);

-- 10. RLS Policies for user_answers
-- Users can manage their own answers
CREATE POLICY "Users can manage their own answers"
    ON public.user_answers FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.quiz_sessions qs
            WHERE qs.id = user_answers.session_id
            AND qs.user_id = auth.uid()
        )
    );

-- =====================================================
-- Verification Queries (Run these to check)
-- =====================================================

-- Check if tables were created
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('doubts', 'quiz_questions', 'quiz_sessions', 'user_answers');

-- Check RLS is enabled
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('doubts', 'quiz_questions', 'quiz_sessions', 'user_answers');
