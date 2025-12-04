"""Text-to-Speech service using Coqui TTS."""
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import warnings

warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)

# Try to import Coqui TTS
try:
    from TTS.api import TTS
    COQUI_TTS_AVAILABLE = True
except ImportError:
    COQUI_TTS_AVAILABLE = False
    logger.warning("Coqui TTS not available. Install TTS library.")


class CoquiTTS:
    """Text-to-Speech service using Coqui TTS."""
    
    def __init__(
        self,
        model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2",
        device: str = "cpu"
    ):
        """
        Initialize Coqui TTS model.
        
        Args:
            model_name: TTS model name (prefer XTTS for multilingual)
            device: Device to use (cpu, cuda)
        """
        self.model_name = model_name
        self.device = device
        self.tts = None
        self.initialized = False
    
    def initialize(self):
        """Initialize the TTS model."""
        if not COQUI_TTS_AVAILABLE:
            raise ImportError("Coqui TTS is not installed. Please install TTS library.")
        
        try:
            logger.info(f"Loading Coqui TTS model: {self.model_name} on {self.device}")
            self.tts = TTS(model_name=self.model_name, progress_bar=False).to(self.device)
            self.initialized = True
            logger.info("Coqui TTS model loaded successfully")
        except Exception as e:
            logger.error(f"Error initializing Coqui TTS: {str(e)}")
            raise
    
    def synthesize(
        self,
        text: str,
        output_path: Path,
        language: str = "en",
        speaker_wav: Optional[Path] = None
    ) -> bool:
        """
        Synthesize speech from text.
        
        Args:
            text: Text to synthesize
            output_path: Path to save output WAV file
            language: Language code
            speaker_wav: Optional speaker reference audio for voice cloning
        
        Returns:
            True if successful, False otherwise
        """
        if not self.initialized:
            self.initialize()
        
        try:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Generating TTS audio for language {language}: {output_path}")
            
            # Map language codes to Coqui TTS language codes
            lang_map = {
                "hi": "hi",
                "bn": "bn",
                "mr": "mr",
                "ta": "ta",
                "te": "te",
                "kn": "kn",
                "ml": "ml",
                "or": "or",
                "gu": "gu",
                "pa": "pa",
                "as": "as",
                "en": "en"
            }
            
            tts_lang = lang_map.get(language, "en")
            
            # Use XTTS if available (supports multilingual)
            if "xtts" in self.model_name.lower():
                if speaker_wav and speaker_wav.exists():
                    # Voice cloning mode
                    self.tts.tts_to_file(
                        text=text,
                        file_path=str(output_path),
                        language=tts_lang,
                        speaker_wav=str(speaker_wav)
                    )
                else:
                    # Standard mode
                    self.tts.tts_to_file(
                        text=text,
                        file_path=str(output_path),
                        language=tts_lang
                    )
            else:
                # For other models, use standard synthesis
                self.tts.tts_to_file(
                    text=text,
                    file_path=str(output_path)
                )
            
            logger.info(f"TTS audio generated successfully: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating TTS: {str(e)}")
            return False
    
    def synthesize_from_transcript(
        self,
        transcript_data: Dict[str, Any],
        output_path: Path,
        language: str,
        speaker_wav: Optional[Path] = None
    ) -> bool:
        """
        Synthesize speech from transcript data.
        
        Args:
            transcript_data: Transcript data dictionary
            output_path: Path to save output WAV file
            language: Language code
            speaker_wav: Optional speaker reference audio
        
        Returns:
            True if successful, False otherwise
        """
        # Extract full text from transcript
        full_text = transcript_data.get("full_text", "")
        
        if not full_text:
            # Fallback: concatenate segment texts
            segments = transcript_data.get("segments", [])
            full_text = " ".join([seg.get("text", "") for seg in segments])
        
        return self.synthesize(full_text, output_path, language, speaker_wav)


# Fallback TTS for when Coqui TTS is not available
class FallbackTTS:
    """Fallback TTS that creates a silent audio file (for testing)."""
    
    def synthesize(
        self,
        text: str,
        output_path: Path,
        language: str = "en",
        speaker_wav: Optional[Path] = None
    ) -> bool:
        """Create a placeholder file (fallback)."""
        logger.warning(f"Fallback TTS: creating placeholder file for {language}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        # Create an empty file as placeholder
        output_path.touch()
        return True
    
    def synthesize_from_transcript(
        self,
        transcript_data: Dict[str, Any],
        output_path: Path,
        language: str,
        speaker_wav: Optional[Path] = None
    ) -> bool:
        """Create a placeholder file (fallback)."""
        return self.synthesize("", output_path, language, speaker_wav)


def get_tts_service(
    model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2",
    device: str = "cpu"
) -> Any:
    """Get TTS service instance (Coqui TTS or fallback)."""
    if COQUI_TTS_AVAILABLE:
        return CoquiTTS(model_name=model_name, device=device)
    else:
        logger.warning("Using fallback TTS. Install Coqui TTS for real synthesis.")
        return FallbackTTS()



