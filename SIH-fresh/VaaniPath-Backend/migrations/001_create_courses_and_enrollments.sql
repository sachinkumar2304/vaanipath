-- Migration: Create courses and enrollments tables
-- Run this in Supabase SQL Editor

-- 1. Create courses table
CREATE TABLE IF NOT EXISTS courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    description TEXT,
    thumbnail_url TEXT,
    teacher_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    domain TEXT NOT NULL,
    source_language TEXT NOT NULL DEFAULT 'en',
    target_languages JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- 2. Create enrollments table
CREATE TABLE IF NOT EXISTS enrollments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    enrolled_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    progress JSONB DEFAULT '{}'::jsonb,
    UNIQUE(student_id, course_id)
);

-- 3. Add course_id to videos table (nullable for backward compatibility)
ALTER TABLE videos 
ADD COLUMN IF NOT EXISTS course_id UUID REFERENCES courses(id) ON DELETE CASCADE;

-- 4. Add order column to videos table
ALTER TABLE videos 
ADD COLUMN IF NOT EXISTS "order" INTEGER DEFAULT 0;

-- 5. Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_courses_teacher_id ON courses(teacher_id);
CREATE INDEX IF NOT EXISTS idx_courses_domain ON courses(domain);
CREATE INDEX IF NOT EXISTS idx_enrollments_student_id ON enrollments(student_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_course_id ON enrollments(course_id);
CREATE INDEX IF NOT EXISTS idx_videos_course_id ON videos(course_id);

-- 6. Add updated_at trigger for courses
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_courses_updated_at BEFORE UPDATE ON courses
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 7. Row Level Security (RLS)
-- Temporarily disable RLS for development - will add proper policies later
-- ALTER TABLE courses ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE enrollments ENABLE ROW LEVEL SECURITY;

-- Note: RLS is disabled for now. To enable later, uncomment above lines
-- and add policies as per your security requirements

-- 8. Grant necessary permissions
GRANT ALL ON courses TO authenticated;
GRANT ALL ON enrollments TO authenticated;

COMMENT ON TABLE courses IS 'Stores course information created by teachers';
COMMENT ON TABLE enrollments IS 'Stores student course enrollments and progress tracking';
COMMENT ON COLUMN videos.course_id IS 'Links video to a course (nullable for backward compatibility)';
COMMENT ON COLUMN videos."order" IS 'Display order of videos within a course';
