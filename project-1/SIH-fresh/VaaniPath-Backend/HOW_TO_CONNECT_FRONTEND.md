# 🔗 Frontend-Backend Connection - Step by Step (Bilkul Simple!)

## 🎯 Current Situation:

```
Tere paas 2 folders hain:

1. D:\backend\          ← Backend (FastAPI) - Yahan tu hai ✅
2. Frontend repo        ← React/TypeScript - Alag folder me hai
```

**Goal:** Dono ko connect karna hai! 💪

---

## 📋 Option 1: Sabse Easy Method (Recommended for Testing)

### **Frontend aur Backend ALAG folders me rakhna - Best for Development!**

```
D:\
├── backend\           ← Backend folder (current)
│   ├── app/
│   ├── venv/
│   └── ...
│
├── frontend\          ← Frontend folder (clone karenge)
│   ├── src/
│   ├── package.json
│   └── ...
```

### **Step 1: Frontend Clone Karo (D:\ drive pe)**

```powershell
# Backend folder se bahar aao
cd D:\

# Frontend clone karo
git clone https://github.com/sachinkumar2304/Gyanify.git frontend

# Ab folder structure:
# D:\backend\  ✅
# D:\frontend\ ✅
```

### **Step 2: Frontend Setup Karo**

```powershell
# Frontend folder me jao
cd D:\frontend

# Dependencies install karo
npm install
# Ya agar pnpm use karte ho:
pnpm install
```

### **Step 3: Frontend me Backend URL Add Karo**

#### **Option A: .env file banao (Best method)**

```powershell
# Frontend folder me .env file banao
cd D:\frontend

# Create .env file
notepad .env
```

**.env file me add karo:**
```env
VITE_API_URL=http://127.0.0.1:8000/api/v1
```

Save kar do (Ctrl+S)!

#### **Option B: Code me directly change karo**

Frontend ke code me jahan API calls hain, wahan URL update karo:

**Pehle (Probably):**
```typescript
const API_URL = "/api";  // Ya kuch aur
```

**Ab (Update karo):**
```typescript
const API_URL = "http://127.0.0.1:8000/api/v1";
```

**Files check karo:**
- `src/config.ts` (agar hai)
- `src/utils/api.ts` (agar hai)
- `src/services/` folder ke files
- Components me direct fetch calls

### **Step 4: Dono Servers Start Karo**

#### **Terminal 1: Backend (Already running!)**

Backend terminal me server already chal raha hai:
```
✅ http://127.0.0.1:8000
```

Agar nahi chal raha to:
```powershell
cd D:\backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

#### **Terminal 2: Frontend (New terminal)**

Naya terminal kholo:
```powershell
cd D:\frontend
npm run dev
# Ya
pnpm dev
```

Frontend start hoga on:
```
✅ http://localhost:5173
```

### **Step 5: Test Karo Browser Me**

1. Browser me jao: `http://localhost:5173`
2. Login/Signup try karo
3. Browser console kholo (F12)
4. Network tab dekho - API calls dikhengi! ✅

---

## 🔧 Connection Test (5 Minutes)

### **Quick Test - Browser Console Me Run Karo:**

```javascript
// Browser console me (F12 > Console)

// Test backend connection
fetch('http://127.0.0.1:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'test@test.com',
    password: 'test123'
  })
})
.then(r => r.json())
.then(data => console.log('✅ Connected! Token:', data.access_token))
.catch(err => console.error('❌ Error:', err));
```

**Agar "✅ Connected!" dikha = Working!** 🎉

---

## 🚨 Common Problems & Solutions

### **Problem 1: CORS Error**

```
Access to fetch at 'http://127.0.0.1:8000' from origin 'http://localhost:5173' 
has been blocked by CORS policy
```

**Solution:** Backend me already fix hai! ✅

Agar phir bhi error aaye to check karo `app/main.py`:

```python
# Ye code hona chahiye:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **Problem 2: Connection Refused**

```
Failed to fetch
net::ERR_CONNECTION_REFUSED
```

**Solution:** Backend server start karo!

```powershell
cd D:\backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

### **Problem 3: 404 Not Found**

**Check karo URL sahi hai:**
```
✅ http://127.0.0.1:8000/api/v1/auth/login  (Sahi)
❌ http://127.0.0.1:8000/auth/login         (Galat - /api/v1 missing)
```

---

## 📦 Option 2: Push Karne Se Pehle (Optional)

### **Agar Team Ke Saath Work Kar Rahe Ho:**

**Step 1: Backend Push Karo GitHub Pe**

