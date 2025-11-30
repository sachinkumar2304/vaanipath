from typing import Dict

from .utils import setup_logger

logger = setup_logger("culture")


def apply_cultural_adaptation(text: str, target_lang: str, cultural_rules: Dict[str, str]) -> str:
    if not text:
        return text

    adapted = text
    for k, v in (cultural_rules or {}).items():
        adapted = adapted.replace(k, v)

    # Simple courtesy localization
    if target_lang.startswith("hi"):
        adapted = adapted.replace("Thank you", "धन्यवाद")
    elif target_lang.startswith("es"):
        adapted = adapted.replace("Thank you", "Gracias")

    return adapted