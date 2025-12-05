-- Clean Migration: Drop and recreate courses and enrollments tables
-- Run this in Supabase SQL Editor

-- Step 1: Drop existing policies (if any)
DROP POLICY IF EXISTS "Anyone can view courses" ON courses;
DROP POLICY IF EXISTS "Teachers can create courses" ON courses;
DROP POLICY IF EXISTS "Teachers can update their own courses" ON courses;
DROP POLICY IF EXISTS "Teachers can delete their own courses" ON courses;
DROP POLICY IF EXISTS "Students can view their own enrollments" ON enrollments;
DROP POLICY IF EXISTS "Students can enroll in courses" ON enrollments;
DROP POLICY IF EXISTS "Students can update their own progress" ON enrollments;
DROP POLICY IF EXISTS "Students can delete their own enrollments" ON enrollments;

-- Step 2: Drop existing tables (if any) - CASCADE will remove foreign keys
DROP TABLE IF EXISTS enrollments CASCADE;
DROP TABLE IF EXISTS courses CASCADE;

-- Step 3: Remove course_id column from videos if it exists (will re-add later)
ALTER TABLE videos DROP COLUMN IF EXISTS course_id CASCADE;
ALTER TABLE videos DROP COLUMN IF EXISTS "order" CASCADE;

-- Step 4: Create courses table from scratch
CREATE TABLE courses (
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

-- Step 5: Create enrollments table from scratch
CREATE TABLE enrollments (
    id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL,
    course_id TEXT NOT NULL,
    enrolled_at TIMESTAMP NOT NULL DEFAULT NOW(),
    progress TEXT DEFAULT '{}'
);

-- Step 6: Add course_id to videos table
ALTER TABLE videos ADD COLUMN course_id TEXT;
ALTER TABLE videos ADD COLUMN "order" INTEGER DEFAULT 0;

-- Step 7: Create indexes
CREATE INDEX idx_courses_teacher_id ON courses(teacher_id);
CREATE INDEX idx_courses_domain ON courses(domain);
CREATE INDEX idx_enrollments_student_id ON enrollments(student_id);
CREATE INDEX idx_enrollments_course_id ON enrollments(course_id);
CREATE INDEX idx_videos_course_id ON videos(course_id);

-- Step 8: Create unique constraint
CREATE UNIQUE INDEX idx_enrollments_unique ON enrollments(student_id, course_id);

-- Done! Tables created successfully
