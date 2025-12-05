from deep_translator import GoogleTranslator

def test_deep_translator():
    text = "Hello, how are you?"
    target_lang = "hi"
    print(f"Translating '{text}' to '{target_lang}'...")
    try:
        translator = GoogleTranslator(source='auto', target=target_lang)
        result = translator.translate(text)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_deep_translator()
