import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

try:
    print("Attempting to import localizer.api...")
    from localizer import api
    print("Import successful!")
    
    if hasattr(api, 'app'):
        print("Found 'app' object in api module.")
        print(f"Type of app: {type(api.app)}")
    else:
        print("ERROR: 'app' object NOT found in api module!")
        print(f"Available attributes: {dir(api)}")

except Exception as e:
    print(f"Import failed with error: {e}")
    import traceback
    traceback.print_exc()
