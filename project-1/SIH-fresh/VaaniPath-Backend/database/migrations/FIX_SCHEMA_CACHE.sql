-- =====================================================
-- CRITICAL: Run this in Supabase SQL Editor
-- This fixes the "posts column not found" error
-- =====================================================

-- Step 1: Reload Supabase Schema Cache
NOTIFY pgrst, 'reload schema';

-- Step 2: Verify Tables Exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('doubts', 'quiz_questions', 'quiz_sessions', 'user_answers');

-- Step 3: Verify quiz_questions Columns (should NOT have 'posts')
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'quiz_questions'
ORDER BY ordinal_position;

-- Step 4: Verify doubts Table
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'doubts'
ORDER BY ordinal_position;

-- Step 5: Check for any videos with NULL target_languages
SELECT id, title, target_languages, source_language
FROM videos
WHERE target_languages IS NULL OR source_language IS NULL
LIMIT 10;

-- Step 6 (Optional): Fix NULL target_languages if any exist
UPDATE videos
SET target_languages = ARRAY[]::text[]
WHERE target_languages IS NULL;

UPDATE videos
SET source_language = 'en'
WHERE source_language IS NULL;

-- =====================================================
-- After running these commands:
-- 1. Quiz creation should work ✅
-- 2. Doubts page should load ✅  
-- 3. Language selector should show languages ✅
-- =====================================================
