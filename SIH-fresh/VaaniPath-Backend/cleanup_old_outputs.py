"""
Cleanup script to delete old output files that are already on Cloudinary
"""
import os
import json
import shutil
import sys
from app.db.supabase_client import supabase

print("=" * 70)
print("🗑️  Gyanify Output Folder Cleanup")
print("=" * 70)

output_dir = r"d:\project-1\SIH-fresh\VaaniPath-Localizer\localizer\output"

if not os.path.exists(output_dir):
    print("❌ Output directory doesn't exist")
    exit()

# Get all job folders
job_folders = [d for d in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir, d))]
print(f"\n📁 Total folders: {len(job_folders)}")

safe_to_delete = []
total_size = 0

print("\n🔍 Analyzing folders...\n")

for job_id in job_folders:
    job_path = os.path.join(output_dir, job_id)
    manifest_path = os.path.join(job_path, "manifest.json")
    
    if not os.path.exists(manifest_path):
        continue
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        cloudinary_url = manifest.get("cloudinary_url")
        
        if cloudinary_url and "cloudinary.com" in cloudinary_url:
            # Calculate folder size
            folder_size = sum(os.path.getsize(os.path.join(dirpath, filename))
                            for dirpath, dirnames, filenames in os.walk(job_path)
                            for filename in filenames)
            
            safe_to_delete.append({
                'id': job_id,
                'path': job_path,
                'size': folder_size,
                'url': cloudinary_url
            })
            total_size += folder_size
            
            print(f"✅ {job_id[:25]}... ({folder_size / (1024*1024):.1f} MB)")
    
    except Exception as e:
        print(f"⚠️  {job_id[:25]}... - Error: {e}")

print("\n" + "=" * 70)
print(f"📊 Summary:")
print(f"   Folders to delete: {len(safe_to_delete)}")
print(f"   Total space: {total_size / (1024*1024):.2f} MB ({total_size / (1024*1024*1024):.2f} GB)")
print("=" * 70)

if not safe_to_delete:
    print("\n✅ No files to delete!")
    exit()

# Check if --confirm flag is present
if "--confirm" in sys.argv or "-y" in sys.argv:
    print("\n🗑️  Deleting folders...")
    deleted = 0
    errors = 0
    
    for item in safe_to_delete:
        try:
            shutil.rmtree(item['path'])
            deleted += 1
            print(f"   ✅ Deleted: {item['id'][:30]}...")
        except Exception as e:
            errors += 1
            print(f"   ❌ Failed: {item['id'][:30]}... - {e}")
    
    print(f"\n✅ Cleanup complete!")
    print(f"   Deleted: {deleted} folders")
    print(f"   Errors: {errors}")
    print(f"   Space freed: {total_size / (1024*1024):.2f} MB")
else:
    print("\n⚠️  DRY RUN MODE - No files deleted")
    print("\n📋 To actually delete these files, run:")
    print("   python cleanup_old_outputs.py --confirm")
    print("\n💡 Or to skip confirmation:")
    print("   python cleanup_old_outputs.py -y")
