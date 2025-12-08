"""
Check teacher_id in courses table
"""
from app.db.supabase_client import supabase

# Get all courses
courses = supabase.table("courses").select("id, title, teacher_id, tutor_id").execute()

print("=== COURSES IN DATABASE ===")
for course in courses.data:
    print(f"\nCourse: {course['title']}")
    print(f"  ID: {course['id']}")
    print(f"  teacher_id: {course.get('teacher_id')}")
    print(f"  tutor_id: {course.get('tutor_id')}")

# Get all teachers
teachers = supabase.table("users").select("id, full_name, email, is_teacher").eq("is_teacher", True).execute()

print("\n\n=== TEACHERS IN DATABASE ===")
for teacher in teachers.data:
    print(f"\nTeacher: {teacher['full_name']}")
    print(f"  ID: {teacher['id']}")
    print(f"  Email: {teacher['email']}")
