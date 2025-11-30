# 🎓 Gyanify - AI-Powered Multilingual Content Localization Engine

> Smart India Hackathon 2025 - Problem Statement #25203

## 📋 Overview

Gyanify is an AI-powered multilingual content localization engine designed for skill courses. It translates vocational training materials (video, audio, text) into 22+ Indian languages with domain-specific accuracy, cultural adaptation, and lip-sync capabilities.

## ✨ Features

- 🎬 **Video Localization**: Automatic translation of training videos
- 🗣️ **Speech-to-Text**: Whisper-powered ASR for accurate transcription
- 🌏 **22+ Indian Languages**: Support for all major Indian languages
- 📚 **Domain-Specific Glossaries**: IT, Healthcare, Construction, etc.
- 🎯 **Cultural Adaptation**: Region-specific examples and context
- 🎵 **Text-to-Speech**: Natural-sounding voice generation
- 💋 **Lip Sync**: Audio-video synchronization
- 🎮 **Gamification**: Quiz generation during processing
- 👥 **Review System**: Human-in-the-loop for quality assurance
- 📊 **Quality Metrics**: Automated quality scoring

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework
- **Supabase**: Database and storage
- **Redis**: Task queue and caching
- **Celery**: Background job processing

### AI/ML
- **Whisper**: Speech-to-text (OpenAI)
- **IndicTrans2**: Indian language translation
- **Coqui TTS**: Text-to-speech synthesis
- **spaCy**: NLP and domain detection
- **FastText**: Word embeddings

### Video/Audio
- **FFmpeg**: Video/audio processing
- **MoviePy**: Python video editing
- **aeneas**: Subtitle alignment

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── api/                 # API endpoints
│   │   └── v1/
│   │       ├── endpoints/   # Route handlers
│   │       └── router.py    # API router
│   ├── core/                # Core utilities
│   │   └── security.py      # Auth & security
│   ├── db/                  # Database clients
│   │   ├── supabase_client.py
│   │   └── redis_client.py
│   ├── models/              # Pydantic models
│   ├── schemas/             # Database schemas
│   ├── services/            # Business logic
│   ├── workers/             # Celery tasks
│   └── utils/               # Helper functions
├── models/                  # ML model files
├── glossaries/             # Domain glossaries
├── storage/                # Local storage
├── tests/                  # Unit tests
└── requirements.txt        # Dependencies
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Redis
- FFmpeg
- GPU (recommended) or CPU

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1  # Windows
   # source venv/bin/activate     # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

5. **Setup Supabase**
   - Create a new project on [Supabase](https://supabase.com)
   - Run the SQL in `app/schemas/tables.sql` in Supabase SQL Editor
   - Copy project URL and keys to `.env`

6. **Install Redis** (Windows)
   ```bash
   # Download Redis from GitHub
   # Or use Docker:
   docker run -d -p 6379:6379 redis
   ```

7. **Run the application**
   ```bash
   python -m app.main
   ```

   The API will be available at `http://localhost:8000`

8. **Start Celery worker** (in new terminal)
   ```bash
   celery -A app.workers.tasks worker --loglevel=info
   ```

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔑 API Endpoints

### Authentication
- `POST /api/v1/auth/signup` - Register new user
- `POST /api/v1/auth/login` - Login and get token
- `GET /api/v1/auth/me` - Get current user

### Videos
- `POST /api/v1/videos/upload` - Upload video (Admin)
- `GET /api/v1/videos/` - List all videos
- `GET /api/v1/videos/{id}` - Get video details
- `GET /api/v1/videos/{id}/progress` - Get processing progress

### Translation
- `POST /api/v1/translation/start` - Start translation job
- `GET /api/v1/translation/{job_id}/status` - Get job status
- `GET /api/v1/translation/{job_id}/quality` - Get quality metrics

### Quiz
- `GET /api/v1/quiz/video/{id}/questions` - Get quiz questions
- `POST /api/v1/quiz/start/{video_id}` - Start quiz session
- `POST /api/v1/quiz/answer` - Submit answer

### Review
- `GET /api/v1/review/pending` - Get pending reviews
- `POST /api/v1/review/submit` - Submit review

### Admin
- `GET /api/v1/admin/stats` - Get dashboard stats
- `GET /api/v1/admin/users` - List all users
- `GET /api/v1/admin/jobs/active` - Get active jobs

## 🧪 Testing

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

## 🎯 Development Roadmap

### Week 1: Core Setup ✅
- [x] FastAPI structure
- [x] Database schema
- [x] Authentication
- [x] Basic endpoints

### Week 2: Video Processing
- [ ] Video upload & storage
- [ ] Whisper ASR integration
- [ ] IndicTrans2 translation
- [ ] Celery task queue

### Week 3: Advanced Features
- [ ] TTS integration
- [ ] Lip sync processing
- [ ] Cultural adaptation
- [ ] Glossary system

### Week 4: Polish & Deploy
- [ ] Review system
- [ ] Quality metrics
- [ ] Gamification
- [ ] Testing & deployment

## 🤝 Team

- **Backend & ML**: [Your Name]
- **Frontend**: [Team Members]
- **Design**: [Team Members]

## 📝 License

This project is developed for Smart India Hackathon 2025.

## 🙏 Acknowledgments

- NCVET & MSDE for the problem statement
- AI4Bharat for Indic language models
- OpenAI for Whisper
- Coqui for TTS models

## 📞 Contact

For queries, contact: [your-email@example.com]

---

**Built with ❤️ for Smart India Hackathon 2025**
