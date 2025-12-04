"""Translation service using IndicTrans2."""
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)

# Try to import IndicTrans2
try:
    from indicTrans.inference.engine import Model
    INDICTRANS_AVAILABLE = True
except ImportError:
    INDICTRANS_AVAILABLE = False
    logger.warning("IndicTrans2 not available. Install indicTrans library.")


class IndicTransTranslator:
    """Translation service using IndicTrans2."""
    
    def __init__(self, model_dir: Optional[str] = None):
        """
        Initialize IndicTrans2 translator.
        
        Args:
            model_dir: Directory containing IndicTrans2 models
        """
        self.model_dir = model_dir
        self.en_indic_model = None
        self.indic_en_model = None
        self.initialized = False
    
    def initialize(self):
        """Initialize the translation models."""
        if not INDICTRANS_AVAILABLE:
            raise ImportError("IndicTrans2 is not installed. Please install indicTrans library.")
        
        try:
            # Initialize English to Indic model
            logger.info("Loading IndicTrans2 English-to-Indic model...")
            self.en_indic_model = Model(
                expdir=self.model_dir or "ai4bharat/indictrans2-en-indic-1B"
            )
            
            self.initialized = True
            logger.info("IndicTrans2 models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error initializing IndicTrans2: {str(e)}")
            raise
    
    def translate_text(
        self,
        text: str,
        source_lang: str = "en",
        target_lang: str = "hi"
    ) -> str:
        """
        Translate a single text string.
        
        Args:
            text: Text to translate
            source_lang: Source language code (default: en)
            target_lang: Target language code
        
        Returns:
            Translated text
        """
        if not self.initialized:
            self.initialize()
        
        if source_lang == "en" and target_lang != "en":
            # Use English to Indic model
            if self.en_indic_model is None:
                self.initialize()
            
            try:
                # Map language codes to IndicTrans2 script codes
                script_map = {
                    "hi": "hin_Deva", "bn": "ben_Beng", "mr": "mar_Deva",
                    "ta": "tam_Taml", "te": "tel_Telu", "kn": "kan_Knda",
                    "ml": "mal_Mlym", "or": "ory_Orya", "gu": "guj_Gujr",
                    "pa": "pan_Guru", "as": "asm_Beng", "ks": "kas_Arab",
                    "sd": "snd_Arab", "kok": "kok_Deva", "ne": "nep_Deva",
                    "sa": "san_Deva", "ur": "urd_Arab"
                }
                
                target_script = script_map.get(target_lang, f"{target_lang}_Deva")
                translated = self.en_indic_model.translate_paragraph(
                    text,
                    "eng_Latn",
                    target_script
                )
                return translated
            except Exception as e:
                logger.error(f"Translation error: {str(e)}")
                # Fallback: return original text
                return text
        else:
            logger.warning(f"Translation from {source_lang} to {target_lang} not supported yet")
            return text
    
    def translate_segments(
        self,
        segments: List[Dict[str, Any]],
        target_lang: str
    ) -> List[Dict[str, Any]]:
        """
        Translate transcript segments.
        
        Args:
            segments: List of segment dictionaries
            target_lang: Target language code
        
        Returns:
            List of translated segments
        """
        translated_segments = []
        
        for segment in segments:
            translated_segment = segment.copy()
            
            # Translate segment text
            if "text" in segment:
                translated_text = self.translate_text(
                    segment["text"],
                    source_lang="en",
                    target_lang=target_lang
                )
                translated_segment["text"] = translated_text
            
            # Translate words if present
            if "words" in segment:
                translated_words = []
                for word in segment["words"]:
                    translated_word = word.copy()
                    if "word" in word:
                        translated_word["word"] = self.translate_text(
                            word["word"],
                            source_lang="en",
                            target_lang=target_lang
                        )
                    translated_words.append(translated_word)
                translated_segment["words"] = translated_words
            
            translated_segments.append(translated_segment)
        
        return translated_segments
    
    def translate_transcript(
        self,
        transcript_data: Dict[str, Any],
        target_lang: str
    ) -> Dict[str, Any]:
        """
        Translate entire transcript data structure.
        
        Args:
            transcript_data: Transcript data dictionary
            target_lang: Target language code
        
        Returns:
            Translated transcript data
        """
        translated = transcript_data.copy()
        
        # Translate full text
        if "full_text" in translated:
            translated["full_text"] = self.translate_text(
                translated["full_text"],
                source_lang="en",
                target_lang=target_lang
            )
        
        # Translate segments
        if "segments" in translated:
            translated["segments"] = self.translate_segments(
                translated["segments"],
                target_lang
            )
        
        return translated
    
    def translate_to_all_indic_languages(
        self,
        transcript_data: Dict[str, Any],
        languages: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Translate transcript to multiple Indic languages.
        
        Args:
            transcript_data: Transcript data dictionary
            languages: List of target language codes
        
        Returns:
            Dictionary mapping language codes to translated transcript data
        """
        translations = {}
        
        for lang in languages:
            logger.info(f"Translating to {lang}...")
            try:
                translated = self.translate_transcript(transcript_data, lang)
                translations[lang] = translated
            except Exception as e:
                logger.error(f"Error translating to {lang}: {str(e)}")
                # Store original transcript as fallback
                translations[lang] = transcript_data.copy()
        
        return translations


# Fallback translator for when IndicTrans2 is not available
class FallbackTranslator:
    """Fallback translator that returns original text (for testing)."""
    
    def translate_transcript(
        self,
        transcript_data: Dict[str, Any],
        target_lang: str
    ) -> Dict[str, Any]:
        """Return transcript as-is (fallback)."""
        logger.warning(f"Fallback translator: returning original text for {target_lang}")
        return transcript_data.copy()
    
    def translate_to_all_indic_languages(
        self,
        transcript_data: Dict[str, Any],
        languages: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """Return original transcript for all languages (fallback)."""
        translations = {}
        for lang in languages:
            translations[lang] = transcript_data.copy()
        return translations


def get_translator(model_dir: Optional[str] = None) -> Any:
    """Get translator instance (IndicTrans2 or fallback)."""
    if INDICTRANS_AVAILABLE:
        return IndicTransTranslator(model_dir=model_dir)
    else:
        logger.warning("Using fallback translator. Install IndicTrans2 for real translations.")
        return FallbackTranslator()

