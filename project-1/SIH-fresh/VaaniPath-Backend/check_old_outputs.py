"""
Script to verify Cloudinary uploads and safely delete local output files
"""
import os
import json
import shutil
from app.db.supabase_client import supabase

print("=" * 70)
print("🔍 Checking Old Output Files vs Cloudinary")
print("=" * 70)

output_dir = r"d:\project-1\SIH-fresh\VaaniPath-Localizer\localizer\output"

if not os.path.exists(output_dir):
    print("❌ Output directory doesn't exist")
    exit()

# Get all job folders
job_folders = [d for d in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir, d))]
print(f"\n📁 Found {len(job_folders)} job folders\n")

safe_to_delete = []
needs_check = []

for job_id in job_folders:
    job_path = os.path.join(output_dir, job_id)
    manifest_path = os.path.join(job_path, "manifest.json")
    
    # Check if manifest exists
    if not os.path.exists(manifest_path):
        print(f"⚠️  {job_id}: No manifest.json - SKIP")
        continue
    
    try:
        # Read manifest
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        cloudinary_url = manifest.get("cloudinary_url")
        
        if cloudinary_url:
            # Check if this video exists in database
            video_check = supabase.table("videos").select("id").eq("id", job_id).execute()
            
            if video_check.data:
                print(f"✅ {job_id[:20]}... - Cloudinary: YES, DB: YES - SAFE TO DELETE")
                safe_to_delete.append(job_id)
            else:
                print(f"⚠️  {job_id[:20]}... - Cloudinary: YES, DB: NO - NEEDS CHECK")
                needs_check.append(job_id)
        else:
            print(f"❌ {job_id[:20]}... - Cloudinary: NO - KEEP")
    
    except Exception as e:
        print(f"❌ {job_id[:20]}... - Error: {e} - KEEP")

print("\n" + "=" * 70)
print(f"📊 Summary:")
print(f"   Safe to delete: {len(safe_to_delete)}")
print(f"   Needs manual check: {len(needs_check)}")
print(f"   Total folders: {len(job_folders)}")
print("=" * 70)

if safe_to_delete:
    print(f"\n🗑️  Ready to delete {len(safe_to_delete)} folders")
    print("\nDo you want to delete these folders? (yes/no): ", end="")
    
    # For script automation, we'll just show what would be deleted
    print("\n\n📋 Folders that will be deleted:")
    for job_id in safe_to_delete[:10]:  # Show first 10
        job_path = os.path.join(output_dir, job_id)
        size = sum(os.path.getsize(os.path.join(dirpath, filename))
                   for dirpath, dirnames, filenames in os.walk(job_path)
                   for filename in filenames)
        size_mb = size / (1024 * 1024)
        print(f"   - {job_id[:30]}... ({size_mb:.2f} MB)")
    
    if len(safe_to_delete) > 10:
        print(f"   ... and {len(safe_to_delete) - 10} more")
    
    total_size = 0
    for job_id in safe_to_delete:
        job_path = os.path.join(output_dir, job_id)
        size = sum(os.path.getsize(os.path.join(dirpath, filename))
                   for dirpath, dirnames, filenames in os.walk(job_path)
                   for filename in filenames)
        total_size += size
    
    print(f"\n💾 Total space to free: {total_size / (1024 * 1024):.2f} MB")
    print("\n⚠️  To actually delete, run: python cleanup_old_outputs.py --confirm")
else:
    print("\n✅ No files safe to delete automatically")

if needs_check:
    print(f"\n⚠️  {len(needs_check)} folders need manual verification:")
    for job_id in needs_check[:5]:
        print(f"   - {job_id}")
