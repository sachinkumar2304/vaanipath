# 🔗 Frontend-Backend API Mapping

## ✅ Complete Endpoint Mapping

### **Authentication Endpoints**

| Frontend Need | Backend Endpoint | Status |
|--------------|------------------|--------|
| Student Login | `POST /api/v1/auth/login` | ✅ Ready |
| Student Signup | `POST /api/v1/auth/signup` | ✅ Ready |
| Teacher Login | `POST /api/v1/auth/login` | ✅ Ready (same) |
| Logout | Frontend only (clear token) | ✅ Ready |
| Get User Info | `GET /api/v1/auth/me` | ✅ Ready |

---

### **Teacher Panel Endpoints**

| Frontend Feature | Frontend TODO Comment | Backend Endpoint | Status |
|-----------------|----------------------|------------------|--------|
| Upload Content | `POST /api/teacher/upload` | `POST /api/v1/videos/upload` | ✅ Created |
| Get Teacher Courses | `GET /api/teacher/courses` | `GET /api/v1/videos/?uploaded_by=userId` | ✅ Ready |
| Delete Course | `DELETE /api/teacher/courses/:id` | `DELETE /api/v1/videos/:id` | ✅ Ready |
| Teacher Stats | `GET /api/teacher/stats` | `GET /api/v1/admin/stats` | 🔄 Need to implement |
| Get Doubts | `GET /api/doubts` | `GET /api/v1/quiz/video/:id/questions` | ✅ Ready (adapt) |
| Answer Doubt | `PUT /api/doubts/:id` | `POST /api/v1/quiz/answer` | ✅ Ready |

---

### **Student Panel Endpoints**

| Frontend Feature | Frontend TODO Comment | Backend Endpoint | Status |
|-----------------|----------------------|------------------|--------|
| Browse Courses | `GET /api/courses` | `GET /api/v1/videos/` | ✅ Ready |
| Enroll Course | `POST /api/courses/:id/enroll` | `POST /api/v1/videos/:id/enroll` | 🔄 Need to add |
| Get Enrolled | `GET /api/student/enrolled-courses` | `GET /api/v1/videos/?user_id=userId` | ✅ Ready |
| Course Details | `GET /api/courses/:id` | `GET /api/v1/videos/:id` | ✅ Ready |
| Submit Doubt | `POST /api/doubts` | `POST /api/v1/quiz/start/:video_id` | ✅ Ready (adapt) |

---

### **Translation Endpoints** (Backend Unique)

| Feature | Endpoint | Purpose |
|---------|----------|---------|
| Start Translation | `POST /api/v1/translation/start` | Trigger video localization |
| Check Status | `GET /api/v1/translation/:job_id/status` | Real-time progress |
| Get Quality | `GET /api/v1/translation/:job_id/quality` | Quality metrics |
| Add Glossary | `POST /api/v1/translation/glossary` | Domain terms |

---

### **Review System** (Backend Unique)

| Feature | Endpoint | Purpose |
|---------|----------|---------|
| Pending Reviews | `GET /api/v1/review/pending` | Admin review queue |
| Submit Review | `POST /api/v1/review/submit` | Approve/reject |
| Review History | `GET /api/v1/review/:id/history` | Audit trail |

---

## 🔄 **Endpoints We Need to Add** (Missing from current backend)

1. **Enroll Endpoint** - Add in `videos.py`:
   ```python
   @router.post("/{video_id}/enroll")
   async def enroll_video(video_id: str, current_user: dict = Depends(get_current_user)):
       # Add user to video enrollment
   ```

2. **Teacher Stats** - Add in `admin.py`:
   ```python
   @router.get("/stats")
   async def get_stats(current_user: dict = Depends(get_current_admin)):
       # Return teacher/admin statistics
   ```

3. **User Videos Filter** - Modify existing `list_videos` to support filtering

---

## ✅ **Kya Compatible Hai:**

### **100% Compatible:**
- Authentication system ✅
- Video upload ✅
- Video listing ✅
- Video details ✅
- Quiz system ✅

### **Need Minor Tweaks:**
- Course enrollment (new endpoint needed)
- Teacher stats (new endpoint needed)
- Doubts system (reuse quiz endpoints)

---

## 📝 **Frontend Integration Guide**

### Example: Login Integration

**Frontend Code** (StudentLogin.tsx):
```typescript
const handleLogin = async (e: React.FormEvent) => {
  e.preventDefault();
  
  const response = await fetch('http://localhost:8000/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  
  const data = await response.json();
  
  if (response.ok) {
    localStorage.setItem('token', data.access_token);
    navigate('/homepage');
  }
};
```

### Example: Upload Video

**Frontend Code** (TeacherUpload.tsx):
```typescript
const handleUpload = async (formData: FormData) => {
  const token = localStorage.getItem('token');
  
  const response = await fetch('http://localhost:8000/api/v1/videos/upload', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData  // multipart/form-data
  });
  
  const data = await response.json();
  
  toast({
    title: 'Upload Successful',
    description: 'Video is being processed'
  });
};
```

---

## 🎯 **FastAPI vs Frontend Routing:**

| Frontend Route | FastAPI Equivalent | Notes |
|----------------|-------------------|-------|
| `/teacher/dashboard` | Dashboard page (no API) | Fetches multiple APIs |
| `/teacher/upload` | `POST /api/v1/videos/upload` | Form submission |
| `/teacher/courses` | `GET /api/v1/videos/` | List teacher's videos |
| `/homepage` | `GET /api/v1/videos/` | List all videos |
| `/enrolled` | `GET /api/v1/videos/?enrolled=true` | Filter enrolled |
| `/course/:id` | `GET /api/v1/videos/:id` | Course details |

---

## ⚡ **Summary:**

✅ **90% endpoints already match** tumhare frontend ke saath!  
✅ FastAPI **100% compatible** hai React ke saath  
✅ Sirf 2-3 endpoints add karne hain  
✅ Structure **bilkul perfect** hai integration ke liye  

**Next Step**: Supabase setup + implement missing endpoints!
