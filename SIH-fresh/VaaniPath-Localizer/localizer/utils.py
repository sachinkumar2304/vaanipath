import os
import logging
from multiprocessing import cpu_count


def mkdir_p(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def safe_filename(name: str) -> str:
    return "".join(c if c.isalnum() or c in ("_", "-", ".") else "_" for c in name)


def get_worker_count() -> int:
    try:
        cpus = cpu_count() or 2
    except Exception:
        cpus = 2
    return max(1, cpus - 1)


def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
import os
import logging
from multiprocessing import cpu_count


def mkdir_p(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def safe_filename(name: str) -> str:
    return "".join(c if c.isalnum() or c in ("_", "-", ".") else "_" for c in name)


def get_worker_count() -> int:
    try:
        cpus = cpu_count() or 2
    except Exception:
        cpus = 2
    return max(1, cpus - 1)


def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter(
            fmt="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
            datefmt="%H:%M:%S",
        )
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger


def _discover_ffbin(bin_name: str) -> str:
    # 1. Try environment override first
    env_key = "FFMPEG_EXE" if bin_name == "ffmpeg" else "FFPROBE_EXE"
    p = os.environ.get(env_key)
    if p and os.path.exists(p):
        return p

    # 2. Try project-local directory (Robust Fix)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    local_bin = os.path.join(project_root, "ffmpeg-8.0.1-essentials_build", "bin", f"{bin_name}.exe")
    if os.path.exists(local_bin):
        return local_bin

    # 3. Try Winget installation directory
    la = os.environ.get("LOCALAPPDATA", "")
    winget_pkg = os.path.join(la, "Microsoft", "WinGet", "Packages")
    if os.path.isdir(winget_pkg):
        try:
            for root, dirs, files in os.walk(winget_pkg):
                if bin_name + ".exe" in files:
                    candidate = os.path.join(root, bin_name + ".exe")
                    return candidate
        except Exception:
            pass

    # Fallback to plain name in PATH
    return bin_name


FFMPEG = _discover_ffbin("ffmpeg")
FFPROBE = _discover_ffbin("ffprobe")


def generate_vtt(chunks: list, output_path: str) -> str:
    """Generate a WebVTT file from transcript chunks."""
    def format_time(seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds * 1000) % 1000)
        return f"{h:02}:{m:02}:{s:02}.{ms:03}"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("WEBVTT\n\n")
        for chunk in chunks:
            start = format_time(chunk["start"])
            end = format_time(chunk["end"])
            # Use translated text if available, otherwise original text
import os
import logging
from multiprocessing import cpu_count


def mkdir_p(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def safe_filename(name: str) -> str:
    return "".join(c if c.isalnum() or c in ("_", "-", ".") else "_" for c in name)


def get_worker_count() -> int:
    try:
        cpus = cpu_count() or 2
    except Exception:
        cpus = 2
    return max(1, cpus - 1)


def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter(
            fmt="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
            datefmt="%H:%M:%S",
        )
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger


def _discover_ffbin(bin_name: str) -> str:
    # 1. Try environment override first
    env_key = "FFMPEG_EXE" if bin_name == "ffmpeg" else "FFPROBE_EXE"
    p = os.environ.get(env_key)
    if p and os.path.exists(p):
        return p

    # 2. Try project-local directory (Robust Fix)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    local_bin = os.path.join(project_root, "ffmpeg-8.0.1-essentials_build", "bin", f"{bin_name}.exe")
    if os.path.exists(local_bin):
        return local_bin

    # 3. Try Winget installation directory
    la = os.environ.get("LOCALAPPDATA", "")
    winget_pkg = os.path.join(la, "Microsoft", "WinGet", "Packages")
    if os.path.isdir(winget_pkg):
        try:
            for root, dirs, files in os.walk(winget_pkg):
                if bin_name + ".exe" in files:
                    candidate = os.path.join(root, bin_name + ".exe")
                    return candidate
        except Exception:
            pass

    # Fallback to plain name in PATH
    return bin_name


FFMPEG = _discover_ffbin("ffmpeg")
FFPROBE = _discover_ffbin("ffprobe")


def generate_vtt(chunks: list, output_path: str) -> str:
    """Generate a WebVTT file from transcript chunks."""
    def format_time(seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds * 1000) % 1000)
        return f"{h:02}:{m:02}:{s:02}.{ms:03}"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("WEBVTT\n\n")
        for chunk in chunks:
            start = format_time(chunk["start"])
            end = format_time(chunk["end"])
            # Use translated text if available, otherwise original text
            text = chunk.get("text_translated", chunk.get("text", "")).strip()
            if text:
                f.write(f"{start} --> {end}\n{text}\n\n")
    return output_path


def smart_split_text(text: str, max_chars: int = 40) -> list[str]:
    """
    Split text into smaller chunks based on punctuation and length.
    Ensures no chunk exceeds max_chars if possible.
    """
    import re
    
    if not text:
        return []
        
    # 1. Initial split by sentence terminators
    # Match periods, question marks, exclamations, and Danda (।)
    raw_sentences = re.split(r'([.?!।|]+)', text)
    
    sentences = []
    current_sent = ""
    for part in raw_sentences:
        if re.match(r'[.?!।|]+', part):
            current_sent += part
            if current_sent.strip():
                sentences.append(current_sent.strip())
            current_sent = ""
        else:
            current_sent += part
    if current_sent.strip():
        sentences.append(current_sent.strip())
        
    if not sentences:
        sentences = [text]
        
    # 2. Further split long sentences
    final_chunks = []
    for sent in sentences:
        if len(sent) <= max_chars:
            final_chunks.append(sent)
            continue
            
        # Split by comma first
        comma_parts = sent.split(',')
        current_part = ""
        
        for part in comma_parts:
            # Add comma back if it wasn't the last part
            part = part.strip()
            if not part:
                continue
                
            candidate = f"{current_part}, {part}" if current_part else part
            
            if len(candidate) <= max_chars:
                current_part = candidate
            else:
                if current_part:
                    final_chunks.append(current_part + ",")
                
                # If the part itself is too long, split by words
                if len(part) > max_chars:
                    words = part.split(' ')
                    current_word_chunk = ""
                    for word in words:
                        if len(current_word_chunk) + len(word) + 1 <= max_chars:
                            current_word_chunk += (" " if current_word_chunk else "") + word
                        else:
                            if current_word_chunk:
                                final_chunks.append(current_word_chunk)
                            current_word_chunk = word
                    if current_word_chunk:
                        current_part = current_word_chunk
                else:
                    current_part = part
                    
        if current_part:
            final_chunks.append(current_part)
            
    return final_chunks