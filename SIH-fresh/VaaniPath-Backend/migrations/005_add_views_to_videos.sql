-- Add views column to videos table
ALTER TABLE videos ADD COLUMN IF NOT EXISTS views INTEGER DEFAULT 0;
