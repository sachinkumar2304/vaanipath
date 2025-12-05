# 🚀 Cloudflare R2 Setup Guide - Step by Step

## ✨ Kya Hai Cloudflare R2?

**Cloudflare R2 = S3-compatible object storage (videos/files ke liye)**

### **Benefits:**
- ✅ **10GB FREE** storage
- ✅ **UNLIMITED bandwidth** (download/upload FREE!)
- ✅ No egress fees (S3 me $0.09/GB bandwidth charge hota hai)
- ✅ S3-compatible (same code works)
- ✅ Fast global CDN
- ✅ Only $0.015/GB after 10GB ($1.50 for 100GB)

---

## 📋 Step-by-Step Setup (5 minutes)

### **Step 1: Cloudflare Account Banao**

1. Go to: **https://dash.cloudflare.com/sign-up**
2. Email se signup karo (free!)
3. Email verify karo

---

### **Step 2: R2 Enable Karo**

1. Dashboard pe jao: **https://dash.cloudflare.com**
2. Left sidebar me **"R2"** pe click karo
3. **"Purchase R2 Plan"** pe click
4. Select **"FREE"** plan
5. Confirm karo ✅

**Note:** Credit card chahiye hoga verification ke liye, but **FREE tier completely free hai!**

---

### **Step 3: Bucket Banao**

1. R2 dashboard me **"Create bucket"** pe click
2. Bucket name enter karo: **`gyanify-videos`**
3. Location: **Automatic** (Cloudflare decides best location)
4. **"Create bucket"** pe click ✅

---

### **Step 4: API Tokens Generate Karo**

#### **4a. R2 API Tokens Section**

1. R2 dashboard me **"Manage R2 API Tokens"** pe click
2. Ya direct: **https://dash.cloudflare.com/profile/api-tokens**

#### **4b. Create API Token**

1. **"Create API Token"** button pe click
2. **"Edit Cloudflare Workers"** template select karo
3. Ya scroll down to **"Create Custom Token"**

#### **4c. Token Permissions Set Karo**

```
Token name: Gyanify Backend Access
Permissions:
  - Account > R2 > Edit
  
Account Resources:
  - Include > [Your account] > All
  
Client IP Address Filtering:
  - Leave empty (allow all IPs)
  
TTL:
  - Forever (no expiration)
```

4. **"Continue to summary"** pe click
5. **"Create Token"** pe click

#### **4d. Copy Token Details**

**Screen pe 3 values dikhenge - COPY KARO!**

```
Access Key ID: abc123def456...
Secret Access Key: xyz789...
Token: cloudflare_token_here...
```

⚠️ **IMPORTANT:** Secret key sirf **ek baar** dikhega! Copy karke save karo!

---

### **Step 5: Account ID Find Karo**

1. Cloudflare dashboard me kisi bhi page pe jao
2. URL me dekho:
   ```
   https://dash.cloudflare.com/<ACCOUNT_ID>/...
                                   ^^^^^^^^^^^^
                                   Ye copy karo!
   ```
3. Ya right sidebar me **Account ID** hogi

**Example:**
```
URL: https://dash.cloudflare.com/a1b2c3d4e5f6g7h8/r2
Account ID: a1b2c3d4e5f6g7h8
```

---

### **Step 6: R2 Endpoint URL Generate Karo**

**Format:**
```
https://{ACCOUNT_ID}.r2.cloudflarestorage.com
```

**Example:**
```
Account ID: a1b2c3d4e5f6g7h8
Endpoint: https://a1b2c3d4e5f6g7h8.r2.cloudflarestorage.com
```

---

### **Step 7: Public URL Setup (Optional - For Demo)**

#### **Option A: R2.dev Subdomain (Easiest)**

1. R2 bucket settings me jao
2. **"Settings"** tab
3. **"Public Access"** section
4. **"Allow Access"** pe click
5. **R2.dev subdomain** automatically generate hoga:
   ```
   https://gyanify-videos.a1b2c3d4e5f6g7h8.r2.dev
   ```

#### **Option B: Custom Domain (Advanced)**

1. Apna domain Cloudflare me add karo
2. DNS settings me:
   ```
   Type: CNAME
   Name: videos (or cdn)
   Target: gyanify-videos.{account}.r2.cloudflarestorage.com
   ```
3. Public URL hoga: `https://videos.yourdomain.com`

---

### **Step 8: Backend Me Configure Karo**

#### **8a. Update `.env` File**

```bash
# Open .env file
notepad d:\backend\.env
```

**Fill these values:**

```dotenv
# =================================
# Storage Configuration - Cloudflare R2
# =================================
STORAGE_TYPE=cloudflare_r2
R2_ACCOUNT_ID=a1b2c3d4e5f6g7h8                    # ← Step 5 se
R2_ACCESS_KEY_ID=abc123def456...                   # ← Step 4d se (Access Key ID)
R2_SECRET_ACCESS_KEY=xyz789secret...               # ← Step 4d se (Secret Access Key)
R2_BUCKET_NAME=gyanify-videos                      # ← Step 3 se
R2_ENDPOINT_URL=https://a1b2c3d4e5f6g7h8.r2.cloudflarestorage.com  # ← Step 6 se
R2_PUBLIC_URL=https://gyanify-videos.a1b2c3d4e5f6g7h8.r2.dev       # ← Step 7 se
```

