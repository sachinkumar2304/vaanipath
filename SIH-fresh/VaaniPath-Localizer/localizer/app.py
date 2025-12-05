import argparse
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Dict, Any, List
import subprocess
from .config import CHUNK_LENGTH_SECONDS, CHUNK_OVERLAP_SECONDS, MODE_CONFIG, TRANSLATION_DEFAULT_MODEL
from .utils import mkdir_p, setup_logger, get_worker_count, FFMPEG, FFPROBE
from .video_splitter import split_video
from .stt import transcribe
from .glossary import DEFAULT_GLOSSARY, merge_glossaries, clean_transcript
from .translation import translate_text

# Only Konkani (Generic) requires Gemini as Google Translate doesn't support it
# All other Indian languages now use Google Translate (as of 2024)
GEMINI_PREFERRED_LANGS = {"kok"}  # Konkani (Generic)
from .culture import apply_cultural_adaptation
from .tts import tts_synthesize, generate_srt
from .manifest import build_manifest, load_manifest
from .rag_client import get_job_context
from .audio_sync import concatenate_and_stretch
from pathlib import Path
from .audio_utils import get_duration
from .cloudinary_uploader import upload_video_to_cloudinary as cloudinary_upload




logger = setup_logger("app")


def process_chunk(
    chunk_meta: Dict[str, Any],
    source_lang: str,
    target_lang: str,
    mode: str,
    job_context: Dict[str, Any],
    tts_dir: str,
    translation_model: str,
) -> Dict[str, Any]:
    audio_path = chunk_meta["audio_path"]

    # 1) STT
    text_original, segments = transcribe(
        audio_path=audio_path,
        source_lang=source_lang,
        initial_prompt=job_context.get("initial_prompt"),
        mode=mode,
    )

    # 2) Glossary cleanup
    merged_glossary = merge_glossaries(DEFAULT_GLOSSARY, job_context.get("glossary", {}))
    text_clean = clean_transcript(text_original, merged_glossary)

    # 3) Translation
    text_translated = translate_text(
        text_clean,
        target_lang,
        model=translation_model,
        style_guide=job_context.get("style_guide"),
        glossary=job_context.get("target_glossary"),
    )

    # 4) Cultural adaptation
    text_adapted = apply_cultural_adaptation(text_translated, target_lang, job_context.get("cultural_rules", {}))

    # 5) TTS + SRT
    audio_out = os.path.join(tts_dir, f"chunk_{chunk_meta['index']:04d}.mp3")
    srt_out = os.path.join(tts_dir, f"chunk_{chunk_meta['index']:04d}.srt")
    tts_synthesize(text_adapted, target_lang, audio_out)
    generate_srt(segments, srt_out)

    # Keep only raw TTS generation, remove time stretching
    final_audio_path = audio_out

    return {
        "index": chunk_meta["index"],
        "start": chunk_meta["start"],
        "end": chunk_meta["end"],
        "text_original": text_original,
        "text_translated": text_adapted,
        "audio_path": final_audio_path,
        "srt_path": srt_out,
    }

# Gemini-preferred languages that should use single-pass processing
GEMINI_PREFERRED_LANGS = {"brx", "doi", "ks", "gom", "mai", "mni", "sat", "mwr", "bho", "bgc"}


