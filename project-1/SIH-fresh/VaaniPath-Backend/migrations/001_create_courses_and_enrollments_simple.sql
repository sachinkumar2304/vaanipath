-- Simple Migration: Create courses and enrollments tables
-- Run this in Supabase SQL Editor

-- 1. Create courses table (simple version)
CREATE TABLE IF NOT EXISTS courses (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    thumbnail_url TEXT,
    teacher_id TEXT NOT NULL,
    domain TEXT NOT NULL,
    source_language TEXT NOT NULL DEFAULT 'en',
    target_languages TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- 2. Create enrollments table (simple version)
CREATE TABLE IF NOT EXISTS enrollments (
    id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL,
    course_id TEXT NOT NULL,
    enrolled_at TIMESTAMP NOT NULL DEFAULT NOW(),
    progress TEXT DEFAULT '{}'
);

-- 3. Add course_id to videos table if column doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='videos' AND column_name='course_id') THEN
        ALTER TABLE videos ADD COLUMN course_id TEXT;
    END IF;
END $$;

-- 4. Add order column to videos table if it doesn't exist  
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='videos' AND column_name='order') THEN
        ALTER TABLE videos ADD COLUMN "order" INTEGER DEFAULT 0;
    END IF;
END $$;

-- 5. Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_courses_teacher_id ON courses(teacher_id);
CREATE INDEX IF NOT EXISTS idx_courses_domain ON courses(domain);
CREATE INDEX IF NOT EXISTS idx_enrollments_student_id ON enrollments(student_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_course_id ON enrollments(course_id);
CREATE INDEX IF NOT EXISTS idx_videos_course_id ON videos(course_id);

-- 6. Create unique constraint for enrollment
CREATE UNIQUE INDEX IF NOT EXISTS idx_enrollments_unique ON enrollments(student_id, course_id);
