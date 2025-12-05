import os
import argparse
import subprocess
from typing import Dict
from pathlib import Path

from .manifest import load_manifest, build_manifest
from .tts import tts_synthesize, apply_pronunciation_overrides
from .utils import mkdir_p, setup_logger, FFMPEG
from .audio_sync import concatenate_and_stretch
from .audio_utils import get_duration

logger = setup_logger("resynthesize")


def resynthesize_job(manifest_path: str, output_dir: str | None = None) -> Dict:
    m = load_manifest(manifest_path)
    target_lang = m.get("target_lang", "hi")
    base_out = os.path.dirname(manifest_path)
    tts_dir = os.path.join(base_out, "tts")
    if output_dir:
        tts_out = output_dir
        mkdir_p(tts_out)
    else:
        tts_out = tts_dir

    updated = []
    # Re-generate TTS for all chunks (or specific ones if we tracked changes, but for now all)
    # Ideally we only regen changed ones, but 'resynthesize' implies full pass or we need logic.
    # The current code does full pass.
    for c in sorted(m.get("chunks", []), key=lambda x: x.get("index", 0)):
        text = c.get("text_translated", "")
        text_over = apply_pronunciation_overrides(text, target_lang)
        audio_out = os.path.join(tts_out, f"chunk_{int(c['index']):04d}.mp3")
        tts_synthesize(text_over, target_lang, audio_out)
        # Update audio path in chunk if it changed location
        c["audio_path"] = audio_out
        updated.append({"index": c["index"], "audio_path": audio_out})
    
    logger.info(f"Resynthesized {len(updated)} chunks to {tts_out}")
    return {"updated": updated, "tts_dir": tts_out, "manifest": m}


def finalize_resynthesis(manifest_path: str, manifest_data: Dict) -> str:
    """Re-run global sync and merge using updated TTS audio."""
    base_out = os.path.dirname(manifest_path)
    input_path = manifest_data.get("input_path")
    
    # 1. Global Sync
    video_duration = get_duration(input_path)
    chunks = sorted(manifest_data.get("chunks", []), key=lambda x: x["index"])
    audio_paths = [Path(c["audio_path"]) for c in chunks]
    
    final_audio_path = Path(base_out) / "final_audio_resynth.wav"
    concatenate_and_stretch(audio_paths, video_duration, final_audio_path)
    
    # 2. Merge
    final_video_path = Path(base_out) / "final_video_resynth.mp4"
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
    
    # 3. Update Manifest
    # We can either update the existing one or save a new one. 
    # Let's update the existing one to point to new final artifacts.
    manifest_data["final_audio"] = str(final_audio_path)
    manifest_data["final_video"] = str(final_video_path)
    
    # Use build_manifest to save (it handles mkdir etc)
    build_manifest(
        job_id=manifest_data.get("job_id"),
        mode=manifest_data.get("mode"),
        source=manifest_data.get("source_lang"),
        target=manifest_data.get("target_lang"),
        course_id=manifest_data.get("course_id"),
        input_path=input_path,
        chunks=chunks,
        output_dir=base_out,
        final_audio=str(final_audio_path),
        final_video=str(final_video_path)
    )
    
    return str(final_video_path)


def main():
    parser = argparse.ArgumentParser(description="Resynthesize TTS for a job with pronunciation overrides")
    parser.add_argument("--job", help="Job ID in localizer/output/<job>")
    parser.add_argument("--manifest", help="Path to manifest.json (overrides --job)")
    parser.add_argument("--out", help="Optional output TTS dir; defaults to job tts dir")
    parser.add_argument("--finalize", action="store_true", help="After resynth, finalize into a merged video")
    args = parser.parse_args()

    if args.manifest:
        manifest_path = args.manifest
    elif args.job:
        base = os.path.join("localizer", "output", args.job)
        manifest_path = os.path.join(base, "manifest.json")
    else:
        raise SystemExit("Provide --job or --manifest")

    res = resynthesize_job(manifest_path, args.out)
    print(f"Resynthesis complete. Updated {len(res['updated'])} chunks.")
    
    if args.finalize:
        final_video = finalize_resynthesis(manifest_path, res["manifest"])
        print(f"Finalized video: {final_video}")


if __name__ == "__main__":
    main()

