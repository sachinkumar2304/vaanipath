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