"""
Script to update all videos in database to set content_type = 'video'
"""
import asyncio
from app.db.supabase_client import supabase

async def fix_content_types():
    # Get all videos
    response = supabase.table("videos").select("*").execute()
    
    if not response.data:
        print("No videos found")
        return
    
    print(f"Found {len(response.data)} videos")
    
    updated_count = 0
    
    for video in response.data:
        video_id = video.get('id')
        title = video.get('title')
        current_content_type = video.get('content_type')
        file_url = video.get('file_url')
        
        # Determine content type from file_url if available
        new_content_type = current_content_type
        
        if not current_content_type or current_content_type == 'None':
            # Guess from file extension or just set to video
            if file_url:
                if any(ext in file_url.lower() for ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']):
                    new_content_type = 'video'
                elif any(ext in file_url.lower() for ext in ['.mp3', '.wav', '.m4a', '.aac']):
                    new_content_type = 'audio'
                elif any(ext in file_url.lower() for ext in ['.pdf', '.doc', '.docx', '.ppt']):
                    new_content_type = 'document'
                else:
                    new_content_type = 'video'  # Default to video
            else:
                new_content_type = 'video'  # Default to video
                
            try:
                result = supabase.table("videos").update({
                    "content_type": new_content_type
                }).eq("id", video_id).execute()
                
                print(f"✅ Updated '{title}': {current_content_type} → {new_content_type}")
                updated_count += 1
            except Exception as e:
                print(f"❌ Failed to update '{title}': {e}")
        else:
            print(f"⏭️  Skipped '{title}': already has content_type = {current_content_type}")
    
    print(f"\n✅ Updated {updated_count} videos")

if __name__ == "__main__":
    asyncio.run(fix_content_types())
