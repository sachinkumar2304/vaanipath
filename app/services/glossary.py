"""Glossary processing for domain-specific term replacements."""
import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional
import unicodedata

logger = logging.getLogger(__name__)


class GlossaryProcessor:
    """Process glossary for domain-specific term replacements."""
    
    def __init__(self, glossary_path: Optional[Path] = None):
        """
        Initialize glossary processor.
        
        Args:
            glossary_path: Path to JSON glossary file
        """
        self.glossary: Dict[str, Dict[str, str]] = {}
        if glossary_path and glossary_path.exists():
            self.load_glossary(glossary_path)
    
    def load_glossary(self, glossary_path: Path):
        """Load glossary from JSON file."""
        try:
            with open(glossary_path, "r", encoding="utf-8") as f:
                self.glossary = json.load(f)
            logger.info(f"Loaded glossary with {len(self.glossary)} entries from {glossary_path}")
        except Exception as e:
            logger.error(f"Error loading glossary: {str(e)}")
            self.glossary = {}
    
    def set_glossary(self, glossary: Dict[str, Dict[str, str]]):
        """Set glossary dictionary directly."""
        self.glossary = glossary
        logger.info(f"Set glossary with {len(self.glossary)} entries")
    
    def normalize_unicode(self, text: str) -> str:
        """
        Normalize Unicode text.
        
        Args:
            text: Input text
        
        Returns:
            Normalized text
        """
        # Normalize to NFC form
        normalized = unicodedata.normalize("NFC", text)
        return normalized
    
    def apply_glossary(
        self,
        text: str,
        target_lang: str,
        exact_match: bool = True,
        case_sensitive: bool = False
    ) -> str:
        """
        Apply glossary replacements to text.
        
        Args:
            text: Input text to process
            target_lang: Target language code
            exact_match: Whether to use exact word matching
            case_sensitive: Whether matching should be case-sensitive
        
        Returns:
            Text with glossary replacements applied
        """
        if not self.glossary:
            return self.normalize_unicode(text)
        
        result = text
        
        # Normalize Unicode first
        result = self.normalize_unicode(result)
        
        # Process each glossary entry
        for source_term, translations in self.glossary.items():
            if target_lang not in translations:
                continue
            
            replacement = translations[target_lang]
            
            if exact_match:
                # Exact word boundary matching
                pattern = r'\b' + re.escape(source_term) + r'\b'
                if not case_sensitive:
                    pattern = f"(?i){pattern}"
                
                result = re.sub(pattern, replacement, result)
            else:
                # Fuzzy matching (substring replacement)
                if case_sensitive:
                    result = result.replace(source_term, replacement)
                else:
                    # Case-insensitive replacement
                    pattern = re.compile(re.escape(source_term), re.IGNORECASE)
                    result = pattern.sub(replacement, result)
        
        return result
    
    def apply_glossary_to_segments(
        self,
        segments: List[Dict[str, any]],
        target_lang: str,
        exact_match: bool = True
    ) -> List[Dict[str, any]]:
        """
        Apply glossary to transcript segments.
        
        Args:
            segments: List of segment dictionaries
            target_lang: Target language code
            exact_match: Whether to use exact word matching
        
        Returns:
            List of segments with glossary applied
        """
        processed_segments = []
        
        for segment in segments:
            processed_segment = segment.copy()
            
            # Apply glossary to segment text
            if "text" in processed_segment:
                processed_segment["text"] = self.apply_glossary(
                    processed_segment["text"],
                    target_lang,
                    exact_match
                )
            
            # Apply glossary to words if present
            if "words" in processed_segment:
                processed_words = []
                for word in processed_segment["words"]:
                    processed_word = word.copy()
                    if "word" in processed_word:
                        processed_word["word"] = self.apply_glossary(
                            processed_word["word"],
                            target_lang,
                            exact_match
                        )
                    processed_words.append(processed_word)
                processed_segment["words"] = processed_words
            
            processed_segments.append(processed_segment)
        
        return processed_segments
    
    def apply_glossary_to_translation(
        self,
        translation_data: Dict[str, any],
        target_lang: str
    ) -> Dict[str, any]:
        """
        Apply glossary to entire translation data structure.
        
        Args:
            translation_data: Translation data dictionary
            target_lang: Target language code
        
        Returns:
            Translation data with glossary applied
        """
        processed = translation_data.copy()
        
        # Apply to full text
        if "full_text" in processed:
            processed["full_text"] = self.apply_glossary(
                processed["full_text"],
                target_lang
            )
        
        # Apply to segments
        if "segments" in processed:
            processed["segments"] = self.apply_glossary_to_segments(
                processed["segments"],
                target_lang
            )
        
        return processed


def create_sample_glossary() -> Dict[str, Dict[str, str]]:
    """Create a sample glossary dictionary."""
    return {
        "AI": {
            "hi": "कृत्रिम बुद्धिमत्ता",
            "bn": "কৃত্রিম বুদ্ধিমত্তা",
            "ta": "செயற்கை நுண்ணறிவு",
            "te": "కృత్రిమ మేధస్సు"
        },
        "Machine Learning": {
            "hi": "मशीन लर्निंग",
            "bn": "মেশিন লার্নিং",
            "ta": "இயந்திரக் கற்பித்தல்",
            "te": "మెషిన్ లెర్నింగ్"
        },
        "Deep Learning": {
            "hi": "डीप लर्निंग",
            "bn": "ডিপ লার্নিং",
            "ta": "ஆழமான கற்றல்",
            "te": "డీప్ లెర్నింగ్"
        }
    }