def process_full_video(
    input_path: str,
    source: str,
    target: str,
    job_id: str,
    course_id: str,
    mode: str,
    translation_model: str,
    base_out: str,
) -> tuple[str, str, List[Dict[str, Any]]]:
    """Process entire video without chunking (for Gemini languages).
    
    Returns: (final_audio_path, final_video_path, chunks_metadata)
    """
    tts_dir = os.path.join(base_out, "tts")
    mkdir_p(tts_dir)
    
    job_context = get_job_context(course_id, source, target)
    logger.info("Job context loaded (single-pass mode).")
    
    # Extract audio from full video
    audio_path = os.path.join(base_out, "full_audio.wav")
    extract_cmd = [
        FFMPEG, "-y", "-i", input_path,
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
        audio_path
    ]
    subprocess.check_call(extract_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    logger.info(f"Extracted full audio: {audio_path}")
    
    # STT on full audio
    text_original, segments = transcribe(
        audio_path=audio_path,
        source_lang=source,
        initial_prompt=job_context.get("initial_prompt"),
        mode=mode,
    )
    logger.info(f"Transcribed full audio: {len(text_original)} chars")
    
    # Glossary cleanup
    merged_glossary = merge_glossaries(DEFAULT_GLOSSARY, job_context.get("glossary", {}))
    text_clean = clean_transcript(text_original, merged_glossary)
    
    # Single Gemini translation call
    text_translated = translate_text(
        text_clean,
        target,
        model=translation_model,
        style_guide=job_context.get("style_guide"),
        glossary=job_context.get("target_glossary"),
    )
    logger.info(f"Translated via Gemini: {len(text_translated)} chars")
    
    # Cultural adaptation
    text_adapted = apply_cultural_adaptation(text_translated, target, job_context.get("cultural_rules", {}))
    
    # TTS + SRT for full content
    audio_out = os.path.join(tts_dir, "full_audio.mp3")
    srt_out = os.path.join(tts_dir, "full_audio.srt")
    tts_synthesize(text_adapted, target, audio_out)
    generate_srt(segments, srt_out)
    logger.info(f"Generated TTS: {audio_out}")
    
    # Time-stretch to match video duration
    video_duration = get_duration(input_path)
    final_audio_path = os.path.join(base_out, "final_audio.wav")
    
    # Use time_stretch_audio from audio_utils
    from .audio_utils import time_stretch_audio
    time_stretch_audio(audio_out, video_duration, final_audio_path)
    
    # Merge with video (if input is video)
    final_video_path = os.path.join(base_out, "final_video.mp4")
    # Note: Merging happens in run_job usually, but here we just return paths
    # Actually, for single-pass, we might want to return the stretched audio as final result
    
    chunks_metadata = [{
        "index": 0,
        "start": 0.0,
        "end": video_duration,
        "text_original": text_original,
        "text_translated": text_adapted,
        "audio_path": final_audio_path,
        "srt_path": srt_out,
    }]
    
    return str(final_audio_path), str(final_video_path), chunks_metadata


def run_job(
    input_path: str,
    source: str,
    target: str,
    job_id: str,
    course_id: str,
    mode: str = "fast",
    translation_model: str = TRANSLATION_DEFAULT_MODEL,
) -> str:
    start_time = time.time()
    base_out = os.path.join(os.path.dirname(__file__), "output", job_id)
    mkdir_p(base_out)
    
    # Check if target language requires Gemini (single-pass processing)
    base_target = target.split("-")[0]
    if base_target in GEMINI_PREFERRED_LANGS:
        logger.info(f"Language {target} requires Gemini - using single-pass processing")
        final_audio, final_video, chunks_metadata = process_full_video(
            input_path, source, target, job_id, course_id, mode, translation_model, base_out
        )
        
        # Upload to Cloudinary
        cloudinary_url = None
        try:
            # Determine content type (audio or video)
            content_type = "audio"  # Default for single-pass as we skip video merge usually
            upload_path = final_audio
            
            # If we had video merging, we would check if final_video exists
            if final_video and os.path.exists(final_video):
                content_type = "video"
                upload_path = final_video
                
            if upload_path and os.path.exists(upload_path):
                logger.info(f"Uploading {content_type} to Cloudinary: {upload_path}")
                result = cloudinary_upload(
                    upload_path,
                    job_id,
                    target,
                    content_type=content_type
                )
                if result:
                    cloudinary_url = result  # cloudinary_upload returns URL string directly
                    logger.info(f"Cloudinary URL ({content_type}): {cloudinary_url}")
                else:
                    logger.error("Cloudinary upload returned no result")
            else:
                logger.error(f"Upload path does not exist: {upload_path}")
        except Exception as e:
            logger.error(f"Cloudinary upload failed: {e}")
        
        # Build manifest
        manifest = build_manifest(
            job_id=job_id,
            mode=mode,
            source=source,
            target=target,
            course_id=course_id,
            input_path=input_path,
            chunks=chunks_metadata,
            output_dir=base_out,
            final_audio=final_audio,
            final_video=final_video,
            cloudinary_url=cloudinary_url,
        )
        
        elapsed = time.time() - start_time
        logger.info(f"Job {job_id} finished (single-pass): chunks=1 mode={mode} time={elapsed:.2f}s")
        return os.path.join(base_out, "manifest.json")
    
    # Standard chunked processing for non-Gemini languages
    chunks_dir = os.path.join(base_out, "chunks")
    mkdir_p(chunks_dir)
    tts_dir = os.path.join(base_out, "tts")
    mkdir_p(tts_dir)

    job_context = get_job_context(course_id, source, target)
    logger.info("Job context loaded.")

    # Split video
    chunk_meta_list = split_video(
        input_path=input_path,
        output_dir=chunks_dir,
        chunk_length=CHUNK_LENGTH_SECONDS,
        overlap=CHUNK_OVERLAP_SECONDS,
    )

    # Process chunks in parallel
    results: List[Dict[str, Any]] = []
    workers = get_worker_count()
    logger.info(f"Processing {len(chunk_meta_list)} chunks with {workers} workers")
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(
                process_chunk,
                meta,
                source,
                target,
                mode,
                job_context,
                tts_dir,
                translation_model,
            ): meta["index"]
            for meta in chunk_meta_list
        }
        for fut in as_completed(futures):
            try:
                res = fut.result()
                results.append(res)
            except Exception as e:
                logger.error(f"Chunk processing failed: {e}")

    # Sort results by chunk index
    results.sort(key=lambda x: x["index"]) 
    
    # Global audio synchronization
    video_duration = get_duration(input_path)
    audio_paths = [Path(r["audio_path"]) for r in results]
    final_audio_path = Path(base_out) / "final_audio.wav"
    
    if not audio_paths:
        logger.error("No audio chunks generated! Skipping audio sync.")
        # Create a dummy silent audio or just fail gracefully?
        # For now, let's raise an error but with a better message, or return early
        raise RuntimeError("Localization failed: No audio chunks were generated.")
        
    concatenate_and_stretch(audio_paths, video_duration, final_audio_path)

    # 🎵 Detect if input is audio-only (no video stream)
    def has_video_stream(file_path: str) -> bool:
        """Check if file has video stream using ffprobe"""
        cmd = [
            FFPROBE,
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=codec_type",
            "-of", "default=noprint_wrappers=1:nokey=1",
            file_path
        ]
        try:
            out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            return b"video" in out.lower()
        except:
            return False

    is_audio_only = not has_video_stream(input_path)
    
    if is_audio_only:
        # 🎵 Audio-only: Upload final audio directly
        logger.info("📻 Detected audio-only input, skipping video merge")
        from .cloudinary_uploader import upload_video_to_cloudinary
        cloudinary_url = upload_video_to_cloudinary(
            file_path=str(final_audio_path),
            video_id=job_id,
            language=target,
            content_type='audio'  # 🎵 Upload as audio
        )
        logger.info(f"📤 Cloudinary URL (audio): {cloudinary_url}")
        
        manifest = build_manifest(
            job_id=job_id,
            mode=mode,
            source=source,
            target=target,
            course_id=course_id,
            input_path=input_path,
            chunks=results,
            output_dir=base_out,
            final_audio=str(final_audio_path),
            final_video=None,  # No video for audio-only
            cloudinary_url=cloudinary_url,
        )
    else:
        # 🎬 Video: Merge audio with video
        logger.info("🎬 Detected video input, merging audio with video")
        final_video_path = Path(base_out) / "final_video.mp4"
        merge_cmd = [
            FFMPEG,
            "-y",
            "-i",
            input_path,
            "-i",
            str(final_audio_path),
            "-c:v",
            "copy",
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-shortest",
            str(final_video_path),
        ]
        subprocess.check_call(merge_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

        # 🚀 Upload to Cloudinary and get URL
        from .cloudinary_uploader import upload_video_to_cloudinary
        cloudinary_url = upload_video_to_cloudinary(
            file_path=str(final_video_path),
            video_id=job_id,
            language=target,
            content_type='video'
        )
        logger.info(f"📤 Cloudinary URL (video): {cloudinary_url}")

        manifest = build_manifest(
            job_id=job_id,
            mode=mode,
            source=source,
            target=target,
            course_id=course_id,
            input_path=input_path,
            chunks=results,
            output_dir=base_out,
            final_audio=str(final_audio_path),
            final_video=str(final_video_path),
            cloudinary_url=cloudinary_url,  # 🚀 Store Cloudinary URL in manifest
        )

    elapsed = time.time() - start_time
    logger.info(
        f"Job {job_id} finished: chunks={len(results)} mode={mode} time={elapsed:.2f}s"
    )
    return os.path.join(base_out, "manifest.json")


def _manifest_path(job_id: str) -> str:
    return os.path.join(os.path.dirname(__file__), "output", job_id, "manifest.json")


def get_manifest(job_id: str) -> Dict[str, Any]:
    path = _manifest_path(job_id)
    return load_manifest(path)


def list_chunks(job_id: str) -> List[Dict[str, Any]]:
    m = get_manifest(job_id)
    return m.get("chunks", [])


def get_chunk_detail(job_id: str, chunk_index: int) -> Dict[str, Any]:
    m = get_manifest(job_id)
    for c in m.get("chunks", []):
        if int(c.get("index", -1)) == int(chunk_index):
            return c
    raise ValueError(f"Chunk {chunk_index} not found in job {job_id}")


def reprocess_chunk(job_id: str, chunk_index: int, target_lang: str, mode: str = "fast") -> Dict[str, Any]:
    m = get_manifest(job_id)
    source = m.get("source_lang", "en")
    course_id = m.get("course_id", "")
    job_context = get_job_context(course_id, source, target_lang)

    # Locate original chunk audio
    base_out = os.path.join(os.path.dirname(__file__), "output", job_id)
    tts_dir = os.path.join(base_out, "tts")
    chunks_dir = os.path.join(base_out, "chunks")
    meta = None
    for c in m.get("chunks", []):
        if int(c.get("index", -1)) == int(chunk_index):
            meta = c
            break
    if meta is None:
        # Fallback: rebuild meta from chunks dir
        audio_path = os.path.join(chunks_dir, f"chunk_{int(chunk_index):04d}.wav")
        # Start/end unknown here; set to 0
        meta = {"index": int(chunk_index), "start": 0.0, "end": 0.0, "audio_path": audio_path}

    # Re-run processing
    res = process_chunk(
        chunk_meta={"index": int(chunk_index), "start": meta.get("start", 0.0), "end": meta.get("end", 0.0), "audio_path": os.path.join(chunks_dir, f"chunk_{int(chunk_index):04d}.wav")},
        source_lang=source,
        target_lang=target_lang,
        mode=mode,
        job_context=job_context,
        tts_dir=tts_dir,
        translation_model=TRANSLATION_DEFAULT_MODEL,
    )

    # Update manifest in place
    for i, c in enumerate(m.get("chunks", [])):
        if int(c.get("index", -1)) == int(chunk_index):
            m["chunks"][i] = res
            break
    with open(_manifest_path(job_id), "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=2)
    return res


def get_job_stats(job_id: str) -> Dict[str, Any]:
    m = get_manifest(job_id)
    chunks = m.get("chunks", [])
    return {
        "job_id": job_id,
        "chunk_count": len(chunks),
        "mode": m.get("mode"),
        "source_lang": m.get("source_lang"),
        "target_lang": m.get("target_lang"),
    }


def main():
    parser = argparse.ArgumentParser(description="Localizer - multilingual video localization engine")
    parser.add_argument("--input", required=True, help="Path to input video file")
    parser.add_argument("--source", required=True, help="Source language code (e.g., en)")
    parser.add_argument("--target", required=True, help="Target language code (e.g., hi)")
    parser.add_argument("--job", dest="job_id", required=True, help="Job ID")
    parser.add_argument("--course_id", required=True, help="Course identifier")
    parser.add_argument("--mode", choices=list(MODE_CONFIG.keys()), default="fast")

    args = parser.parse_args()
    manifest_path = run_job(
        input_path=args.input,
        source=args.source,
        target=args.target,
        job_id=args.job_id,
        course_id=args.course_id,
        mode=args.mode,
    )
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
