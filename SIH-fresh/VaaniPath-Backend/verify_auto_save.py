"""
Quick verification script to check if auto-save features are working
"""
from app.db.supabase_client import supabase
import os

print("=" * 60)
print("🔍 Gyanify Auto-Save Feature Verification")
print("=" * 60)

# 1. Check latest transcription
print("\n1️⃣ Checking Transcriptions Table...")
try:
    trans = supabase.table("transcriptions").select("*").order("created_at", desc=True).limit(3).execute()
    print(f"   Total transcriptions: {len(trans.data)}")
    if trans.data:
        latest = trans.data[0]
        print(f"   Latest: Video ID: {latest['video_id']}")
        print(f"   Language: {latest['language']}")
        print(f"   Text preview: {latest['full_text'][:100]}...")
        print(f"   Status: {latest['status']}")
    else:
        print("   ⚠️  No transcriptions found yet")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 2. Check latest translation
print("\n2️⃣ Checking Translations Table...")
try:
    transl = supabase.table("translations").select("*").order("created_at", desc=True).limit(3).execute()
    print(f"   Total translations: {len(transl.data)}")
    if transl.data:
        latest = transl.data[0]
        print(f"   Latest: Video ID: {latest['video_id']}")
        print(f"   Language: {latest['language']}")
        print(f"   Dubbed URL: {latest.get('dubbed_video_url', 'N/A')[:50]}...")
        print(f"   Status: {latest['status']}")
        if latest.get('translated_text'):
            print(f"   Translated text preview: {latest['translated_text'][:100]}...")
    else:
        print("   ⚠️  No translations found yet")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 3. Check local output folder
print("\n3️⃣ Checking Local Output Folder...")
output_dir = r"d:\project-1\SIH-fresh\VaaniPath-Localizer\localizer\output"
try:
    if os.path.exists(output_dir):
        folders = [d for d in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir, d))]
        print(f"   Folders in output: {len(folders)}")
        if len(folders) == 0:
            print("   ✅ Clean! Auto-cleanup is working")
        else:
            print(f"   ⚠️  {len(folders)} folders still present")
            print(f"   Recent: {folders[:3]}")
    else:
        print("   ⚠️  Output directory doesn't exist")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 4. Check Cloudinary uploads
print("\n4️⃣ Checking Cloudinary Integration...")
try:
    videos = supabase.table("videos").select("file_url, cloudinary_public_id").order("created_at", desc=True).limit(3).execute()
    if videos.data:
        cloudinary_count = sum(1 for v in videos.data if v.get('cloudinary_public_id'))
        print(f"   Videos with Cloudinary: {cloudinary_count}/{len(videos.data)}")
        if cloudinary_count > 0:
            print("   ✅ Cloudinary integration working")
        else:
            print("   ⚠️  No Cloudinary uploads found")
    else:
        print("   ⚠️  No videos found")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("✅ Verification Complete!")
print("=" * 60)
print("\n💡 To test the full flow:")
print("   1. Login as teacher: http://localhost:8080/login")
print("   2. Upload a small video (1-2 min)")
print("   3. Request dubbing to Hindi")
print("   4. Run this script again to verify")
print("=" * 60)
