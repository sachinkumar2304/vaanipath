import os
from pathlib import Path
from typing import List
import subprocess
import logging

from .utils import setup_logger, FFMPEG
from .audio_utils import get_duration, time_stretch_audio

logger = setup_logger("audio_sync")

def concatenate_and_stretch(audio_paths: List[Path], target_duration: float, output_path: Path) -> Path:
    """Concatenate a list of audio files and stretch them to match *target_duration*.

    Steps:
    1. Create a temporary ``concat.txt`` file listing the inputs for ffmpeg.
    2. Use ffmpeg ``-f concat`` to merge them into a single intermediate file.
    3. Compute the stretch ratio (source_duration / target_duration).
    4. Call :func:`audio_utils.time_stretch_audio` to apply a single atempo chain.
    5. Return the path to the stretched audio file.
    """
    # Ensure all paths are absolute strings
    audio_paths = [Path(p).resolve() for p in audio_paths]
    if not audio_paths:
        raise ValueError("No audio files provided for concatenation")

    # 1. Write concat list
    concat_file = output_path.parent / "concat.txt"
    with open(concat_file, "w", encoding="utf-8") as f:
        for p in audio_paths:
            f.write(f"file '{p.as_posix()}'\n")

    intermediate = output_path.parent / "intermediate.wav"
    # 2. Concatenate using ffmpeg
    cmd_concat = [
        FFMPEG,
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_file),
        "-c",
        "copy",
        str(intermediate),
    ]
    logger.info("Concatenating %d audio chunks", len(audio_paths))
    subprocess.check_call(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    # 3. Compute source duration
    src_dur = get_duration(str(intermediate))
    if src_dur <= 0:
        raise RuntimeError(f"Failed to obtain duration of concatenated audio {intermediate}")

    # 4. Stretch to target duration
    stretched = time_stretch_audio(str(intermediate), target_duration, str(output_path))
    logger.info("Created stretched audio %s (target %.2fs)", stretched, target_duration)

    # Cleanup temporary files
    try:
        os.remove(concat_file)
        os.remove(intermediate)
    except OSError:
        pass

    return Path(stretched)
