from typing import Dict
import os
import json

from .utils import setup_logger

logger = setup_logger("rag_client")


def _load_sector_glossary(course_id: str) -> Dict[str, str]:
    base_dir = os.path.join(os.path.dirname(__file__), "sample_data", "glossaries")
    path = os.path.join(base_dir, f"{course_id}.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def get_job_context(course_id: str, src: str, tgt: str) -> Dict:
    # Lightweight RAG context with sector-aware glossary support
    logger.info(f"Loading RAG context for course_id={course_id} src={src} tgt={tgt}")
    base_glossary = {
        "safety": "safety",
        "apprentice": "apprentice",
        "training": "training",
        "assessment": "assessment",
        "workshop": "workshop",
    }

    sector_glossary = _load_sector_glossary(course_id)
    # Always merge job roles/person roles for vocational relevance
    roles_path = os.path.join(os.path.dirname(__file__), "sample_data", "glossaries", "roles.json")
    roles_glossary = {}
    if os.path.exists(roles_path):
        try:
            with open(roles_path, "r", encoding="utf-8") as f:
                roles_glossary = json.load(f)
        except Exception:
            roles_glossary = {}
    merged_glossary = {**base_glossary, **roles_glossary, **sector_glossary}

    # Load optional language-specific target glossary to guide translations
    def _load_language_glossary(lang_code: str) -> Dict[str, str]:
        base_dir = os.path.join(os.path.dirname(__file__), "sample_data", "glossaries", "lang")
        base_code = (lang_code or "").split("-")[0]
        path = os.path.join(base_dir, f"{base_code}.json")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    target_glossary = _load_language_glossary(tgt)

    cultural_rules = {
        "USD": "INR" if tgt.startswith("hi") or tgt.endswith("-IN") else "USD",
        "kilometers": "kilometers",  # avoid US-centric swaps
    }

    context = {
        "glossary": merged_glossary,
        "initial_prompt": (
            "This is a vocational training module. Use clear, industry terminology; avoid slang; keep sentences short."
        ),
        "style_guide": (
            "Use concise, professional tone. Prefer active voice. Keep terminology consistent with glossary."
        ),
        "cultural_rules": cultural_rules,
        "target_glossary": target_glossary,
    }
    return context
