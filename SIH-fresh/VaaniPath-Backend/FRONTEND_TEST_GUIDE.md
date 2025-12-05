# 🎯 Frontend Connection Testing Guide

## ✅ Backend Status: READY FOR TESTING!

**Server Running:** http://127.0.0.1:8000 ✅  
**API Docs:** http://127.0.0.1:8000/docs ✅  
**Mock Responses:** Enabled (Supabase not configured yet) ✅

---

## 🚀 Frontend Connection Steps

### **Step 1: Update Frontend API URL**

```typescript
// In your frontend .env or config file
const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

// Or in vite config
VITE_API_URL=http://127.0.0.1:8000/api/v1
```

### **Step 2: Test Endpoints with Frontend**

All endpoints return **proper JSON structure** even without database!

---

## 📋 Testable Endpoints (100% Ready)

### **1. Authentication (/api/v1/auth)**

#### **Signup:**
```typescript
// POST http://127.0.0.1:8000/api/v1/auth/signup
fetch(`${API_BASE_URL}/auth/signup`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'test@example.com',
    password: 'password123',
    full_name: 'Test User',
    is_admin: false
  })
})
.then(res => res.json())
.then(data => console.log(data));

// Expected Response (Mock):
{
  "id": "uuid-here",
  "email": "test@example.com",
  "full_name": "Test User",
  "is_admin": false,
  "created_at": "2025-11-17T...",
  "message": "Database not configured - mock response"
}
```

#### **Login:**
```typescript
// POST http://127.0.0.1:8000/api/v1/auth/login
fetch(`${API_BASE_URL}/auth/login`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'test@example.com',
    password: 'any-password'  // Any password works in mock mode
  })
})
.then(res => res.json())
.then(data => {
  // Save token
  localStorage.setItem('token', data.access_token);
  console.log('Token:', data.access_token);
});

// Expected Response (Mock):
{
  "access_token": "eyJ...",  // Valid JWT token!
  "token_type": "bearer"
}
```

#### **Get Current User:**
```typescript
// GET http://127.0.0.1:8000/api/v1/auth/me
const token = localStorage.getItem('token');

fetch(`${API_BASE_URL}/auth/me`, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
.then(res => res.json())
.then(data => console.log('User:', data));

// Expected Response:
{
  "user_id": "uuid-here",
  "email": "user@example.com",
  "full_name": "User Name",
  "is_admin": false
}
```

---

### **2. Videos (/api/v1/videos)**

#### **List Videos:**
```typescript
// GET http://127.0.0.1:8000/api/v1/videos/
fetch(`${API_BASE_URL}/videos/`)
  .then(res => res.json())
  .then(data => console.log('Videos:', data));

// Expected Response (Mock):
{
  "videos": [],  // Empty array (no DB yet)
  "total": 0,
  "page": 1,
  "page_size": 20
}
```

#### **Get Video Details:**
```typescript
// GET http://127.0.0.1:8000/api/v1/videos/{video_id}
fetch(`${API_BASE_URL}/videos/test-id`)
  .then(res => res.json())
  .then(data => console.log(data));

// Expected Response (Mock):
{
  "id": "test-id",
  "title": "Mock Video",
  "description": "Test video for frontend",
  "status": "completed",
  "domain": "IT",
  "duration": 600,
  "file_url": "https://example.com/video.mp4"
}
```

#### **Upload Video (Teacher):**
```typescript
// POST http://127.0.0.1:8000/api/v1/videos/upload
const formData = new FormData();
formData.append('file', videoFile);
formData.append('title', 'My Video');
formData.append('description', 'Video description');
formData.append('domain', 'IT');

const token = localStorage.getItem('token');

fetch(`${API_BASE_URL}/videos/upload`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
})
.then(res => res.json())
.then(data => console.log('Upload response:', data));

// Expected Response (Mock):
{
  "message": "Upload endpoint ready - R2 credentials needed",
  "video_id": "new-uuid",
  "status": "pending"
}
```

