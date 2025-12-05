import os

MODE_CONFIG = {
    "fast": {
        "whisper_model": "tiny",
        "compute_type": "int8",
        "vad_filter": False,
    },
    "quality": {
        "whisper_model": "base",
        "compute_type": "float32",
        "vad_filter": True,
    },
    "balanced": {
        "whisper_model": "small",
        "compute_type": "float16",
        "vad_filter": True,
    },
    "high_accuracy": {
        "whisper_model": "medium",
        "compute_type": "float16",
        "vad_filter": True,
    },
    "max_accuracy": {
        "whisper_model": "large",
        "compute_type": "float32",
        "vad_filter": True,
    },
    "gpu_optimized": {
        "whisper_model": "small",
        "compute_type": "float16",
        "vad_filter": False,
    },
    "low_memory": {
        "whisper_model": "tiny",
        "compute_type": "int8",
        "vad_filter": True,
    },
    "noisy_audio": {
        "whisper_model": "medium",
        "compute_type": "float32",
        "vad_filter": True,
    },
}


# Allow env override for the translation model (e.g., "llm", "google", "indictrans2")
TRANSLATION_DEFAULT_MODEL = os.environ.get("TRANSLATION_MODEL", "google")

CHUNK_LENGTH_SECONDS = 30.0
CHUNK_OVERLAP_SECONDS = 0.0
