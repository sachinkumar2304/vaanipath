# Demo script for Localizer

"""Run a demo localization from English to Marathi.

This script assumes a file named `demo-input.mp4` exists in the repository root.
It will create a job `demo_job` and produce `final_video.mp4` in the output folder.
After the job finishes, it validates that the audio and video durations match
within a small tolerance.
"""

import subprocess
import pathlib
import json
import sys

from localizer.app import run_job
from localizer.audio_utils import get_duration

def main():
    repo_root = pathlib.Path(__file__).resolve().parents[1]
    input_video = repo_root / "demo-input.mp4"
    if not input_video.is_file():
        print("demo-input.mp4 not found in repository root.")
        sys.exit(1)

    job_id = "demo_job"
    course_id = "demo_course"
    manifest_path = run_job(
        input_path=str(input_video),
        source="en",
        target="mr",
        job_id=job_id,
        course_id=course_id,
        mode="fast",
    )
    # Load manifest to get final video path
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    final_video = pathlib.Path(manifest.get("final_video", ""))
    if not final_video.is_file():
        print("Final video not generated.")
        sys.exit(1)

    # Verify durations
    video_dur = get_duration(str(final_video))
    audio_dur = get_duration(str(manifest.get("final_audio")))
    diff = abs(video_dur - audio_dur)
    print(f"Video duration: {video_dur:.2f}s, Audio duration: {audio_dur:.2f}s, diff: {diff:.3f}s")
    if diff > 0.05:
        print("Warning: audio and video durations differ by more than 0.05s.")
    else:
        print("Success: audio and video are synchronized.")

if __name__ == "__main__":
    main()