#### **Enroll in Video:**
```typescript
// POST http://127.0.0.1:8000/api/v1/videos/{video_id}/enroll
const token = localStorage.getItem('token');

fetch(`${API_BASE_URL}/videos/test-id/enroll`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
.then(res => res.json())
.then(data => console.log('Enrolled:', data));

// Expected Response (Mock):
{
  "message": "Enrolled successfully",
  "video_id": "test-id",
  "enrolled_at": "2025-11-17T..."
}
```

---

### **3. Translation (/api/v1/translation)**

#### **Start Translation:**
```typescript
// POST http://127.0.0.1:8000/api/v1/translation/start
const token = localStorage.getItem('token');

fetch(`${API_BASE_URL}/translation/start`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    video_id: 'test-video-id',
    target_languages: ['hi', 'ta', 'te']
  })
})
.then(res => res.json())
.then(data => console.log('Translation started:', data));

// Expected Response (Mock):
{
  "job_id": "job-uuid",
  "status": "queued",
  "video_id": "test-video-id",
  "languages": ["hi", "ta", "te"]
}
```

#### **Check Translation Status:**
```typescript
// GET http://127.0.0.1:8000/api/v1/translation/{job_id}/status
fetch(`${API_BASE_URL}/translation/job-id/status`)
  .then(res => res.json())
  .then(data => console.log('Status:', data));

// Expected Response (Mock):
{
  "job_id": "job-id",
  "status": "processing",
  "progress": 50,
  "current_step": "translation"
}
```

---

### **4. Quiz (/api/v1/quiz)**

#### **Start Quiz:**
```typescript
// POST http://127.0.0.1:8000/api/v1/quiz/start/{video_id}
const token = localStorage.getItem('token');

fetch(`${API_BASE_URL}/quiz/start/test-video-id`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
.then(res => res.json())
.then(data => console.log('Quiz:', data));

// Expected Response (Mock):
{
  "session_id": "session-uuid",
  "questions": [
    {
      "id": "q1",
      "question": "Sample question?",
      "options": ["A", "B", "C", "D"],
      "type": "mcq"
    }
  ],
  "total_questions": 5
}
```

#### **Submit Answer:**
```typescript
// POST http://127.0.0.1:8000/api/v1/quiz/answer
const token = localStorage.getItem('token');

fetch(`${API_BASE_URL}/quiz/answer`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    session_id: 'session-uuid',
    question_id: 'q1',
    selected_option: 'A'
  })
})
.then(res => res.json())
.then(data => console.log('Answer result:', data));

// Expected Response (Mock):
{
  "correct": true,
  "explanation": "Correct answer explanation"
}
```

---

### **5. Admin (/api/v1/admin)**

#### **Get Admin Stats:**
```typescript
// GET http://127.0.0.1:8000/api/v1/admin/stats
const token = localStorage.getItem('token');

fetch(`${API_BASE_URL}/admin/stats`, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
.then(res => res.json())
.then(data => console.log('Stats:', data));

// Expected Response (Mock):
{
  "total_videos": 0,
  "videos_by_status": {
    "completed": 0,
    "processing": 0,
    "failed": 0
  },
  "total_users": 1,
  "storage_usage_mb": 0,
  "popular_languages": ["hi", "ta", "te"]
}
```

#### **List All Users:**
```typescript
// GET http://127.0.0.1:8000/api/v1/admin/users
const token = localStorage.getItem('token');

fetch(`${API_BASE_URL}/admin/users`, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
.then(res => res.json())
.then(data => console.log('Users:', data));

// Expected Response (Mock):
{
  "users": [
    {
      "id": "user-id",
      "email": "admin@example.com",
      "full_name": "Admin User",
      "is_admin": true
    }
  ],
  "total": 1
}
```

---

## 🧪 Complete Frontend Test Flow

### **Full User Journey Test:**

