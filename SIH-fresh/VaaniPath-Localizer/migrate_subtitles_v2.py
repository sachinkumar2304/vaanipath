"""
Migration Script V2: Generate Subtitles from Database Transcriptions
Uses stored transcriptions from Supabase instead of local manifest files
"""
import os
import sys
import json
from pathlib import Path
import tempfile

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from localizer.utils import generate_vtt
from localizer.cloudinary_uploader import upload_video_to_cloudinary
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase
SUPABASE_URL = (
    os.getenv("SUPABASE_URL") or 
    os.getenv("NEXT_PUBLIC_SUPABASE_URL")
)
SUPABASE_KEY = (
    os.getenv("SUPABASE_ANON_KEY") or 
    os.getenv("SUPABASE_KEY") or
    os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
)

print(f"📡 Connecting to Supabase...")
print(f"   URL: {SUPABASE_URL[:30] if SUPABASE_URL else 'Not set'}...")
print(f"   Key: {'*' * 20}")

if not SUPABASE_URL:
    print("\n❌ ERROR: Supabase URL not configured!")
    sys.exit(1)

if not SUPABASE_KEY:
    print("\n❌ ERROR: Supabase key not configured!")
    sys.exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def parse_transcription(transcription_text):
    """Parse transcription text into chunks with timestamps"""
    if not transcription_text:
        return []
    
    # Try to parse as JSON first (if stored as JSON)
    try:
        data = json.loads(transcription_text)
        if isinstance(data, list):
            return data
    except:
        pass
    
    # If plain text, create simple chunks (1 second intervals)
    # This is a fallback - ideally transcriptions should have timestamps
    chunks = []
    words = transcription_text.split()
    chunk_size = 10  # words per chunk
    duration_per_word = 0.5  # seconds
    
    for i in range(0, len(words), chunk_size):
        chunk_words = words[i:i+chunk_size]
        text = " ".join(chunk_words)
        start = i * duration_per_word
        end = (i + len(chunk_words)) * duration_per_word
        
        chunks.append({
            "start": start,
            "end": end,
            "text": text
        })
    
    return chunks

def migrate_from_database():
    """Generate subtitles from database transcriptions"""
    print("🚀 Starting subtitle migration from database...")
    
    # 1. Get all completed translations without subtitle_url
    translations_response = supabase.table("translations")\
        .select("id, video_id, language, dubbed_video_url, translated_text")\
        .eq("status", "completed")\
        .is_("subtitle_url", "null")\
        .execute()
    
    if not translations_response.data:
        print("✅ No videos to migrate!")
        return
    
    print(f"📊 Found {len(translations_response.data)} dubbed videos without subtitles")
    
    success_count = 0
    error_count = 0
    
    for translation in translations_response.data:
        video_id = translation["video_id"]
        language = translation["language"]
        trans_id = translation["id"]
        translated_text = translation.get("translated_text")
        
        print(f"\n🎬 Processing: Video {video_id} - {language}")
        
        try:
            # 2. Get transcription from database
            if translated_text:
                # Use translated text from translations table
                chunks = parse_transcription(translated_text)
                print(f"  ✅ Found {len(chunks)} chunks from translated_text")
            else:
                # Try to get from transcriptions table
                transcription_response = supabase.table("transcriptions")\
                    .select("full_text")\
                    .eq("video_id", video_id)\
                    .eq("language", language)\
                    .execute()
                
                if not transcription_response.data:
                    print(f"  ⚠️  No transcription found in database")
                    error_count += 1
                    continue
                
                full_text = transcription_response.data[0].get("full_text")
                chunks = parse_transcription(full_text)
                print(f"  ✅ Found {len(chunks)} chunks from transcriptions table")
            
            if not chunks:
                print(f"  ⚠️  No chunks to process")
                error_count += 1
                continue
            
            # 3. Generate VTT file in temp directory
            with tempfile.TemporaryDirectory() as tmpdir:
                vtt_filename = f"subtitles_{language}.vtt"
                vtt_path = os.path.join(tmpdir, vtt_filename)
                
                generate_vtt(chunks, vtt_path)
                print(f"  ✅ Generated VTT: {vtt_filename}")
                
                # 4. Upload to Cloudinary
                subtitle_url = upload_video_to_cloudinary(
                    file_path=vtt_path,
                    video_id=video_id,
                    language=language,
                    content_type='subtitle'
                )
                
                if not subtitle_url:
                    print(f"  ❌ Upload failed")
                    error_count += 1
                    continue
                
                print(f"  ☁️  Uploaded: {subtitle_url}")
            
            # 5. Update database
            supabase.table("translations").update({
                "subtitle_url": subtitle_url
            }).eq("id", trans_id).execute()
            
            print(f"  💾 Database updated")
            success_count += 1
            
            # 6. Also generate English subtitle from original transcription
            if language != "en":
                print(f"  🇬🇧 Generating English subtitle...")
                
                # Get original English transcription
                en_trans_response = supabase.table("transcriptions")\
                    .select("full_text")\
                    .eq("video_id", video_id)\
                    .eq("language", "en")\
                    .execute()
                
                if en_trans_response.data:
                    en_text = en_trans_response.data[0].get("full_text")
                    en_chunks = parse_transcription(en_text)
                    
                    if en_chunks:
                        with tempfile.TemporaryDirectory() as tmpdir:
                            en_vtt_path = os.path.join(tmpdir, "subtitles_en.vtt")
                            generate_vtt(en_chunks, en_vtt_path)
                            
                            # Upload English VTT
                            en_subtitle_url = upload_video_to_cloudinary(
                                file_path=en_vtt_path,
                                video_id=video_id,
                                language="en",
                                content_type='subtitle'
                            )
                            
                            if en_subtitle_url:
                                # Check if English translation entry exists
                                en_check = supabase.table("translations")\
                                    .select("id")\
                                    .eq("video_id", video_id)\
                                    .eq("language", "en")\
                                    .execute()
                                
                                if en_check.data:
                                    # Update existing
                                    supabase.table("translations").update({
                                        "subtitle_url": en_subtitle_url
                                    }).eq("id", en_check.data[0]["id"]).execute()
                                else:
                                    # Create new entry for English
                                    supabase.table("translations").insert({
                                        "video_id": video_id,
                                        "language": "en",
                                        "subtitle_url": en_subtitle_url,
                                        "status": "completed"
                                    }).execute()
                                
                                print(f"  ✅ English subtitle added")
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            error_count += 1
            continue
    
    print(f"\n🎉 Migration complete!")
    print(f"   ✅ Success: {success_count}")
    print(f"   ❌ Failed: {error_count}")

if __name__ == "__main__":
    migrate_from_database()
