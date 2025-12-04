import importlib.util
import sys

optional_packages = [
    "TTS",
    "IndicTrans2", # Check if this is the package name
    "indictrans"   # Alternative name
]

results = {}
for package in optional_packages:
    results[package] = importlib.util.find_spec(package) is not None

print(f"Optional packages status: {results}")
