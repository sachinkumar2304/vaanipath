# Localizer API – India Languages Quick Start

This project localizes training videos across India’s 22 scheduled languages. It supports dynamic voice seeding (Edge TTS), pronunciation overrides, sector glossaries, and job/person roles. The `/upload` endpoint provides a simple, one-call workflow.

## Supported Languages

Base codes: `as`, `bn`, `brx`, `doi`, `gu`, `hi`, `kn`, `ks`, `kok`, `mai`, `ml`, `mni`, `mr`, `ne`, `or`, `pa`, `sa`, `sat`, `sd`, `ta`, `te`, `ur`

Locales (Edge TTS where available): `hi-IN`, `bn-IN`, `ta-IN`, `te-IN`, `mr-IN`, `gu-IN`, `pa-IN`, `kn-IN`, `ml-IN`, `or-IN`, `ur-IN`.

If a specific locale voice is not available, the system falls back to a base code for gTTS.

## Prepare Voices

- Seed voices dynamically for India: `POST /voice/seed/india?gender=male` (or `female`).
- Set a specific voice: `PUT /voice/{lang}` with `{ "voice": "<edge-voice-id>" }`.

## Pronunciation Overrides

- Single file: `localizer/sample_data/pronunciation_overrides.json`
- Keys use base codes (`hi`, `bn`, `ta`, etc.). Locale variants inherit base automatically.
- Add domain-specific pronunciations per language for consistent TTS.

## Glossaries

- Sector glossaries in `localizer/sample_data/glossaries/`:
  - `automotive.json`, `healthcare.json`, `construction.json`, `retail.json`, `hospitality.json`, plus new `agriculture.json`, `banking.json`, `education.json`.
  - Roles glossary: `roles.json` for job roles and person titles.
- Language-specific glossaries: `localizer/sample_data/glossaries/lang/<lang>.json` (e.g., `sa.json`, `bho.json`) to enforce canonical target terminology.
- The RAG context merges base terms + roles + selected sector glossary + target language glossary.

## Upload Endpoint Usage

Endpoint: `POST /upload` (alias to `POST /upload_and_localize`)

Multipart form fields:
- `file`: video file (e.g., `localizer/sample_data/input.mp4`)
- `source`: source language (e.g., `en`)
- `target`: target language or locale (`hi-IN`, `bn-IN`, `ta-IN`, etc.)
- `course_id`: glossary name (e.g., `automotive`, `banking`, `education`)
- `job_id`: optional job name for tracking
- `mode`: `fast` or `accurate`
- `voice`: optional (`male`, `female`, or explicit Edge voice ID)

Workflow:
1. Seed voices: `POST /voice/seed/india?gender=male`
2. Upload: `POST /upload` with fields above
3. Check: `GET /jobs/{job_id}/stats`
4. Captions: `GET /captions/{job_id}?format=vtt`
5. Feedback: `POST /feedback` (optional)

## Examples

Hindi automotive:
```
curl -F file=@localizer/sample_data/input.mp4 \
     -F source=en -F target=hi-IN -F course_id=automotive \
     -F job_id=demo_hi -F mode=fast http://127.0.0.1:8000/upload
```

Tamil healthcare:
```
curl -F file=@localizer/sample_data/input.mp4 \
     -F source=en -F target=ta-IN -F course_id=healthcare \
     -F job_id=demo_ta -F mode=fast http://127.0.0.1:8000/upload
```

Assamese education (base-code fallback):
```
curl -F file=@localizer/sample_data/input.mp4 \
     -F source=en -F target=as -F course_id=education \
     -F job_id=demo_as -F mode=fast http://127.0.0.1:8000/upload
```

## Notes

- Edge TTS voices are discovered dynamically and cached; gTTS fallback uses base code if locale voices are missing.
- Pronunciation overrides file is language-wide. Add or refine entries as needed.
- Sector glossaries bias key terminology; roles glossary ensures consistent job titles.
