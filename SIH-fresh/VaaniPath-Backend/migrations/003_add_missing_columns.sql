-- Add missing columns to existing courses and enrollments tables
-- Run this in Supabase SQL Editor
-- This will NOT delete any existing data!

-- Step 1: Add missing columns to courses table (if they don't exist)
DO $$ 
BEGIN
    -- Add title column (alias for name)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='courses' AND column_name='title') THEN
        ALTER TABLE courses ADD COLUMN title TEXT;
    END IF;
    
    -- Add teacher_id column (alias for tutor_id)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='courses' AND column_name='teacher_id') THEN
        ALTER TABLE courses ADD COLUMN teacher_id TEXT;
    END IF;
    
    -- Add domain column if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='courses' AND column_name='domain') THEN
        ALTER TABLE courses ADD COLUMN domain TEXT DEFAULT 'other';
    END IF;
    
    -- Add source_language if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='courses' AND column_name='source_language') THEN
        ALTER TABLE courses ADD COLUMN source_language TEXT DEFAULT 'en';
    END IF;
    
    -- Add target_languages if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='courses' AND column_name='target_languages') THEN
        ALTER TABLE courses ADD COLUMN target_languages TEXT DEFAULT '[]';
    END IF;
    
    -- Add thumbnail_url if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='courses' AND column_name='thumbnail_url') THEN
        ALTER TABLE courses ADD COLUMN thumbnail_url TEXT;
    END IF;
    
    -- Add created_at if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='courses' AND column_name='created_at') THEN
        ALTER TABLE courses ADD COLUMN created_at TIMESTAMP DEFAULT NOW();
    END IF;
    
    -- Add updated_at if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='courses' AND column_name='updated_at') THEN
        ALTER TABLE courses ADD COLUMN updated_at TIMESTAMP;
    END IF;
END $$;

-- Step 2: Sync existing data (copy tutor_id to teacher_id, name to title)
UPDATE courses SET teacher_id = tutor_id WHERE teacher_id IS NULL AND tutor_id IS NOT NULL;
UPDATE courses SET title = name WHERE title IS NULL AND name IS NOT NULL;

-- Step 3: Add missing columns to enrollments table
DO $$ 
BEGIN
    -- Add student_id column (alias for user_id)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='enrollments' AND column_name='student_id') THEN
        ALTER TABLE enrollments ADD COLUMN student_id TEXT;
    END IF;
    
    -- Add course_id if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='enrollments' AND column_name='course_id') THEN
        ALTER TABLE enrollments ADD COLUMN course_id TEXT;
    END IF;
    
    -- Add progress column if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='enrollments' AND column_name='progress') THEN
        ALTER TABLE enrollments ADD COLUMN progress TEXT DEFAULT '{}';
    END IF;
END $$;

-- Step 4: Sync enrollment data
UPDATE enrollments SET student_id = user_id WHERE student_id IS NULL AND user_id IS NOT NULL;

-- Step 5: Add course_id and order to videos table (if missing)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='videos' AND column_name='course_id') THEN
        ALTER TABLE videos ADD COLUMN course_id TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='videos' AND column_name='order') THEN
        ALTER TABLE videos ADD COLUMN "order" INTEGER DEFAULT 0;
    END IF;
END $$;

-- Step 6: Create indexes if they don't exist
CREATE INDEX IF NOT EXISTS idx_courses_teacher_id ON courses(teacher_id);
CREATE INDEX IF NOT EXISTS idx_courses_tutor_id ON courses(tutor_id);
CREATE INDEX IF NOT EXISTS idx_courses_domain ON courses(domain);
CREATE INDEX IF NOT EXISTS idx_enrollments_student_id ON enrollments(student_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_user_id ON enrollments(user_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_course_id ON enrollments(course_id);
CREATE INDEX IF NOT EXISTS idx_videos_course_id ON videos(course_id);

-- Done! Your existing data is preserved, new columns added!
