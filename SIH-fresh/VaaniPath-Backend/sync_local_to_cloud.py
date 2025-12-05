import os
import json
import asyncio
import cloudinary
import cloudinary.uploader
from app.db.supabase_client import supabase
from app.config import settings

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)

OUTPUT_DIR = r"d:\project-1\SIH-fresh\VaaniPath-Localizer\localizer\output"

async def sync_job(job_id):
    job_dir = os.path.join(OUTPUT_DIR, job_id)
    manifest_path = os.path.join(job_dir, "manifest.json")
    final_video_path = os.path.join(job_dir, "final_video.mp4")
    
    if not os.path.exists(manifest_path):
        print(f"Skipping {job_id}: No manifest.json")
        return

    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    except Exception as e:
        print(f"Error reading manifest for {job_id}: {e}")
        return

    # 1. Upload to Cloudinary if missing
    cloudinary_url = manifest.get("cloudinary_url")
    if not cloudinary_url:
        if os.path.exists(final_video_path):
            print(f"Uploading {job_id} to Cloudinary...")
            try:
                # Upload video
                upload_result = cloudinary.uploader.upload(
                    final_video_path, 
                    resource_type="video",
                    public_id=f"gyanify/dubbed/{job_id}_{manifest.get('target_lang', 'unknown')}",
                    eager=[{'width': 300, 'height': 300, 'crop': 'pad', 'audio_codec': 'none'}] # Generate thumbnail
                )
                cloudinary_url = upload_result.get("secure_url")
                manifest["cloudinary_url"] = cloudinary_url
                
                # Save updated manifest locally
                with open(manifest_path, 'w', encoding='utf-8') as f:
                    json.dump(manifest, f, ensure_ascii=False, indent=2)
                print(f"Uploaded! URL: {cloudinary_url}")
            except Exception as e:
                print(f"Upload failed for {job_id}: {e}")
        else:
            print(f"Skipping upload for {job_id}: final_video.mp4 not found")

    # 2. Sync to Database
    if cloudinary_url:
        target_lang = manifest.get("target_lang")
        source_lang = manifest.get("source_lang", "en")
        course_id = manifest.get("course_id")
        
        # Extract full text from chunks
        full_text_original = ""
        full_text_translated = ""
        segments = []
        
        for chunk in manifest.get("chunks", []):
            full_text_original += chunk.get("text_original", "") + " "
            full_text_translated += chunk.get("text_translated", "") + " "
            segments.append({
                "start": chunk.get("start"),
                "end": chunk.get("end"),
                "text": chunk.get("text_translated")
            })
            
        full_text_original = full_text_original.strip()
        full_text_translated = full_text_translated.strip()

        print(f"Syncing DB for {job_id} ({target_lang})...")
        
        try:
            # 0. Ensure Video Exists (Foreign Key Check)
            video_check = supabase.table("videos").select("id").eq("id", job_id).execute()
            if not video_check.data:
                print(f"Video {job_id} missing in DB. Creating placeholder...")
                # Create placeholder video record
                placeholder_data = {
                    "id": job_id,
                    "title": f"Recovered Video {job_id}",
                    "file_url": cloudinary_url, # Use the dubbed URL as fallback or original if known
                    "source_language": source_lang,
                    "uploaded_by": "00000000-0000-0000-0000-000000000000", # Needs a valid user ID, using a dummy or fetching admin
                    "status": "completed"
                }
                # We need a valid user ID. Let's fetch the first admin user.
                admin_user = supabase.table("users").select("id").eq("is_admin", True).limit(1).execute()
                if admin_user.data:
                    placeholder_data["uploaded_by"] = admin_user.data[0]["id"]
                else:
                    # Fallback: fetch ANY user
                    any_user = supabase.table("users").select("id").limit(1).execute()
                    if any_user.data:
                         placeholder_data["uploaded_by"] = any_user.data[0]["id"]
                    else:
                        print(f"Cannot create placeholder: No users found in DB.")
                        return

                supabase.table("videos").insert(placeholder_data).execute()
                print("Placeholder video created.")

            # A. Update Translations Table
            # Check if record exists
            existing = supabase.table("translations").select("id").eq("video_id", job_id).eq("language", target_lang).execute()
            
            translation_data = {
                "video_id": job_id,
                "language": target_lang,
                "translated_text": full_text_translated,
                "dubbed_video_url": cloudinary_url,
                "status": "completed",
                "updated_at": "now()"
            }
            
            if existing.data:
                supabase.table("translations").update(translation_data).eq("id", existing.data[0]['id']).execute()
            else:
                supabase.table("translations").insert(translation_data).execute()
                
            # B. Insert into Transcriptions Table (Original Transcript)
            # Check if exists
            trans_existing = supabase.table("transcriptions").select("id").eq("video_id", job_id).eq("language", source_lang).execute()
            
            transcription_data = {
                "video_id": job_id,
                "language": source_lang,
                "full_text": full_text_original,
                "status": "completed"
            }
            
            if trans_existing.data:
                supabase.table("transcriptions").update(transcription_data).eq("id", trans_existing.data[0]['id']).execute()
            else:
                supabase.table("transcriptions").insert(transcription_data).execute()
                
            print(f"DB Synced for {job_id}")
            
        except Exception as e:
            print(f"DB Sync failed for {job_id}: {e}")

async def main():
    print("Starting Sync Process...")
    if not os.path.exists(OUTPUT_DIR):
        print("Output directory not found!")
        return

    jobs = [d for d in os.listdir(OUTPUT_DIR) if os.path.isdir(os.path.join(OUTPUT_DIR, d))]
    print(f"Found {len(jobs)} jobs.")
    
    for job_id in jobs:
        await sync_job(job_id)
        
    print("\nSync Complete!")

if __name__ == "__main__":
    asyncio.run(main())
