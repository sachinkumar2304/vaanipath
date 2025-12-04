"""
Dependency checker for the Localisation Engine
Checks for required Python packages in Python 3.11.9 environment
"""
import importlib
import sys

print(f"Python Version: {sys.version}")
print(f"Python Executable: {sys.executable}")
print("=" * 60)

# Core dependencies
core_packages = {
    "torch": "PyTorch - Deep Learning Framework",
    "transformers": "Hugging Face Transformers",
    "indic_nlp_library": "Indic NLP Library",
    "ctranslate2": "CTranslate2 - Fast Translation",
    "nltk": "Natural Language Toolkit",
    "sentencepiece": "SentencePiece - Tokenizer",
}

# Optional/problematic packages
optional_packages = {
    "fairseq": "Fairseq (Note: May fail on Windows)",
    "TTS": "Coqui TTS (Note: May fail on Windows)",
}

# Utility packages
utility_packages = {
    "pandas": "Data Analysis",
    "gradio": "Web UI Framework",
    "urduhack": "Urdu Language Processing",
}

def check_package(package_name, description):
    """Check if a package is installed and importable"""
    try:
        importlib.import_module(package_name)
        return True, "OK"
    except ImportError as e:
        return False, f"MISSING: {str(e)[:50]}"
    except Exception as e:
        return False, f"ERROR: {str(e)[:50]}"

print("\n📦 CORE DEPENDENCIES:")
print("-" * 60)
core_ok = True
for pkg, desc in core_packages.items():
    success, status = check_package(pkg, desc)
    icon = "✅" if success else "❌"
    print(f"{icon} {pkg:25} - {desc}")
    if not success:
        print(f"   └─ {status}")
        core_ok = False

print("\n📦 UTILITY PACKAGES:")
print("-" * 60)
for pkg, desc in utility_packages.items():
    success, status = check_package(pkg, desc)
    icon = "✅" if success else "❌"
    print(f"{icon} {pkg:25} - {desc}")
    if not success:
        print(f"   └─ {status}")

print("\n📦 OPTIONAL PACKAGES (Known Issues on Windows):")
print("-" * 60)
for pkg, desc in optional_packages.items():
    success, status = check_package(pkg, desc)
    icon = "✅" if success else "⚠️"
    print(f"{icon} {pkg:25} - {desc}")
    if not success:
        print(f"   └─ {status}")

print("\n" + "=" * 60)
if core_ok:
    print("✅ All core dependencies are installed!")
    print("⚠️  Note: fairseq and TTS may not be required depending on your use case")
else:
    print("❌ Some core dependencies are missing. Please install them.")
    print("   Run: py -3.11 -m pip install <package_name>")
print("=" * 60)
