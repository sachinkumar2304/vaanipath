import os
import argparse
from .postprocess import finalize_job, cleanup_job_artifacts


def main():
    parser = argparse.ArgumentParser(description="Finalize a localization job by merging TTS into muted original video")
    parser.add_argument("--job", help="Job ID in localizer/output/<job>")
    parser.add_argument("--manifest", help="Path to manifest.json (overrides --job)")
    parser.add_argument("--cleanup", action="store_true", help="Delete chunks/tts/temp after finalization")
    args = parser.parse_args()

    if args.manifest:
        manifest_path = args.manifest
    elif args.job:
        base = os.path.join("localizer", "output", args.job)
        manifest_path = os.path.join(base, "manifest.json")
    else:
        raise SystemExit("Provide --job or --manifest")

    final_out = finalize_job(manifest_path)
    print(final_out)
    if args.cleanup:
        res = cleanup_job_artifacts(manifest_path)
        print(res)


if __name__ == "__main__":
    main()
