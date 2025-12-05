# VaaniPath Localizer - Project Technical Report

**Date:** November 24, 2025
**Project:** VaaniPath Localizer (formerly GyanifyTRAE)
**Repository:** https://github.com/Zaidusyy/VaaniPath-Localizer

---

## 1. Executive Summary
VaaniPath Localizer is an automated video localization pipeline designed to translate educational content into Indian languages. It handles the entire process: extracting audio, transcribing speech (STT), translating text, generating voiceovers (TTS), and synchronizing the new audio with the original video.

**Key Achievement:** The system now supports **22+ languages**, including regional dialects like Haryanvi, Bhojpuri, and Marwari, which are typically unsupported by standard tools.

---

## 2. System Architecture

The pipeline consists of 6 distinct stages:

1.  **Ingestion**: Receives video via REST API (`/upload`).
2.  **Preprocessing**: Extracts audio and splits video into manageable chunks (default 30s) for parallel processing.
3.  **Speech-to-Text (STT)**: Uses `faster-whisper` (OpenAI Whisper model) to transcribe audio to text with timestamps.
4.  **Translation**:
    *   **Primary**: Google Translate (via `deep-translator`).
    *   **Advanced/Regional**: Google Gemini (LLM) for languages requiring context or not supported by standard translation (e.g., Haryanvi, Marwari).
5.  **Text-to-Speech (TTS)**:
    *   **Primary**: Microsoft Edge TTS (high-quality neural voices).
    *   **Fallback**: Google TTS (`gTTS`) for unsupported languages.
    *   **Dialect Mapping**: Maps unsupported languages (e.g., Haryanvi) to the closest available phonetic match (e.g., Hindi) for TTS.
6.  **Synchronization & Merging**:
    *   **Global Sync**: Concatenates all audio segments and applies a single time-stretch factor to match the original video duration exactly, preventing "audio drift".
    *   **FFmpeg**: Merges the new audio track with the original video stream.

---

## 3. Key Technical Decisions & Trade-offs

This section highlights specific architectural choices and their implications (what might be considered "limitations" or "workarounds").

### A. Single-Pass vs. Chunked Processing
*   **The Decision**: For standard languages (Hindi, Tamil), we split video into 30s chunks and process in parallel. For LLM-based languages (Bhojpuri, Haryanvi), we process the **entire video in one pass**.
*   **Why?**
    *   **Chunking (Standard)**: Faster for long videos due to parallelism.
    *   **Single-Pass (LLM)**: LLMs like Gemini have rate limits and need context. Sending 30 small requests causes rate-limiting errors and inconsistent translations. Sending one large request ensures consistency and stays within API limits.
*   **Trade-off**: Single-pass processing requires more memory for very long videos (1hr+) since the entire transcript is loaded at once.

### B. TTS Fallback Strategy
*   **The Decision**: Since no TTS engine natively supports "Haryanvi" or "Bhojpuri", we map these to **Hindi** voices.
*   **Why?** It is better to have a Hindi-accented voiceover than no voiceover at all.
*   **Trade-off**: The accent will sound like standard Hindi, not the specific regional dialect. The *words* will be Haryanvi, but the *accent* will be Hindi.

### C. Global Audio Synchronization
*   **The Decision**: Instead of stretching each 30s audio chunk individually, we generate the full audio track and stretch it *once* to match the video length.
*   **Why?** Stretching small chunks accumulates rounding errors, causing the audio to drift out of sync by the end of the video. Global sync guarantees the start and end match perfectly.
*   **Trade-off**: If one specific sentence is much longer in the target language, the *entire* video speeds up slightly to compensate, rather than just that one section.

### D. Blocking vs. Non-Blocking Code
*   **The Decision**: The heavy video processing runs in a separate thread pool (`run_in_threadpool`) rather than the main async loop.
*   **Why?** Video processing is CPU-intensive. If run on the main loop, it would freeze the API, preventing status checks or new uploads.
*   **Trade-off**: Adds slight complexity to `api.py` but is essential for a responsive server.

---

## 4. Language Support Matrix

| Category | Languages | Translation Engine | TTS Engine |
| :--- | :--- | :--- | :--- |
| **Major Indian** | Hindi, Marathi, Tamil, Telugu, Bengali, Gujarati, Kannada, Malayalam, Punjabi | Google Translate | Edge TTS (Neural) |
| **Regional** | **Haryanvi (bgc)**, **Bhojpuri (bho)**, **Marwari (mwr)**, Bodo, Dogri, Kashmiri, Konkani, Maithili, Manipuri, Santali | **Google Gemini (LLM)** | **Fallback (Hindi/Urdu)** |
| **International** | English, Spanish, French, German, etc. | Google Translate | Edge TTS (Neural) |

---

## 5. Current Limitations (Areas for Improvement)

1.  **Gemini Dependency**: Regional languages *require* a valid `GEMINI_API_KEY`. Without it, they fail (gracefully, with an error message).
2.  **Voice Cloning**: Currently uses stock voices. Does not clone the original speaker's voice.
3.  **Lip Sync**: The system synchronizes *time*, but does not alter the video's lip movements (Wav2Lip is not integrated).
4.  **Memory Usage**: Single-pass processing for Gemini languages loads the full audio into memory. Extremely large files (e.g., 4GB+) might need server upgrades.

## 6. Conclusion
The system is production-ready for the specified use cases. It successfully solves the complex problem of localizing into low-resource languages (Haryanvi, Marwari) by leveraging LLMs and smart fallback strategies. The "Global Sync" mechanism ensures the final output is professional and watchable.
