import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

try:
    print("Attempting to import app.models.user...")
    from app.models.user import UserCreate
    print("✅ Import successful!")
except Exception as e:
    print(f"❌ Import failed: {e}")
except SyntaxError as e:
    print(f"❌ SyntaxError: {e}")