```powershell
cd D:\backend

# Initialize git (agar nahi kiya)
git init

# Add all files
git add .

# Commit
git commit -m "Backend setup complete - Ready for frontend connection"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/sachinkumar2304/gyanify-backend.git

# Push
git branch -M main
git push -u origin main
```

**Step 2: Frontend Team Ko Batao**

```markdown
Backend running at: http://127.0.0.1:8000/api/v1

Update your frontend .env:
VITE_API_URL=http://127.0.0.1:8000/api/v1

Test endpoint:
curl http://127.0.0.1:8000/api/v1/auth/login
```

---

## 🎯 Recommended Workflow (Best Practice)

### **Workflow 1: Both Running Locally (For Solo Testing)**

```
1. Backend: http://127.0.0.1:8000
2. Frontend: http://localhost:5173
3. Test everything locally ✅
4. Then push both to GitHub ✅
```

### **Workflow 2: Backend Deployed (For Team)**

```
1. Deploy backend to Railway/Render
2. Update frontend .env with deployed URL
3. Team can test without running backend locally
```

**Abhi ke liye: Workflow 1 use karo!** ✅

---

## 🔥 Complete Setup Commands (Copy-Paste)

### **Terminal 1 - Backend:**

```powershell
# Backend start karo
cd D:\backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload

# Server running: ✅ http://127.0.0.1:8000
```

### **Terminal 2 - Frontend Setup:**

```powershell
# Frontend clone karo (agar nahi kiya)
cd D:\
git clone https://github.com/sachinkumar2304/Gyanify.git frontend

# Setup
cd frontend
npm install

# .env file banao
echo VITE_API_URL=http://127.0.0.1:8000/api/v1 > .env

# Start frontend
npm run dev

# Frontend running: ✅ http://localhost:5173
```

### **Browser:**

```
Open: http://localhost:5173
Try login/signup
Check browser console (F12)
```

---

## ✅ Checklist - Kya Kya Karna Hai:

```
Phase 1: Setup (10 min)
□ Frontend clone karo D:\frontend me
□ npm install karo
□ .env file banao with VITE_API_URL

Phase 2: Start Servers (2 min)
□ Backend start karo (already running!)
□ Frontend start karo (npm run dev)

Phase 3: Test (5 min)
□ Browser me frontend kholo
□ Login try karo
□ Console me check karo API calls
□ Network tab check karo

Phase 4: Push (Optional)
□ Backend push karo GitHub
□ Frontend update karo if needed
□ Document API URL for team
```

---

## 🎓 Simple Explanation

**Think of it like this:**

```
Frontend = Customer (React app in browser)
Backend = Restaurant (FastAPI server)

Connection = Phone call between them!

Frontend says: "Bhai login karwao!"
Backend replies: "Lo token le lo!"

Both are different programs:
- Frontend: Runs in browser (localhost:5173)
- Backend: Runs in terminal (127.0.0.1:8000)

They talk through HTTP requests! 📞
```

---

## 🚀 TL;DR - Bas Ye 4 Commands Run Karo:

```powershell
# 1. Frontend clone (agar nahi kiya)
cd D:\
git clone https://github.com/sachinkumar2304/Gyanify.git frontend

# 2. Frontend setup
cd frontend
npm install
echo VITE_API_URL=http://127.0.0.1:8000/api/v1 > .env

# 3. Frontend start
npm run dev

# 4. Test browser me
# Open: http://localhost:5173
```

**Backend already running hai!** ✅

---

## ❓ Abhi Kya Karu?

### **Option A: Test Locally (Recommended)**

```
1. Frontend clone karo
2. npm install
3. .env add karo
4. npm run dev
5. Test karo browser me
✅ Done in 15 minutes!
```

### **Option B: Push First, Test Later**

```
1. Backend push karo GitHub
2. Team ko link bhejo
3. Baad me connect karenge
⏳ Takes longer
```

**Mera suggestion: Option A - Pehle test karo!** 💯

---

## 📞 Need Help? Debug Steps:

**Agar kuch kaam nahi kar raha:**

```powershell
# Check 1: Backend running?
curl http://127.0.0.1:8000/api/v1/health
# Should return: {"status": "healthy"}

# Check 2: Frontend running?
# Browser me http://localhost:5173 kholo

# Check 3: .env file sahi hai?
cd D:\frontend
type .env
# Should show: VITE_API_URL=http://127.0.0.1:8000/api/v1

# Check 4: CORS error?
# Browser console (F12) me check karo
```

---

**Bhai, tension mat le! Bas frontend clone kar, npm install kar, aur run kar de! Backend already ready hai! 💪🔥**

**Koi problem aaye to bata, fix kar dunga!** ✅
