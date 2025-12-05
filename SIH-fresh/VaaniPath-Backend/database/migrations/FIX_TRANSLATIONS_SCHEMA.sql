-- Add progress_percentage column if missing
ALTER TABLE translations ADD COLUMN IF NOT EXISTS progress_percentage INTEGER DEFAULT 0;

-- Add dubbed_video_url column if missing
ALTER TABLE translations ADD COLUMN IF NOT EXISTS dubbed_video_url TEXT;

-- Add audio_url column if missing
ALTER TABLE translations ADD COLUMN IF NOT EXISTS audio_url TEXT;

-- Add error_message column if missing
ALTER TABLE translations ADD COLUMN IF NOT EXISTS error_message TEXT;

-- Add comments
COMMENT ON COLUMN translations.progress_percentage IS 'Progress of dubbing/translation generation (0-100)';
COMMENT ON COLUMN translations.dubbed_video_url IS 'URL of the dubbed video file';
COMMENT ON COLUMN translations.audio_url IS 'URL of the dubbed audio file';

-- Reload schema cache to ensure API picks up the new columns
NOTIFY pgrst, 'reload schema';
