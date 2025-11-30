"""
Script to check which videos in the database are missing Cloudinary URLs
and help update them
"""
import asyncio
from app.db.supabase_client import supabase

async def check_videos_without_urls():
    # Get all videos
    response = supabase.table("videos").select("*").execute()
    
    if not response.data:
        print("No videos found in database")
        return
    
    total_videos = len(response.data)
    videos_without_url = []
    
    print(f"\n=== Checking {total_videos} videos ===\n")
    
    for video in response.data:
        video_id = video.get('id')
        title = video.get('title', 'Untitled')
        file_url = video.get('file_url')
        
        if not file_url or file_url == 'null':
            videos_without_url.append({
                'id': video_id,
                'title': title,
                'domain': video.get('domain'),
                'status': video.get('status')
            })
            print(f"❌ Missing URL: {title} (ID: {video_id})")
        else:
            print(f"✅ Has URL: {title}")
    
    print(f"\n=== Summary ===")
    print(f"Total videos: {total_videos}")
    print(f"Videos with URLs: {total_videos - len(videos_without_url)}")
    print(f"Videos WITHOUT URLs: {len(videos_without_url)}")
    
    if videos_without_url:
        print("\n=== Videos needing URL update ===")
        for v in videos_without_url:
            print(f"  - {v['title']} ({v['domain']}) - ID: {v['id']}")

if __name__ == "__main__":
    asyncio.run(check_videos_without_urls())
