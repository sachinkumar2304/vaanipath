import sys
import os

sys.path.append(os.getcwd())

try:
    print("Attempting to import app.models.processing...")
    from app.models.processing import VideoProcessRequest
    print("✅ Import successful!")
except Exception as e:
    print(f"❌ Import failed: {e}")
except SyntaxError as e:
    print(f"❌ SyntaxError: {e}")
