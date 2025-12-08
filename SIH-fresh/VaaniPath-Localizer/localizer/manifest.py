import json
import os
from typing import Dict, List

from .utils import mkdir_p, setup_logger

logger = setup_logger("manifest")


def build_manifest(
    job_id: str,
    mode: str,
    source: str,
    target: str,
    course_id: str,
    input_path: str,
    chunks: List[Dict],
    output_dir: str,
    final_audio: str | None = None,
    final_video: str | None = None,
    cloudinary_url: str | None = None,  # 🚀 NEW: Cloudinary URL
    subtitle_url: str | None = None,    # 🚀 NEW: Subtitle URL
) -> Dict:
    """Create a manifest JSON describing the localization job.

    ``final_audio`` and ``final_video`` are optional paths that point to the
    globally synchronized audio file and the final merged video output.
    ``cloudinary_url`` is the optional Cloudinary URL for the dubbed video.
    ``subtitle_url`` is the optional Cloudinary URL for the VTT subtitle file.
    """
    data = {
        "job_id": job_id,
        "mode": mode,
        "source_lang": source,
        "target_lang": target,
        "course_id": course_id,
        "input_path": input_path,
        "chunk_count": len(chunks),
        "chunks": chunks,
    }
    if final_audio:
        data["final_audio"] = final_audio
    if final_video:
        data["final_video"] = final_video
    if cloudinary_url:  # 🚀 NEW: Store Cloudinary URL
        data["cloudinary_url"] = cloudinary_url
    if subtitle_url:    # 🚀 NEW: Store Subtitle URL
        data["subtitle_url"] = subtitle_url
    mkdir_p(output_dir)
    out_path = os.path.join(output_dir, "manifest.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"Manifest saved: {out_path}")
    return data


def load_manifest(manifest_path: str) -> Dict:
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)