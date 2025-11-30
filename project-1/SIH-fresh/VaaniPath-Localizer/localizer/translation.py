from typing import Optional, Dict
import re
import os
import json
import requests

from .utils import setup_logger

logger = setup_logger("translation")


def _translate_google(text: str, target_lang: str, style_guide: Optional[str] = None, glossary: Optional[Dict[str, str]] = None) -> str:
    """Translate using Google Translate with automatic Gemini fallback for unsupported languages."""
    try:
        from deep_translator import GoogleTranslator
    except Exception as e:
        logger.error("deep-translator not installed; falling back to dummy translation")
        return f"[{target_lang}] {text}"

    # Languages not well-supported by Google Translate - use Gemini instead
    GEMINI_PREFERRED_LANGS = {
        "brx",   # Bodo
        "doi",   # Dogri
        "ks",    # Kashmiri
        "gom",   # Konkani
        "mai",   # Maithili
        "mni",   # Manipuri (Meitei)
        "sat",   # Santali
        "mwr",   # Marwari
        "bho",   # Bhojpuri
        "bgc",   # Haryanvi
    }
    
    # Fallback mapping for languages that can use Google Translate with approximation
    FALLBACK_MAP = {
        "as": "as",      # Assamese - supported by Google
        "ne": "ne",      # Nepali - supported by Google
        "sa": "sa",      # Sanskrit - supported by Google
        "sd": "sd",      # Sindhi - supported by Google
        "ur": "ur",      # Urdu - supported by Google
    }
    
    base_lang = (target_lang or "").split("-")[0]
    
    # Check if this language should use Gemini
    if base_lang in GEMINI_PREFERRED_LANGS:
        logger.info(f"Language {base_lang} not well-supported by Google Translate; using Gemini")
        return _translate_gemini(text, target_lang, style_guide, glossary)
    
    # Use fallback mapping if defined
    lang_to_use = FALLBACK_MAP.get(base_lang, base_lang)
    
    try:
        translator = GoogleTranslator(source='auto', target=lang_to_use)
        out = translator.translate(text)
        
        # Apply dialectal approximation for Bhojpuri
        if base_lang == "bho":
            out = _approx_bhojpuri(out)
        return out
    except Exception as e:
        logger.warning(f"Google translate error for {target_lang}: {e}; trying Gemini fallback")
        # If Google Translate fails, try Gemini as fallback
        return _translate_gemini(text, target_lang, style_guide, glossary)




def _translate_indictrans2(text: str, target_lang: str) -> str:
    # Stub: Implement real model integration later
    return f"{text}"


def _apply_style_guide(text: str, style_guide: Optional[str]) -> str:
    if not style_guide:
        return text
    # Minimal style application: enforce line breaks for readability if guide mentions brevity
    guide = style_guide.lower()
    if "concise" in guide or "brief" in guide:
        return "\n".join([line.strip() for line in text.split(". ")])
    return text


def translate_text(
    text: str,
    target_lang: str,
    model: str = "google",
    style_guide: Optional[str] = None,
    glossary: Optional[Dict[str, str]] = None,
) -> str:
    model = (model or "google").lower()
    if model == "google":
        translated = _translate_google(text, target_lang, style_guide, glossary)
    elif model == "indictrans2":
        translated = _translate_indictrans2(text, target_lang)
    # elif model == "llm":
    #     translated = _translate_llm(text, target_lang, style_guide, glossary)
    elif model == "gemini":
        translated = _translate_gemini(text, target_lang, style_guide, glossary)
    else:
        translated = f"[{target_lang}] {text}"

    translated = _apply_style_guide(translated, style_guide)
    return translated



