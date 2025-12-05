# SQL Commands for Supabase

Run these commands in your Supabase SQL Editor:

## 1. Add content_type field to videos table
```sql
ALTER TABLE videos ADD COLUMN IF NOT EXISTS content_type VARCHAR(20) DEFAULT 'video';

COMMENT ON COLUMN videos.content_type IS 'Type of content: video, audio, or document';
```

## 2. Add progress field to translations table (for dubbing progress)
```sql
ALTER TABLE translations ADD COLUMN IF NOT EXISTS progress_percentage FLOAT DEFAULT 0;

COMMENT ON COLUMN translations.progress_percentage IS 'Dubbing progress from ML service (0-100)';
```

## 3. Create unique constraint to prevent duplicate translations
```sql
-- This prevents duplicate entries when multiple students request same language
ALTER TABLE translations DROP CONSTRAINT IF EXISTS translations_video_language_unique;
ALTER TABLE translations ADD CONSTRAINT translations_video_language_unique 
    UNIQUE (video_id, language);
```

## 4. Verify RLS policies are enabled
```sql
-- Check if RLS is enabled on all tables
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('videos', 'translations', 'enrollments', 'quiz_questions');

-- If any table has rowsecurity = false, enable it:
-- ALTER TABLE table_name ENABLE ROW LEVEL SECURITY;
```

## 5. Optional: Add index for faster translations lookup
```sql
CREATE INDEX IF NOT EXISTS idx_translations_video_language 
ON translations(video_id, language);

CREATE INDEX IF NOT EXISTS idx_translations_status 
ON translations(status) WHERE status IN ('processing', 'pending');
```

---

## How to Run

1. Open Supabase Dashboard
2. Go to SQL Editor
3. Copy and paste each section above
4. Click "Run" for each query
5. Verify success messages

**Run Order**: Execute queries 1-5 in order for best results.
