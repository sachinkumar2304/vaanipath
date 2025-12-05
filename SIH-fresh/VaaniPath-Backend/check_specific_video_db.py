"""
Direct Supabase query to check specific video
"""
import asyncio
from app.db.supabase_client import supabase

async def check_specific_video():
    video_id = "334828f7-e263-4f03-855d-85cca59c2954"
    
    print(f"Querying video: {video_id}\n")
    
    response = supabase.table("videos").select("*").eq("id", video_id).execute()
    
    if not response.data:
        print("❌ Video not found!")
        return
    
    video = response.data[0]
    
    print("=== Video Database Record ===")
    print(f"Title: {video.get('title')}")
    print(f"file_url: {video.get('file_url')}")
    print(f"cloudinary_url: {video.get('cloudinary_url')}")
    print(f"cloudinary_public_id: {video.get('cloudinary_public_id')}")
    print(f"status: {video.get('status')}")
    print(f"content_type: {video.get('content_type')}")
    
    print("\n=== All Fields ===")
    for key, value in video.items():
        if value is not None:
            print(f"{key}: {value}")

if __name__ == "__main__":
    asyncio.run(check_specific_video())
