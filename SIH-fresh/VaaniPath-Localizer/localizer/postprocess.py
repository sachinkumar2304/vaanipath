import os
import shutil

from .utils import setup_logger

logger = setup_logger("postprocess")

# _get_duration, _build_atempo_chain, time_stretch_audio moved to audio_utils.py
# Using imported versions.

# Legacy functions removed.
# Global sync logic is now in audio_sync.py and app.py/resynthesize.py handles finalization.


def cleanup_job_artifacts(manifest_path: str, delete_chunks: bool = True, delete_tts: bool = True, delete_finalize_work: bool = True) -> dict:
    base_out = os.path.dirname(manifest_path)
    removed = []
    try:
        if delete_chunks:
            d = os.path.join(base_out, "chunks")
            if os.path.isdir(d):
                shutil.rmtree(d, ignore_errors=True)
                removed.append(d)
        if delete_tts:
            d = os.path.join(base_out, "tts")
            if os.path.isdir(d):
                shutil.rmtree(d, ignore_errors=True)
                removed.append(d)
        if delete_finalize_work:
            d = os.path.join(base_out, "finalize")
            if os.path.isdir(d):
                shutil.rmtree(d, ignore_errors=True)
                removed.append(d)
    except Exception:
        pass
    logger.info(f"Cleanup removed: {removed}")
    return {"removed": removed}
