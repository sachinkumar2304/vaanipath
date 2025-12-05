import math
import os
import subprocess
from typing import List, Dict

from .utils import mkdir_p, safe_filename, setup_logger, FFMPEG, FFPROBE

logger = setup_logger("video_splitter")


def _ffprobe_duration(input_path: str) -> float:
    cmd = [
        FFPROBE,
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        input_path,
    ]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        return float(out.decode().strip())
    except subprocess.CalledProcessError as e:
        logger.error(f"ffprobe failed: {e.output.decode(errors='ignore')}")
        raise


def split_video(
    input_path: str,
    output_dir: str,
    chunk_length: float = 30.0,
    overlap: float = 1.0,
) -> List[Dict]:
    mkdir_p(output_dir)
    duration = _ffprobe_duration(input_path)
    logger.info(f"Input duration: {duration:.2f}s")

    # Next chunk starts at previous_end - overlap, so step = chunk_length - overlap
    step = max(0.1, chunk_length - overlap)
    starts = []
    t = 0.0
    while t < duration:
        starts.append(t)
        t += step

    chunks = []
    base = os.path.splitext(os.path.basename(input_path))[0]
    for i, start in enumerate(starts):
        end = min(start + chunk_length, duration)
        out_video = os.path.join(output_dir, f"chunk_{i:04d}.mp4")
        out_audio = os.path.join(output_dir, f"chunk_{i:04d}.wav")

        # Extract video segment
        cmd_video = [
            FFMPEG,
            "-y",
            "-ss",
            str(start),
            "-i",
            input_path,
            "-t",
            str(end - start),
            "-c",
            "copy",
            out_video,
        ]

        # Extract audio from the segment
        cmd_audio = [
            FFMPEG,
            "-y",
            "-i",
            out_video,
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-f",
            "wav",
            out_audio,
        ]

        try:
            subprocess.check_call(cmd_video, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            subprocess.check_call(cmd_audio, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            logger.error(f"ffmpeg segment extraction failed at chunk {i}: {e}")
            raise

        chunks.append(
            {
                "index": i,
                "start": start,
                "end": end,
                "video_path": out_video,
                "audio_path": out_audio,
            }
        )

    logger.info(f"Created {len(chunks)} chunks at {output_dir}")
    return chunks