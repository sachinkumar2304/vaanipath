-- Fix enrollments with NULL course_id
-- This SQL script cleans up bad enrollment data

-- Option 1: Delete enrollments with NULL course_id
DELETE FROM enrollments 
WHERE course_id IS NULL OR course_id::text = 'None';

-- Option 2: If you want to keep them but just log them
SELECT id, student_id, video_id, course_id, enrolled_at 
FROM enrollments
WHERE course_id IS NULL OR course_id::text = 'None';
