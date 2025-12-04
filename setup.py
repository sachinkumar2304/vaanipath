"""Setup script for localisation engine."""
import os
import subprocess
from pathlib import Path


def check_ffmpeg():
    """Check if FFmpeg is installed."""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        print("✓ FFmpeg is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ FFmpeg is not installed. Please install FFmpeg.")
        print("  Ubuntu/Debian: sudo apt-get install ffmpeg")
        print("  macOS: brew install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        return False


def check_python_version():
    """Check Python version."""
    import sys
    if sys.version_info >= (3, 10):
        print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} is installed")
        return True
    else:
        print(f"✗ Python 3.10+ required. Current version: {sys.version_info.major}.{sys.version_info.minor}")
        return False


def create_directories():
    """Create necessary directories."""
    directories = [
        "storage",
        "storage/jobs",
        "storage/uploads"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")


def main():
    """Run setup checks."""
    print("Localisation Engine Setup")
    print("=" * 40)
    
    checks_passed = True
    
    # Check Python version
    if not check_python_version():
        checks_passed = False
    
    # Check FFmpeg
    if not check_ffmpeg():
        checks_passed = False
    
    # Create directories
    print("\nCreating directories...")
    create_directories()
    
    print("\n" + "=" * 40)
    if checks_passed:
        print("✓ Setup complete! You can now install dependencies:")
        print("  pip install -r requirements.txt")
        print("\nThen run the application:")
        print("  uvicorn app.main:app --reload")
    else:
        print("⚠ Some checks failed. Please fix the issues above.")
    
    print("\nNote: You may also need to install:")
    print("  - IndicTrans2: git clone https://github.com/AI4Bharat/IndicTrans2.git")
    print("  - Redis (for Celery): sudo apt-get install redis-server")


if __name__ == "__main__":
    main()