def _translate_llm(
    text: str,
    target_lang: str,
    style_guide: Optional[str],
    glossary: Optional[Dict[str, str]] = None,
) -> str:
    """LLM-backed translation with environment-configured endpoint.
    If LLM is unavailable or errors, falls back to Google.
    Environment variables:
      - LLM_API_URL: chat-completions style endpoint (OpenAI-compatible)
      - LLM_API_KEY: bearer key
      - LLM_MODEL: optional model name
    """
    api_url = os.environ.get("LLM_API_URL")
    api_key = os.environ.get("LLM_API_KEY")
    model_name = os.environ.get("LLM_MODEL", "")

    if not api_url or not api_key:
        logger.warning("LLM API not configured; falling back to Google translate")
        return _translate_google(text, target_lang)

    base_lang = (target_lang or "").split("-")[0]
    guide = (style_guide or "").strip()
    def _format_glossary_constraints(glossary: Optional[Dict[str, str]]) -> str:
        if not glossary:
            return ""
        # Limit terms to avoid excessively long prompts
        items = list(glossary.items())[:50]
        pairs = "\n".join([f"- {src} -> {tgt}" for src, tgt in items])
        return (
            "Terminology constraints (honor strictly; prefer these canonical translations):\n"
            f"{pairs}\n"
            "If a listed source term appears, use its mapped target form."
        )

    system_prompt = (
        "You are a professional translator for skill training courses. "
        "Translate the user's text into the target language specified. "
        "Preserve technical terms and proper nouns appropriately. "
        "Return only the translated text without explanations."
    )
    if base_lang == "sa":
        system_prompt += " Use a formal, instructional Sanskrit register."
    if guide:
        system_prompt += f" Style guide: {guide}."
    gc = _format_glossary_constraints(glossary)
    if gc:
        system_prompt += " " + gc

    # OpenAI-compatible payload shape
    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Target language code: {base_lang}\nText:\n{text}"},
        ],
        "temperature": 0.2,
    }
    if model_name:
        payload["model"] = model_name

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    try:
        resp = requests.post(api_url, headers=headers, data=json.dumps(payload), timeout=30)
        resp.raise_for_status()
        data = resp.json()
        # Try common shapes
        if isinstance(data, dict):
            # choices[0].message.content
            choices = data.get("choices")
            if choices and isinstance(choices, list):
                msg = (choices[0] or {}).get("message", {})
                content = msg.get("content")
                if content:
                    return content.strip()
            # direct 'output' or 'completion'
            for key in ("output", "completion", "text"):
                if key in data and isinstance(data[key], str):
                    return data[key].strip()
        logger.error(f"LLM translation: unexpected response shape {str(data)[:200]}")
        return _translate_google(text, target_lang)
    except Exception as e:
        logger.error(f"LLM translate error: {e}; falling back to Google")
        return _translate_google(text, target_lang)


