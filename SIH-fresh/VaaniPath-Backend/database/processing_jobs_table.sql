-- ============================================
-- CREATE PROCESSING JOBS TABLE
-- Run this in Supabase SQL Editor if table doesn't exist
-- ============================================

CREATE TABLE IF NOT EXISTS processing_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
  job_type VARCHAR(50), -- 'transcription', 'translation', 'tts', 'dubbing'
  language VARCHAR(10),
  status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
  progress FLOAT DEFAULT 0, -- 0-100
  error_message TEXT,
  result JSONB, -- Store result data
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  completed_at TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_processing_jobs_video_id ON processing_jobs(video_id);
CREATE INDEX IF NOT EXISTS idx_processing_jobs_status ON processing_jobs(status);

-- Enable RLS
ALTER TABLE processing_jobs ENABLE ROW LEVEL SECURITY;

-- Add policy
CREATE POLICY "Anyone can read processing jobs" ON processing_jobs
  FOR SELECT USING (true);

-- Done!
