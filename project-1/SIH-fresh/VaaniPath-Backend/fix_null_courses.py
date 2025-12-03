"""
Fix courses with NULL title and teacher_id
"""
from app.db.supabase_client import supabase

print("=" * 60)
print("🔍 Checking Courses with NULL values")
print("=" * 60)

# Get all courses
response = supabase.table("courses").select("*").execute()

print(f"\nTotal courses: {len(response.data)}")

# Find courses with NULL title or teacher_id
null_courses = []
for course in response.data:
    if not course.get('title') or not course.get('teacher_id'):
        null_courses.append(course)
        print(f"\n❌ Course ID: {course['id']}")
        print(f"   Title: {course.get('title', 'NULL')}")
        print(f"   Teacher ID: {course.get('teacher_id', 'NULL')}")
        print(f"   Created: {course.get('created_at', 'N/A')}")

if null_courses:
    print(f"\n⚠️  Found {len(null_courses)} courses with NULL values")
    print("\n🔧 Fixing...")
    
    for course in null_courses:
        course_id = course['id']
        
        # Set default values
        update_data = {}
        
        if not course.get('title'):
            update_data['title'] = f"Untitled Course {course_id[:8]}"
        
        if not course.get('teacher_id'):
            # Get first teacher from users table
            teachers = supabase.table("users").select("id").eq("is_teacher", True).limit(1).execute()
            if teachers.data:
                update_data['teacher_id'] = teachers.data[0]['id']
            else:
                # Get any user
                users = supabase.table("users").select("id").limit(1).execute()
                if users.data:
                    update_data['teacher_id'] = users.data[0]['id']
        
        if update_data:
            supabase.table("courses").update(update_data).eq("id", course_id).execute()
            print(f"   ✅ Fixed course {course_id[:8]}")
    
    print("\n✅ All courses fixed!")
else:
    print("\n✅ No courses with NULL values found")

print("\n" + "=" * 60)
print("Verification:")
print("=" * 60)

# Verify
response = supabase.table("courses").select("id, title, teacher_id").execute()
print(f"\nAll courses now:")
for course in response.data:
    print(f"  - {course['title'][:30]} (Teacher: {course['teacher_id'][:8]}...)")