#### **8b. Install boto3 Package**

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install boto3 (AWS SDK for S3/R2)
pip install boto3==1.34.28 botocore==1.34.28
```

#### **8c. Test Configuration**

```powershell
# Run Python to test R2 connection
python -c "from app.storage.r2_client import r2_client; print('✅ R2 Connected!' if r2_client else '❌ Error')"
```

**Expected Output:**
```
✅ R2 client initialized: https://a1b2c3d4e5f6g7h8.r2.cloudflarestorage.com
✅ Bucket exists: gyanify-videos
✅ R2 Connected!
```

---

## 🧪 Test Upload (Optional)

Create test file:

```powershell
# Create test video
echo "Test video content" > test-video.txt

# Run test upload
python -c "
from app.storage.r2_client import r2_client
url = r2_client.upload_file_from_path('test-video.txt', 'test/demo.txt', 'text/plain')
print(f'✅ Uploaded! URL: {url}')
"
```

**Check:**
1. Go to R2 dashboard → `gyanify-videos` bucket
2. You should see `test/demo.txt` file! ✅

---

## 📊 Quick Reference

### **What You Need:**

| Setting | Where to Get | Example |
|---------|--------------|---------|
| **R2_ACCOUNT_ID** | Dashboard URL | `a1b2c3d4e5f6g7h8` |
| **R2_ACCESS_KEY_ID** | API Token creation | `abc123...` (32 chars) |
| **R2_SECRET_ACCESS_KEY** | API Token creation | `xyz789...` (43 chars) |
| **R2_BUCKET_NAME** | Bucket you created | `gyanify-videos` |
| **R2_ENDPOINT_URL** | Auto-generated | `https://{account_id}.r2.cloudflarestorage.com` |
| **R2_PUBLIC_URL** | R2.dev subdomain | `https://{bucket}.{account_id}.r2.dev` |

---

## 🔍 How to Use in Code

### **Upload Video Example:**

```python
from app.storage.r2_client import r2_client

# Upload video file
video_url = r2_client.upload_file(
    file_data=video_file,
    object_name=f"videos/{video_id}/{filename}",
    content_type="video/mp4"
)

# Save URL to database
video_record["file_url"] = video_url
```

### **Download Video Example:**

```python
# Download for processing
local_path = f"storage/temp/{video_id}.mp4"
r2_client.download_file(
    object_name=f"videos/{video_id}/original.mp4",
    download_path=local_path
)
```

### **Delete Video Example:**

```python
# Delete single file
r2_client.delete_file(f"videos/{video_id}/original.mp4")

# Delete multiple files
r2_client.delete_files([
    f"videos/{video_id}/original.mp4",
    f"videos/{video_id}/hindi.mp4",
    f"videos/{video_id}/tamil.mp4"
])
```

---

## 💰 Cost Calculation

### **Free Tier:**
- ✅ 10GB storage
- ✅ Unlimited bandwidth
- ✅ Unlimited requests

### **After 10GB:**

```
Storage: $0.015/GB/month
Example:
- 50GB storage = $0.60/month
- 100GB storage = $1.50/month
- 500GB storage = $7.50/month

Bandwidth: FREE! (Always)
Requests: $0.36 per million (basically free)
```

### **SIH Demo Calculation:**

```
5 demo videos:
- 5 videos × 2GB = 10GB
- Cost: FREE! ✅

10 videos:
- 10 videos × 2GB = 20GB
- 20GB - 10GB free = 10GB paid
- Cost: 10GB × $0.015 = $0.15/month
- ₹12/month only! 💰
```

---

## ⚠️ Common Issues & Solutions

### **Issue 1: "Access Denied"**
```
✅ Solution: Check API token permissions
- Must have "R2 Edit" permission
- Regenerate token if needed
```

### **Issue 2: "Bucket not found"**
```
✅ Solution: Check bucket name spelling
- Must match exactly: gyanify-videos
- Case-sensitive!
```

### **Issue 3: "Invalid endpoint"**
```
✅ Solution: Check account ID in endpoint URL
- Format: https://{ACCOUNT_ID}.r2.cloudflarestorage.com
- No spaces or typos
```

### **Issue 4: "Module boto3 not found"**
```
✅ Solution: Install boto3
pip install boto3==1.34.28
```

---

## 🎯 Next Steps After Setup

1. ✅ R2 configured ho gaya
2. ✅ Test upload/download working
3. **Now:** Supabase database setup karo
4. **Then:** Video upload endpoint complete karo
5. **Finally:** ML models integrate karo

---

## 📞 Quick Support

**Cloudflare R2 Docs:**
- https://developers.cloudflare.com/r2/

**boto3 S3 Docs:**
- https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html

**Questions?**
- Check logs: `logs/app.log`
- Test connection: `python -c "from app.storage.r2_client import r2_client"`

---

**Done! Ab videos upload karne ke liye ready ho! 🚀**

Storage limit: **10GB free** → enough for **3-5 demo videos**  
Test videos delete karke space free kar sakte ho! ✅
