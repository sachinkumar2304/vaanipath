Sample data for localization demos: glossaries, voice map, and assets.

Languages
- Supported targets via Edge TTS/gTTS: `hi-IN`, `bn-IN`, `ta-IN`, `te-IN`, `mr-IN`, `gu-IN`, `pa-IN`, `kn-IN`, `ml-IN`, `or-IN`, `ur-IN`, plus base codes (`hi`, `bn`, `ta`, etc.). Others of India’s 22 scheduled languages use gTTS or fallback behavior.
- Use `POST /voice/seed/india?gender=male|female` to auto-provision voices for available Indian locales.

Files
- `voice_map.json`: per-language voice preferences. `PUT /voice/{lang}` updates it.
- `pronunciation_overrides.json`: language-aware overrides applied before TTS. Keys are base codes (`hi`, `bn`, `ta`...), locale variants inherit base.
- `glossaries/`: sector files like `automotive.json`, `healthcare.json`, `construction.json`, `retail.json`, `hospitality.json`, plus `roles.json` for job/person roles and `general.json` for vocational basics.
- `glossaries/lang/`: per-target language canonical term maps (e.g., `sa.json` for Sanskrit, `bho.json` for Bhojpuri). These bias LLM/Gemini translations to preferred terminology.
- `input.mp4`: sample input for quick runs.

Quick Start
1) Seed Indian voices: `POST /voice/seed/india?gender=male`
2) Upload and localize: `POST /upload` (multipart form)
   - `file`: video file
   - `source`: source language (e.g., `en`)
   - `target`: target language (`hi-IN`, `ta-IN`, `bn-IN`, etc.)
   - `course_id`: glossary file name without `.json` (e.g., `automotive`)
   - `job_id`: optional job name
   - `mode`: `fast` or `accurate`
   - `voice`: optional (`male`, `female`, or explicit voice ID)
3) Check stats: `GET /jobs/{job_id}/stats`
4) Download captions: `GET /captions/{job_id}?format=vtt`
5) Submit feedback: `POST /feedback`

Examples (curl)
- Hindi (hi-IN) automotive:
  `curl -F file=@localizer/sample_data/input.mp4 -F source=en -F target=hi-IN -F course_id=automotive -F job_id=demo_hi -F mode=fast http://127.0.0.1:8000/upload`
- Tamil (ta-IN) healthcare:
  `curl -F file=@localizer/sample_data/input.mp4 -F source=en -F target=ta-IN -F course_id=healthcare -F job_id=demo_ta -F mode=fast http://127.0.0.1:8000/upload`

Notes
- If a locale voice is not available, Edge TTS falls back; if unavailable, gTTS uses base language code automatically.
- Add terms to any glossary file to bias translations/transcripts for your domain.
