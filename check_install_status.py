import importlib
import sys

packages = [
    "torch",
    "torchaudio",
    "torchvision",
    "transformers",
    "indic_nlp_library",
    "ctranslate2",
    "urduhack",
    "nltk",
    "pandas",
    "gradio",
    "sentencepiece",
    "fairseq",
    "TTS"
]

print(f"Python Version: {sys.version}")
print("-" * 30)

for package in packages:
    try:
        importlib.import_module(package)
        print(f"[OK] {package}")
    except ImportError as e:
        print(f"[MISSING] {package}: {e}")
    except Exception as e:
        print(f"[ERROR] {package}: {e}")
