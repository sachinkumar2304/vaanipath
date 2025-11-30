# 💾 Storage Solution - Cloudflare R2 for Gyanify

## ❌ **Problem with Supabase:**

**Free Tier:**
- Storage: 500MB only
- Database: 500MB

**30-min video calculation:**
```
1 video (30 min, 720p) = ~500MB
Original + Translated (3 languages) = 500MB × 4 = 2GB

1 video hi nahi fit hoga! ❌
10-15 videos = 20-30GB needed 😱
```

**Paid Tier:**
- $25/month for 100GB
- Not feasible for development/demo ❌

---

## ✅ **SOLUTION: Cloudflare R2 Storage**

### **Chosen Architecture:**

```
Database (Supabase):
- User data ✅
- Video metadata ✅
- Translations text ✅
- Quiz data ✅
Total: <50MB ✅

File Storage (Cloudflare R2):
- Videos (original + translated) 
- Audio files
- Subtitles
Total: 10GB free, then $0.015/GB ✅
```

**Data Flow:**
```
Frontend
    ↓
Backend (FastAPI)
    ↓
Database (Supabase) → Metadata only
    ↓
Storage (Cloudflare R2) → Actual files
```

**Benefits:**
- ✅ **10GB FREE** storage
- ✅ Unlimited bandwidth (no egress fees!)
- ✅ S3-compatible (easy integration)
- ✅ Global CDN (fast access)
- ✅ Production-ready from day 1
- ✅ Cheap scaling ($1.50 for 100GB)

---

### **Cloudflare R2 - Perfect for SIH**

**Free Tier:**
- Storage: 10GB FREE
- Bandwidth: Unlimited FREE
- Requests: 1M read, 1M write FREE per month

**Cost After Free:**
- Storage: $0.015/GB/month
- 100GB = $1.50/month (very cheap!)
- Bandwidth: Always FREE! ✅

**Comparison:**
| Service | Free Storage | Bandwidth | Cost/GB |
|---------|--------------|-----------|---------|
| Supabase | 500MB | 50GB | $0.021 |
| AWS S3 | None | $0.09/GB | $0.023 |
| **Cloudflare R2** | **10GB** | **FREE** | **$0.015** |

**Winner: Cloudflare R2** ✅

---

### **Option 3: Google Cloud Storage (Education)**

**For Students:**
- $300 credit FREE
- Can use for 3 months
- Good for SIH finals

**But:**
- Needs credit card
- Expires after trial

---

##  **RECOMMENDED SETUP:**

### **Development, Demo & Production (Single Solution):**
```
Storage: Cloudflare R2 (S3-compatible)
Database: Supabase
```

**Why:**
- ✅ Production-ready from day 1
- ✅ No migration needed later
- ✅ 10GB free (enough for 3-5 demo videos)
- ✅ Delete test videos to reuse space
- ✅ Same config for dev + production

---

##  **Cloudflare R2 Setup**

See `R2_SETUP_GUIDE.md` for complete step-by-step setup.

**Quick Setup:**

1. Create Cloudflare account (free)
2. Enable R2 in dashboard
3. Create bucket: `gyanify-videos`
4. Generate API tokens
5. Add credentials to `.env`:

```dotenv
STORAGE_TYPE=cloudflare_r2
R2_ACCOUNT_ID=your_account_id
R2_ACCESS_KEY_ID=your_access_key_id
R2_SECRET_ACCESS_KEY=your_secret_key
R2_BUCKET_NAME=gyanify-videos
```

### **Backend Integration:**

Already implemented in `app/storage/r2_client.py`:

```python
from app.storage.r2_client import r2_client

# Upload
url = r2_client.upload_file(
    file_data=video_file,
    object_name="videos/abc123.mp4",
    content_type="video/mp4"
)

# Download
r2_client.download_file("videos/abc123.mp4", "local/path.mp4")

# Delete
r2_client.delete_file("videos/abc123.mp4")

# Check exists
exists = r2_client.file_exists("videos/abc123.mp4")
```

---

## 📊 **Storage Calculation for SIH:**

