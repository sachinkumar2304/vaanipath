import sys
import os

sys.path.append(os.getcwd())

try:
    print("Attempting to import app.api.v1.endpoints.processing...")
    from app.api.v1.endpoints import processing
    print("✅ Import successful!")
except Exception as e:
    print(f"❌ Import failed: {e}")
except SyntaxError as e:
    print(f"❌ SyntaxError: {e}")
