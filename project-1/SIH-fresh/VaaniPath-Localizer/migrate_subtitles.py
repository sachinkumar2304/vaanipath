"""
Migration Script: Generate Subtitles for Old Dubbed Videos
This script processes existing dubbed videos that don't have subtitles yet.
"""
import os
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from localizer.utils import generate_vtt
from localizer.cloudinary_uploader import upload_video_to_cloudinary
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase - Try multiple variable name patterns
SUPABASE_URL = (
    os.getenv("SUPABASE_URL") or 
    os.getenv("NEXT_PUBLIC_SUPABASE_URL") or
    "https://your-project.supabase.co"  # Replace with your actual URL
)
SUPABASE_KEY = (
    os.getenv("SUPABASE_ANON_KEY") or 
    os.getenv("SUPABASE_KEY") or
    os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY") or
    "your-anon-key"  # Replace with your actual key
)

print(f"📡 Connecting to Supabase...")
print(f"   URL: {SUPABASE_URL[:30]}...")
print(f"   Key: {'*' * 20}")

if not SUPABASE_URL or SUPABASE_URL == "https://your-project.supabase.co":
    print("\n❌ ERROR: Supabase URL not configured!")
    print("📝 Please set SUPABASE_URL in your .env file")
    print("   Example: SUPABASE_URL=https://xxxxx.supabase.co")
    sys.exit(1)

if not SUPABASE_KEY or SUPABASE_KEY == "your-anon-key":
    print("\n❌ ERROR: Supabase key not configured!")
    print("📝 Please set SUPABASE_ANON_KEY in your .env file")
    sys.exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def migrate_old_videos():
    """Generate and upload subtitles for old dubbed videos"""
    print("🚀 Starting subtitle migration for old videos...")
    
    # 1. Get all completed translations without subtitle_url
    response = supabase.table("translations")\
        .select("id, video_id, language, dubbed_video_url")\
        .eq("status", "completed")\
        .is_("subtitle_url", "null")\
        .execute()
    
    if not response.data:
        print("✅ No videos to migrate!")
        return
    
    print(f"📊 Found {len(response.data)} dubbed videos without subtitles")
    
    for translation in response.data:
        video_id = translation["video_id"]
        language = translation["language"]
        trans_id = translation["id"]
        
        print(f"\n🎬 Processing: Video {video_id} - {language}")
        
        try:
            # 2. Find manifest file
            manifest_dir = Path("localizer/output") / video_id
            manifest_path = manifest_dir / "manifest.json"
            
            if not manifest_path.exists():
                print(f"  ⚠️  Manifest not found: {manifest_path}")
                continue
            
            # 3. Load manifest
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            
            chunks = manifest.get("chunks", [])
            if not chunks:
                print(f"  ⚠️  No chunks in manifest")
                continue
            
            # 4. Generate VTT file
            vtt_filename = f"subtitles_{language}.vtt"
            vtt_path = manifest_dir / vtt_filename
            
            generate_vtt(chunks, str(vtt_path))
            print(f"  ✅ Generated VTT: {vtt_filename}")
            
            # 5. Upload to Cloudinary
            subtitle_url = upload_video_to_cloudinary(
                file_path=str(vtt_path),
                video_id=video_id,
                language=language,
                content_type='subtitle'
            )
            
            if not subtitle_url:
                print(f"  ❌ Upload failed")
                continue
            
            print(f"  ☁️  Uploaded: {subtitle_url}")
            
            # 6. Update database
            supabase.table("translations").update({
                "subtitle_url": subtitle_url
            }).eq("id", trans_id).execute()
            
            print(f"  💾 Database updated")
            
            # 7. Also generate English subtitle if not exists
            if language != "en":
                print(f"  🇬🇧 Generating English subtitle...")
                
                # Create English chunks
                english_chunks = []
                for chunk in chunks:
                    english_chunks.append({
                        "start": chunk["start"],
                        "end": chunk["end"],
                        "text": chunk.get("text_original", chunk.get("text", ""))
                    })
                
                # Generate English VTT
                en_vtt_path = manifest_dir / "subtitles_en.vtt"
                generate_vtt(english_chunks, str(en_vtt_path))
                
                # Upload English VTT
                en_subtitle_url = upload_video_to_cloudinary(
                    file_path=str(en_vtt_path),
                    video_id=video_id,
                    language="en",
                    content_type='subtitle'
                )
                
                if en_subtitle_url:
                    # Save English subtitle (check if entry exists)
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
            continue
    
    print("\n🎉 Migration complete!")

if __name__ == "__main__":
    migrate_old_videos()
