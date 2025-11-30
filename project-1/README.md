# VaaniPath - Multilingual Education Platform

A comprehensive multilingual education platform supporting 22 Indian languages with real-time dubbing and translation features.

## Quick Setup

### Prerequisites
- Node.js 18+ (for Frontend)
- Python 3.12+ (for Backend)
- Supabase account
- Cloudinary account

### Required Downloads

**FFmpeg (Required for Localizer)**

The ffmpeg binaries are not included in this repository due to file size limits. Download separately:

1. Download FFmpeg essentials build: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
2. Extract to `VaaniPath-Localizer/ffmpeg-8.0.1-essentials_build/`
3. Ensure `bin/ffmpeg.exe` exists in the path

### Installation

**Frontend:**
```bash
cd SIH-fresh/VaaniPath-Frontend
npm install
npm run dev
```

**Backend:**
```bash
cd SIH-fresh/VaaniPath-Backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Localizer:**
```bash
cd SIH-fresh/VaaniPath-Localizer
pip install -r requirements.txt
uvicorn localizer.api:app --reload --port 8001
```

### Environment Variables

Create `.env` files in each directory:

**Backend & Localizer:**
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`

## Features

- 🌐 Support for 22 Indian languages
- 🎥 Real-time video dubbing
- 📚 Course management for teachers
- 📊 Student progress tracking
- 🔊 Audio translation
- 📄 Document translation

## Tech Stack

- **Frontend:** React, TypeScript, TailwindCSS, ShadCN UI
- **Backend:** FastAPI, Supabase, Cloudinary
- **Localizer:** FastAPI, FFmpeg, AI Translation APIs
