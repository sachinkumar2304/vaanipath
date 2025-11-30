import os
import subprocess
from typing import List

from .utils import setup_logger, FFMPEG, FFPROBE

logger = setup_logger("audio_utils")


def get_duration(path: str) -> float:
    cmd = [
        FFPROBE,
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        path,
    ]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        return float(out.decode().strip())
    except Exception as e:
        logger.error(f"Failed to get duration for {path}: {e}")
        return 0.0


def _build_atempo_chain(ratio: float) -> str:
    # We want to change speed by factor 'ratio'. atempo supports 0.5..2.0 per stage
    if abs(ratio - 1.0) < 0.01:
        return "atempo=1.0"
    stages: List[float] = []
    if ratio > 1.0:
        r = ratio
        while r > 2.0:
            stages.append(2.0)
            r /= 2.0
        stages.append(r)
    else:
        r = ratio
        while r < 0.5:
            stages.append(0.5)
            r /= 0.5
        stages.append(r)
    return ",".join([f"atempo={s:.6f}" for s in stages])


def time_stretch_audio(input_audio: str, target_duration: float, output_audio: str) -> str:
    src_dur = get_duration(input_audio)
    if src_dur <= 0.0:
        logger.warning(f"Invalid source duration for {input_audio}, copying as is.")
        import shutil
        shutil.copy2(input_audio, output_audio)
        return output_audio
        
    ratio = src_dur / target_duration
    
    # Safety check: if ratio is too extreme, clamp it or warn?
    # For now, let's trust the user wants sync even if it sounds weird.
    
    # Select codec based on output file extension
    if output_audio.endswith('.m4a') or output_audio.endswith('.aac'):
        codec = 'aac'
    else:
        codec = 'libmp3lame'
    
    filter_str = _build_atempo_chain(ratio)
    cmd = [
        FFMPEG,
        "-y",
        "-i",
        input_audio,
        "-filter:a",
        filter_str,
        "-c:a",
        codec,
        output_audio,
    ]
    try:
        subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        logger.info(f"Time-stretched audio to match {target_duration:.2f}s (ratio {ratio:.2f}): {output_audio}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Time stretch failed: {e}")
        raise
    return output_audio
