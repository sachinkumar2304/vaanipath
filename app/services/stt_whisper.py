"""Speech-to-Text service using Whisper."""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import warnings

# Try to import faster-whisper first (preferred), fallback to whisperx
try:
    from faster_whisper import WhisperModel
    USE_FASTER_WHISPER = True
except ImportError:
    USE_FASTER_WHISPER = False
    try:
        import whisperx
        USE_WHISPERX = True
    except ImportError:
        USE_WHISPERX = False
        logging.warning("Neither faster-whisper nor whisperx is installed. STT will not work.")

logger = logging.getLogger(__name__)


class WhisperSTT:
    """Speech-to-Text service using Whisper."""
    
    def __init__(self, model_size: str = "base", device: str = "cpu", compute_type: str = "int8"):
        """
        Initialize Whisper STT model.
        
        Args:
            model_size: Model size (tiny, base, small, medium, large)
            device: Device to use (cpu, cuda)
            compute_type: Compute type for faster-whisper (int8, int8_float16, float16, float32)
        """
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model = None
        
    def load_model(self):
        """Load the Whisper model."""
        if USE_FASTER_WHISPER:
            logger.info(f"Loading faster-whisper model: {self.model_size} on {self.device}")
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type
            )
        elif USE_WHISPERX:
            logger.info(f"Loading whisperx model: {self.model_size} on {self.device}")
            self.model = whisperx.load_model(
                self.model_size,
                self.device,
                compute_type=self.compute_type
            )
        else:
            raise ImportError("No Whisper implementation available. Install faster-whisper or whisperx.")
    
    def transcribe(
        self,
        audio_path: Path,
        language: str = "en",
        word_timestamps: bool = True
    ) -> Dict[str, Any]:
        """
        Transcribe audio file.
        
        Args:
            audio_path: Path to audio file
            language: Language code (default: en)
            word_timestamps: Whether to include word-level timestamps
        
        Returns:
            Dictionary with transcript data including segments and word timestamps
        """
        if self.model is None:
            self.load_model()
        
        logger.info(f"Transcribing audio: {audio_path}")
        
        if USE_FASTER_WHISPER:
            return self._transcribe_faster_whisper(audio_path, language, word_timestamps)
        elif USE_WHISPERX:
            return self._transcribe_whisperx(audio_path, language, word_timestamps)
        else:
            raise RuntimeError("No Whisper implementation available")
    
    def _transcribe_faster_whisper(
        self,
        audio_path: Path,
        language: str,
        word_timestamps: bool
    ) -> Dict[str, Any]:
        """Transcribe using faster-whisper."""
        segments, info = self.model.transcribe(
            str(audio_path),
            language=language,
            word_timestamps=word_timestamps,
            beam_size=5
        )
        
        # Convert segments to list
        segments_list = []
        full_text = ""
        
        for segment in segments:
            segment_dict = {
                "id": len(segments_list),
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip()
            }
            
            if word_timestamps and hasattr(segment, 'words'):
                segment_dict["words"] = [
                    {
                        "word": word.word,
                        "start": word.start,
                        "end": word.end,
                        "probability": getattr(word, 'probability', None)
                    }
                    for word in segment.words
                ]
            
            segments_list.append(segment_dict)
            full_text += segment.text.strip() + " "
        
        return {
            "language": info.language,
            "language_probability": info.language_probability,
            "duration": info.duration,
            "full_text": full_text.strip(),
            "segments": segments_list
        }
    
    def _transcribe_whisperx(
        self,
        audio_path: Path,
        language: str,
        word_timestamps: bool
    ) -> Dict[str, Any]:
        """Transcribe using whisperx."""
        audio = whisperx.load_audio(str(audio_path))
        result = self.model.transcribe(audio, language=language, batch_size=16)
        
        # Align for word timestamps if needed
        if word_timestamps:
            model_a, metadata = whisperx.load_align_model(language_code=language, device=self.device)
            result = whisperx.align(result["segments"], model_a, metadata, audio, self.device, return_char_alignments=False)
        
        # Format result
        segments_list = []
        full_text = ""
        
        for segment in result.get("segments", []):
            segment_dict = {
                "id": segment.get("id", len(segments_list)),
                "start": segment.get("start", 0),
                "end": segment.get("end", 0),
                "text": segment.get("text", "").strip()
            }
            
            if word_timestamps and "words" in segment:
                segment_dict["words"] = [
                    {
                        "word": word.get("word", ""),
                        "start": word.get("start", 0),
                        "end": word.get("end", 0),
                        "probability": word.get("probability", None)
                    }
                    for word in segment["words"]
                ]
            
            segments_list.append(segment_dict)
            full_text += segment_dict["text"] + " "
        
        return {
            "language": result.get("language", language),
            "duration": result.get("duration", 0),
            "full_text": full_text.strip(),
            "segments": segments_list
        }
    
    def save_transcript_json(self, transcript_data: Dict[str, Any], output_path: Path):
        """Save transcript as JSON."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(transcript_data, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved transcript JSON: {output_path}")
    
    def save_transcript_vtt(self, transcript_data: Dict[str, Any], output_path: Path):
        """Save transcript as WebVTT format."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        vtt_content = "WEBVTT\n\n"
        
        for segment in transcript_data.get("segments", []):
            start = self._format_timestamp(segment["start"])
            end = self._format_timestamp(segment["end"])
            text = segment["text"]
            
            vtt_content += f"{start} --> {end}\n{text}\n\n"
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(vtt_content)
        
        logger.info(f"Saved transcript VTT: {output_path}")
    
    def save_transcript_srt(self, transcript_data: Dict[str, Any], output_path: Path):
        """Save transcript as SRT format."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        srt_content = ""
        
        for idx, segment in enumerate(transcript_data.get("segments", []), 1):
            start = self._format_timestamp_srt(segment["start"])
            end = self._format_timestamp_srt(segment["end"])
            text = segment["text"]
            
            srt_content += f"{idx}\n{start} --> {end}\n{text}\n\n"
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(srt_content)
        
        logger.info(f"Saved transcript SRT: {output_path}")
    
    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        """Format timestamp for VTT (HH:MM:SS.mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"
    
    @staticmethod
    def _format_timestamp_srt(seconds: float) -> str:
        """Format timestamp for SRT (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"



