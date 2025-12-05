# Course-Based Architecture - Database Migration

## SQL Migration Required

Aapko yeh SQL script run karna hoga Supabase SQL Editor mein:

**File Location:** `migrations/001_create_courses_and_enrollments.sql`

### Steps to Run Migration:

1. Open Supabase Dashboard: https://supabase.com/dashboard
2. Apna project select karein
3. Left sidebar se **SQL Editor** open karein
4. **New Query** click karein
5. `migrations/001_create_courses_and_enrollments.sql` file ke saare content copy karein
6. SQL Editor mein paste karein
7. **Run** button click karein

### What This Migration Does:

✅ **Creates `courses` table** - Teacher ke courses store karega
✅ **Creates `enrollments` table** - Student enrollments aur progress track karega
✅ **Adds `course_id` to `videos` table** - Videos ko courses ke saath link karega
✅ **Adds `order` column to `videos`** - Videos ki ordering karega  
✅ **Creates indexes** - Better performance ke liye
✅ **Sets up RLS policies** - Security ke liye

### Important Notes:

⚠️ Existing videos mein `course_id` NULL hoga (backward compatibility ke liye)
⚠️ Aapko existing videos ko courses mein migrate karna hoga
⚠️ Backend server automatically reload hoga after you save the new files

### After Migration:

Backend APIs available honge:
- `POST /api/v1/courses` - Create course
- `GET /api/v1/courses` - Get all courses
- `GET /api/v1/courses/my` - Get teacher's courses
- `GET /api/v1/courses/{id}` - Get course details
- `PUT /api/v1/courses/{id}` - Update course
- `DELETE /api/v1/courses/{id}` - Delete course
- `POST /api/v1/enrollments/{course_id}` - Enroll in course
- `GET /api/v1/enrollments/my` - Get my enrollments
- `PUT /api/v1/enrollments/{course_id}/progress` - Update progress

## Next Steps:

Main ab frontend components banaaunga:
1. CreateCourse page (teacher)
2. CourseManagement page (teacher)
3. BrowseCourses page (student)
4. MyCourses page (student) 
5. CoursePlayer page (student)