def _translate_gemini(
    text: str,
    target_lang: str,
    style_guide: Optional[str],
    glossary: Optional[Dict[str, str]] = None,
) -> str:
    """Translate using Google's Gemini (via google-genai SDK).

    Requires environment variable `GEMINI_API_KEY`. Optional `GEMINI_MODEL` (defaults to
    `gemini-2.5-flash`). If the SDK is unavailable or API key is missing, returns a
    placeholder translation to avoid infinite recursion.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error(f"GEMINI_API_KEY not set; cannot translate {target_lang}. Please set GEMINI_API_KEY environment variable.")
        return f"[{target_lang} - GEMINI_API_KEY required] {text}"

    try:
        # Import here to keep dependency optional
        from google import genai
        from google.genai import types
    except Exception as e:
        logger.error(f"google-genai SDK import failed ({e}); cannot translate. Install: pip install google-genai")
        return f"[{target_lang} - Gemini SDK required] {text}"

    try:
        client = genai.Client(api_key=api_key)
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

        # Map codes to full language names for better Gemini accuracy
        LANG_NAMES = {
            "brx": "Bodo",
            "doi": "Dogri",
            "ks": "Kashmiri",
            "gom": "Konkani",
            "mai": "Maithili",
            "mni": "Manipuri (Meitei)",
            "sat": "Santali",
            "mwr": "Marwari",
            "bho": "Bhojpuri",
            "as": "Assamese",
            "ne": "Nepali",
            "sa": "Sanskrit",
            "sd": "Sindhi",
            "ur": "Urdu",
            "bgc": "Haryanvi",
        }
        
        base_lang = (target_lang or "").split("-")[0]
        lang_name = LANG_NAMES.get(base_lang, base_lang)
        
        # Prompt: ask for direct translation, no extra commentary.
        instructions = [
            f"Translate the following content into the target language '{lang_name}' (code: {base_lang}).",
            "Return only the translated text without quotes or explanation.",
        ]
        if style_guide:
            instructions.append(f"Style guide: {style_guide}")
        # Add terminology constraints if provided
        if glossary:
            items = list(glossary.items())[:50]
            pairs = "\n".join([f"- {src} -> {tgt}" for src, tgt in items])
            instructions.append(
                "Terminology constraints (use these canonical translations when applicable):\n" + pairs
            )

        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text="\n".join(instructions)),
                    types.Part.from_text(text=text),
                ],
            ),
        ]

        # Use non-streaming for simplicity and determinism.
        resp = client.models.generate_content(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(),
        )

        # The SDK returns a rich object; `.text` provides concatenated string.
        translated = getattr(resp, "text", None)
        if not translated:
            logger.error("Gemini returned empty text")
            return f"[{target_lang} - Gemini error] {text}"

        return translated.strip()
    except Exception as e:
        logger.error(f"Gemini translation failed ({e})")
        return f"[{target_lang} - Gemini error: {str(e)[:50]}] {text}"



def _approx_bhojpuri(text: str) -> str:
    """Approximate Bhojpuri dialect from Hindi using lightweight rules.
    This is not a full linguistic conversion, but it nudges common copulas,
    pronouns, auxiliaries, and conjunctions toward Bhojpuri usage.
    """
    rules = [
        # --- Fixed expressions and punctuation-adjacent copulas ---
        (r"ठीक है", "ठीक बा"),
        (r"यह है", "ई बा"),
        (r"ये हैं", "ई लोग बाड़े"),
        (r"वह है", "उ बा"),
        (r"वे हैं", "ऊ लोग बाड़े"),
        (r"Python क्या है", "पायथन का बा"),
        (r"तो क्या है", "तऽ का बा"),
        (r"है([\.,!?])", r"बा\1"),
        (r"हैं([\.,!?])", r"बाड़े\1"),
        # --- Copula / auxiliaries / aspect ---
        (r"\bहै\b", "बा"),
        (r"\bहैं\b", "बाड़े"),
        (r"\bथा\b", "रहल"),
        (r"\bथे\b", "रहल"),
        (r"\bथी\b", "रहल"),
        (r"\bरहा है\b", "करत बा"),
        (r"\bरहे हैं\b", "करत बाड़े"),
        (r"\bरही है\b", "करत बा"),
        (r"\bरही हैं\b", "करत बाड़े"),
        (r"\bहोता है\b", "होला"),
        (r"\bहोते हैं\b", "होले"),
        (r"\bहोगा\b", "होई"),
        (r"\bहोंगे\b", "होइहें"),
        (r"\bकिया जा रहा है\b", "कइल जा रहल बा"),
        (r"\bकिया गया\b", "कइल गइल"),
        (r"\bकिया\b", "कइल"),
        (r"\bकर चुका है\b", "कर चुकल बा"),
        (r"\bकर चुके हैं\b", "कर चुकल बा"),
        (r"\bकर रही है\b", "करत बा"),
        (r"\bकर रहा है\b", "करत बा"),

        # --- Pronouns and possessives ---
        (r"\bमैं\b", "हम"),
        (r"\bमुझे\b", "हमके"),
        (r"\bमुझे\b", "हमके"),
        (r"\bमेरा\b", "हमार"),
        (r"\bमेरी\b", "हमार"),
        (r"\bमेरे\b", "हमार"),
        (r"\bतुम\b", "तू"),
        (r"\bतुम्हें\b", "तोहके"),
        (r"\bतुम्हारा\b", "तोहार"),
        (r"\bतुम्हारी\b", "तोहार"),
        (r"\bआप\b", "रउआ"),
        (r"\bआपको\b", "रउआ के"),
        (r"\bआपका\b", "रउआ के"),
        (r"\bआपकी\b", "रउआ के"),
        (r"\bवह\b", "उह"),
        (r"\bवो\b", "उह"),
        (r"\bवे\b", "ऊ लोग"),
        (r"\bये\b", "ई"),
        (r"\bयह\b", "ई"),

        # --- Question words / particles ---
        (r"\bक्या\b", "का"),
        (r"\bक्यों\b", "काहे"),
        (r"\bकैसे\b", "कइसन"),
        (r"\bकब\b", "कबहुँ"),
        (r"\bकहाँ\b", "कहँवा"),
        (r"\bकिस\b", "कवन"),
        (r"\bकिसे\b", "कवनो/काके"),  # rough
        (r"\bका है\b", "का बा"),
        (r"\bक्या हुआ\b", "का भइल"),

        # --- Negation ---
        (r"\bनहीं\b", "ना"),
        (r"\bमत\b", "ना"),
        (r"\bनही\b", "ना"),  # common misspelling
        (r"\bकभी नहीं\b", "कबहुँ ना"),
        (r"\bनहीं होगा\b", "ना होई"),
        (r"\bनहीं हैं\b", "ना बाड़े"),

        # --- Conjunctions / discourse ---
        (r"\bऔर\b", "आउर"),
        (r"\bलेकिन\b", "बाकिर"),
        (r"\bतब\b", "तब"),
        (r"\bयदि\b", "अगर"),
        (r"\bक्योंकि\b", "काहे कि"),
        (r"\bइसलिए\b", "एही से"),
        (r"\bभी\b", "भि"),
        (r"\bही\b", "एह"),

        # --- Modal / ability / permission ---
        (r"\bसकता है\b", "सकेला"),
        (r"\bसकती है\b", "सकेले"),
        (r"\bसकते हैं\b", "सकेला"),
        (r"\bकर सकता है\b", "कर सकेला"),
        (r"\bकर सकती है\b", "कर सकेले"),
        (r"\bकर सकते हैं\b", "कर सकेला"),
        (r"\bचाहता है\b", "चाहेला"),
        (r"\bचाहती है\b", "चाहेला"),
        (r"\bपाना\b", "पावे"),

        # --- Infinitives / verbal nouns ---
        (r"\bकरना\b", "करे के"),
        (r"\bखाना\b", "खाये के"),
        (r"\bपीना\b", "पीये के"),
        (r"\bदेखना\b", "देखे के"),
        (r"\bलेना\b", "लेवे के"),
        (r"\bदेना\b", "देवे के"),
        (r"\bबनाना\b", "बनावे के"),
        (r"\bपढ़ना\b", "पढ़े के"),
        (r"\bलिखना\b", "लिखे के"),

        # --- Common verbs / domain words ---
        (r"\bजाना\b", "जाए के"),
        (r"\bआना\b", "आवे के"),
        (r"\bबैठना\b", "बैठे के"),
        (r"\bखोलना\b", "खोले के"),
        (r"\bबंद करना\b", "बंद करे के"),
        (r"\bशुरू करना\b", "शुरू करे के"),
        (r"\bसमाप्त करना\b", "खत्म करे के"),
        (r"\bप्रयोग\b", "उपयोग"),
        (r"\bकनेक्ट\b", "जुड़"),
        (r"\bकनेक्शन\b", "जुड़ाव"),
        (r"\bडाटाबेस\b", "डेटाबेस"),
        (r"\bवर्कफ़्लो\b", "वर्कफ्लो"),  # keep loanword

        # --- Politeness / honorifics ---
        (r"\bजी\b", "जी"),  # keep 'जी' as-is but ensure spacing
        (r"\bसाहब\b", "साहेब"),
        (r"\bश्री\b", "श्री"),  # unchanged

        # --- Numbers / quantifiers ---
        (r"\bएक\b", "एक"),
        (r"\bदो\b", "दू"),
        (r"\bतीन\b", "तीन"),
        (r"\bकई\b", "कई"),
        (r"\bसब\b", "सब"), 
        (r"\bकाफी\b", "काफ़ी"),

        # --- Emphasis / intensifiers ---
        (r"\bबहुत\b", "बहुते"),
        (r"\bथोड़ा\b", "थोड़"),
        (r"\bबिलकुल\b", "पूरी तरह"),
        (r"\bअभी\b", "अभी/एगो"),
        (r"\bफिर\b", "फिर"),
        (r"\bअब\b", "अब"),

        # --- Time phrases / temporals ---
        (r"\bकल\b", "काल/भोरे"),  # ambiguous; keep simple
        (r"\bआज\b", "आज"),
        (r"\bसुबह\b", "सबेरे"),
        (r"\bशाम\b", "सांझ"),

        # --- Punctuation / spacing cleanups applied after substitutions ---
    ]
    out = text
    for pattern, repl in rules:
        out = re.sub(pattern, repl, out)
    return out
