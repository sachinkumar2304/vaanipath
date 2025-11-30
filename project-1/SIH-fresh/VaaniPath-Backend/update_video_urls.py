"""
Script to update Supabase videos with Cloudinary URLs
"""
import asyncio
from app.db.supabase_client import supabase

# You need to manually map video IDs to their Cloudinary URLs
# Get the URLs from your Cloudinary dashboard
VIDEO_URL_MAPPING = {
    # Example format - replace with your actual data:
    # "video-id-here": "https://res.cloudinary.com/your-cloud/video/upload/...",
    
    # Add your video mappings here:
    # "334828f7-e263-4f03-855d-85cca59c2954": "https://res.cloudinary.com/dokvotjx6/video/upload/v1234567890/gyanify/videos/organic_farming.mp4",
}

async def update_video_urls():
    """
    Update videos in database with Cloudinary URLs
    """
    if not VIDEO_URL_MAPPING:
        print("⚠️  No video mappings defined!")
        print("\nPlease edit this file and add your video ID to Cloudinary URL mappings.")
        print("\nFormat:")
        print('VIDEO_URL_MAPPING = {')
        print('    "video-id": "cloudinary-url",')
        print('}')
        return
    
    print(f"Updating {len(VIDEO_URL_MAPPING)} videos...")
    
    for video_id, cloudinary_url in VIDEO_URL_MAPPING.items():
        try:
            result = supabase.table("videos").update({
                "file_url": cloudinary_url
            }).eq("id", video_id).execute()
            
            if result.data:
                print(f"✅ Updated video {video_id}")
            else:
                print(f"❌ Failed to update {video_id}")
        except Exception as e:
            print(f"❌ Error updating {video_id}: {e}")

if __name__ == "__main__":
    asyncio.run(update_video_urls())
