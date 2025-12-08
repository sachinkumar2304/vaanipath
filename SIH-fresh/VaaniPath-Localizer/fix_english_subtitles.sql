-- Insert English subtitle for video eed30668-fc50-4a59-a0e4-5a3ba06dffa5
INSERT INTO translations (video_id, language, subtitle_url, status, translated_text)
VALUES (
  'eed30668-fc50-4a59-a0e4-5a3ba06dffa5', 
  'en', 
  'https://res.cloudinary.com/dokvotjx6/raw/upload/v1764761447/gyanify/subtitles/gyanify/subtitles/eed30668-fc50-4a59-a0e4-5a3ba06dffa5_en.vtt', 
  'completed',
  'Original English Transcript'
)
ON CONFLICT (video_id, language) 
DO UPDATE SET 
  subtitle_url = EXCLUDED.subtitle_url,
  status = 'completed';
