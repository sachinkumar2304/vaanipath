import asyncio
import uuid
import json
from app.db.supabase_client import supabase
from datetime import datetime

async def migrate_legacy_videos():
    print("Starting migration of legacy videos...")
    
    # 1. Fetch all videos with null course_id
    response = supabase.table("videos").select("*").is_("course_id", "null").execute()
    videos = response.data
    
    if not videos:
        print("No legacy videos found.")
        return

    print(f"Found {len(videos)} legacy videos.")
    
    # 2. Group by uploaded_by (teacher_id)
    videos_by_teacher = {}
    for video in videos:
        teacher_id = video.get("uploaded_by")
        if not teacher_id:
            print(f"Skipping video {video['id']} - no uploader")
            continue
            
        if teacher_id not in videos_by_teacher:
            videos_by_teacher[teacher_id] = []
        videos_by_teacher[teacher_id].append(video)
        
    # 3. Create course for each teacher and assign videos
    for teacher_id, teacher_videos in videos_by_teacher.items():
        print(f"Processing teacher {teacher_id} with {len(teacher_videos)} videos...")
        
        # Check if "Legacy Videos" course already exists
        existing_course = supabase.table("courses")\
            .select("id")\
            .eq("teacher_id", teacher_id)\
            .eq("title", "Legacy Videos")\
            .execute()
            
        if existing_course.data:
            course_id = existing_course.data[0]["id"]
            print(f"Found existing 'Legacy Videos' course: {course_id}")
        else:
            # Create new course
            course_id = str(uuid.uuid4())
            course_data = {
                "id": course_id,
                "title": "Legacy Videos",
                "name": "Legacy Videos",  # Required for legacy compatibility
                "description": "Collection of previously uploaded videos",
                "teacher_id": teacher_id,
                "tutor_id": teacher_id,  # Required for legacy compatibility
                "domain": "other",
                "source_language": "en",
                "target_languages": "[]",  # Send as string
                "created_at": datetime.utcnow().isoformat(),
                "thumbnail_url": teacher_videos[0].get("thumbnail_url")
            }
            
            print(f"Attempting to insert course: {json.dumps(course_data, indent=2)}")
            
            try:
                res = supabase.table("courses").insert(course_data).execute()
                if not res.data:
                    print(f"Failed to create course for teacher {teacher_id} (No data returned)")
                    continue
                print(f"Created new 'Legacy Videos' course: {course_id}")
            except Exception as e:
                print(f"ERROR creating course for teacher {teacher_id}:")
                print(e)
                if hasattr(e, 'code'): print(f"Code: {e.code}")
                if hasattr(e, 'message'): print(f"Message: {e.message}")
                if hasattr(e, 'details'): print(f"Details: {e.details}")
                continue
            
        # Update videos
        video_ids = [v["id"] for v in teacher_videos]
        update_res = supabase.table("videos")\
            .update({"course_id": course_id})\
            .in_("id", video_ids)\
            .execute()
            
        print(f"Moved {len(video_ids)} videos to course {course_id}")

    print("Migration complete!")

if __name__ == "__main__":
    asyncio.run(migrate_legacy_videos())
