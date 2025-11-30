# Localizer Pipeline

## Overview
The **Localizer** package provides a full end‑to‑end pipeline for multilingual video localization:
1. **Video splitting** into overlapping chunks.
2. **Speech‑to‑text** (STT) for each chunk.
3. **Glossary‑based cleaning** of the transcript.
4. **Translation** (with optional LLM fallback).
5. **Cultural adaptation** of the translated text.
6. **Text‑to‑speech** (TTS) generation for each chunk.
7. **Global audio synchronization** – all TTS chunks are concatenated and time‑stretched once to match the original video duration.
8. **Final merge** – the synchronized audio is merged back with the original video.

## Installation
```bash
# Clone the repository
git clone https://github.com/Zaidusyy/VaaniPath-Localizer.git
cd VaaniPath-Localizer/localizer

# Install dependencies (Python 3.10+ recommended)
python -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage (CLI)
```bash
python -m localizer.app \
    --input path/to/input.mp4 \
    --source en \
    --target mr \
    --job demo_job \
    --course_id demo_course \
    --mode fast
```
- `--input` – path to the source video.
- `--source` – source language code (e.g., `en`).
- `--target` – target language code (e.g., `mr` for Marathi).
- `--job` – unique identifier for the job; a folder will be created under `localizer/output/`.
- `--course_id` – optional identifier for grouping jobs.
- `--mode` – processing mode (`fast` or `accurate`).

The command creates:
- `output/<job_id>/chunks/` – raw video/audio chunks.
- `output/<job_id>/tts/` – per‑chunk TTS audio and SRT files.
- `output/<job_id>/manifest.json` – job metadata.
- `output/<job_id>/final_audio.wav` – globally synchronized audio.
- `output/<job_id>/final_video.mp4` – final localized video.

## Demo Script
A ready‑to‑run demo is provided in `demo_test.py`. It localizes `demo-input.mp4` from English to Marathi and validates that the output video duration matches the source.

## Development
- **Code structure** – core logic lives in `localizer/` modules (`audio_sync.py`, `audio_utils.py`, `manifest.py`, etc.).
- **Extensibility** – you can replace the STT, translation, or TTS back‑ends by editing the corresponding modules.
- **Testing** – run `pytest` to execute the existing test suite.

## License
MIT License – see `LICENSE` file.
