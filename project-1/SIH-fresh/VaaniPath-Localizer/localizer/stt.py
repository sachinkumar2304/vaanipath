from typing import Dict, Any, List, Tuple

from faster_whisper import WhisperModel

from .config import MODE_CONFIG
from .utils import setup_logger

logger = setup_logger("stt")


def transcribe(
    audio_path: str,
    source_lang: str,
    initial_prompt: str,
    mode: str = "fast",
) -> Tuple[str, List[Dict[str, Any]]]:
    cfg = MODE_CONFIG.get(mode, MODE_CONFIG["fast"])
    model_size = cfg["whisper_model"]
    compute_type = cfg["compute_type"]

    logger.info(f"STT mode={mode}, model={model_size}, compute={compute_type}")
    model = WhisperModel(model_size, device="cpu", compute_type=compute_type)

    segments_iter, info = model.transcribe(
        audio_path,
        language=source_lang,
        vad_filter=cfg.get("vad_filter", False),
        initial_prompt=initial_prompt or None,
        beam_size=1,
        condition_on_previous_text=True,
    )

    segments = []
    texts = []
    for seg in segments_iter:
        segments.append({"start": seg.start, "end": seg.end, "text": seg.text})
        texts.append(seg.text)

    text = " ".join(t.strip() for t in texts)
    return text, segments