```typescript
// 1. Signup
const signupResponse = await fetch(`${API_BASE_URL}/auth/signup`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'student@test.com',
    password: 'pass123',
    full_name: 'Test Student',
    is_admin: false
  })
});
const user = await signupResponse.json();
console.log('✅ Signup:', user);

// 2. Login
const loginResponse = await fetch(`${API_BASE_URL}/auth/login`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'student@test.com',
    password: 'pass123'
  })
});
const { access_token } = await loginResponse.json();
localStorage.setItem('token', access_token);
console.log('✅ Login: Token saved');

// 3. Get current user
const meResponse = await fetch(`${API_BASE_URL}/auth/me`, {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const currentUser = await meResponse.json();
console.log('✅ Current user:', currentUser);

// 4. List videos
const videosResponse = await fetch(`${API_BASE_URL}/videos/`);
const videos = await videosResponse.json();
console.log('✅ Videos:', videos);

// 5. Enroll in video
const enrollResponse = await fetch(`${API_BASE_URL}/videos/test-id/enroll`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const enrollment = await enrollResponse.json();
console.log('✅ Enrolled:', enrollment);

// All endpoints working! ✅
```

---

## ✅ What's Working NOW:

1. **Authentication** ✅
   - Signup returns mock user
   - Login returns valid JWT token
   - Token validation works
   - Get current user works

2. **Videos** ✅
   - List videos (returns empty)
   - Get video details (returns mock)
   - Upload endpoint ready
   - Enroll endpoint ready

3. **Translation** ✅
   - Start translation (mock job)
   - Check status (mock progress)

4. **Quiz** ✅
   - Start quiz session
   - Submit answers
   - Get results

5. **Admin** ✅
   - Get statistics
   - List users
   - Manage permissions

---

## ⏳ What Needs Database (Coming Tomorrow):

1. **Real User Data**
   - After Supabase setup
   - Real login/signup
   - Persistent user accounts

2. **Real Videos**
   - After R2 setup
   - Actual file upload
   - Video storage

3. **Real Quiz Data**
   - Database-backed questions
   - Score tracking

---

## 🎯 Testing Checklist for Frontend:

```
✅ Connect to backend API
✅ Test CORS (should work automatically)
✅ Test signup endpoint
✅ Test login endpoint
✅ Test JWT token storage
✅ Test authenticated requests
✅ Test video list endpoint
✅ Test video details endpoint
✅ Test enrollment endpoint
✅ Test admin endpoints
✅ Verify response formats match TypeScript interfaces
✅ Check error handling (try invalid requests)
```

---

## 📞 How to Test Right Now:

### **Option 1: Use Browser DevTools**

```javascript
// Open browser console on frontend
// Run these commands:

const API = 'http://127.0.0.1:8000/api/v1';

// Test login
fetch(`${API}/auth/login`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'test@test.com',
    password: 'test'
  })
})
.then(r => r.json())
.then(console.log);
```

### **Option 2: Use Postman/Thunder Client**

1. Import these endpoints
2. Test each one
3. Verify response structure

### **Option 3: Integrate with React Frontend**

Update your frontend code with API calls above!

---

## 🚀 Next Steps:

**TODAY:**
- ✅ Backend running
- ✅ Frontend connect karo
- ✅ Test all endpoints
- ✅ Verify response structures

**TOMORROW:**
- ⏳ Setup Supabase (15 min)
- ⏳ Setup R2 (15 min)
- ✅ Real data working!

---

## ✅ ANSWER: Frontend Connect AABHI KARO!

**Kab?** RIGHT NOW! ✅

**Kya kaam karega?**
- All endpoint structures ✅
- JWT authentication ✅
- Request/response formats ✅
- Error handling ✅

**Kya nahi karega?**
- Real data storage ❌ (kal hoga)
- Actual video upload ❌ (kal hoga)
- Persistent login ❌ (kal hoga)

**But testing perfect hai!** 💯

---

**Bhai, frontend run karo aur test karo! Server ready hai! 🚀**
