from app.config import Settings
try:
    s = Settings()
    print("Settings loaded successfully")
except Exception as e:
    print(f"Error loading settings: {e}")
