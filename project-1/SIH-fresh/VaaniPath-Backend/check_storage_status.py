import json
import os
from app.db.supabase_client import supabase
import asyncio

async def check_status():
    # 1. Check Local Manifest
    manifest_path = r"d:\project-1\SIH-fresh\VaaniPath-Localizer\localizer\output\0e650047-787f-4dd7-97c5-66999a397500\manifest.json"
    
    print(f"\n--- Checking Manifest: {manifest_path} ---")
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"Cloudinary URL: {data.get('cloudinary_url', 'NOT FOUND')}")
            print(f"Original Text Length: {len(data.get('chunks', [{}])[0].get('text_original', ''))}")
            print(f"Translated Text Length: {len(data.get('chunks', [{}])[0].get('text_translated', ''))}")
            print(f"Is Audio Only: {data.get('is_audio_only', False)}")
    else:
        print("Manifest file not found!")

    # 2. Check Database
    print(f"\n--- Checking Database (Transcriptions) ---")
    try:
        response = supabase.table("transcriptions").select("count", count="exact").execute()
        print(f"Total Transcriptions in DB: {response.count}")
        
        # Check specific video
        vid_response = supabase.table("transcriptions").select("*").eq("video_id", "0e650047-787f-4dd7-97c5-66999a397500").execute()
        print(f"Transcription for this video in DB: {'YES' if vid_response.data else 'NO'}")
    except Exception as e:
        print(f"DB Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_status())
