-- Add content_type field to videos table for detecting video/audio/document
ALTER TABLE videos ADD COLUMN IF NOT EXISTS content_type VARCHAR(20) DEFAULT 'video';

-- Add comment
COMMENT ON COLUMN videos.content_type IS 'Type of content: video, audio, or document';