### **Demo Requirement:**
- 3-5 sample videos (10 min each)
- 3 languages per video
- Total: 9-15 translated videos

**Size:**
```
1 video (10 min, 720p) = ~200MB
5 original videos = 1GB
15 translated videos = 3GB
Intermediate files = 500MB
Total = 4.5GB

Cloudflare R2 Free Tier: 10GB ✅
Completely within free tier! ✅
```

**Test Videos:**
```
During development:
- Use 4-5 min short videos (~100MB each)
- Test processing pipeline
- Delete after testing
- Reuse storage space ✅
```

---

## 🎯 **Final Recommendation:**

### **For SIH (Development + Demo):**

```yaml
Database: Supabase (Free)
  - Users
**Use Cloudflare R2 from Day 1:**

```yaml
Database: Supabase
  - User accounts
  - Video metadata
  - Glossary
  - Quiz data

Storage: Cloudflare R2
  - Original videos
  - Translated videos
  - Audio files
  - Subtitles

Why:
  - Production-ready ✅
  - 10GB free ✅
  - No migration ✅
  - Global CDN ✅
  - Delete tests = reuse space ✅
```

---

## 🔄 **Architecture:**

```
┌─────────────────────────────────────────┐
│  Frontend (Vercel/Netlify free)        │
│  - Upload interface                     │
│  - Video player                         │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  FastAPI Backend (Railway/Render free)  │
│  - API endpoints                        │
│  - File handling                        │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
┌──────▼──────┐  ┌──────▼──────────────┐
│  Supabase   │  │  Cloudflare R2      │
│  (Database) │  │  (File Storage)     │
│  - Metadata │  │  - Videos           │
│  - Users    │  │  - Audio            │
│  - Glossary │  │  - Subtitles        │
└─────────────┘  └─────────────────────┘
```

---

## 💡 **Decision Matrix:**

| Criteria | Supabase Only | Cloudflare R2 |
|----------|---------------|---------------|
| **Cost** | ❌ Limited | ✅ Cheap |
| **Storage** | ❌ 500MB | ✅ 10GB free |
| **Speed** | ✅ Fast | ✅ Fast + CDN |
| **Demo** | ❌ Won't work | ✅ Perfect |
| **Setup** | ✅ Easy | 🔄 Medium |
| **Production** | ❌ Expensive | ✅ Production-ready |
| **Bandwidth** | 🔄 Limited | ✅ Unlimited FREE |

**Winner: Cloudflare R2!** 🏆

---

## 🚀 **Implementation Plan:**

### **Setup (Today/Tomorrow):**
1. ✅ Setup Supabase (database only)
2. ✅ Create Cloudflare R2 bucket
3. ✅ Configure backend (already done!)

### **Testing:**
1. Test file upload to R2
2. Store metadata in Supabase
3. Video playback from R2 CDN

### **Benefits:**
- No storage worries ✅
- Fast development ✅
- Production-ready from day 1 ✅
- Perfect for demo ✅

---

## 📝 **Environment Config:**

```bash
# Database (Supabase)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_key

# Storage (Cloudflare R2)
STORAGE_TYPE=cloudflare_r2
R2_ACCOUNT_ID=your_account_id
R2_ACCESS_KEY_ID=your_access_key
R2_SECRET_ACCESS_KEY=your_secret
R2_BUCKET_NAME=gyanify-videos
R2_ENDPOINT_URL=https://your_account.r2.cloudflarestorage.com
R2_PUBLIC_URL=https://your-bucket.r2.dev
```

**See `R2_SETUP_GUIDE.md` for complete setup instructions!**

---

## ✅ **Final Answer:**

**DON'T use Supabase for video storage!**

**USE:**
- **Cloudflare R2** for all file storage → 10GB free, production-ready
- **Supabase** only for database → metadata, users, quiz, etc.

**Benefits:**
- ✅ Single storage solution (dev + production)
- ✅ No migration needed
- ✅ 10GB free tier
- ✅ Delete test videos to reuse space
- ✅ Unlimited bandwidth (FREE!)
- ✅ Global CDN

**This is the BEST solution!** 💪🔥
