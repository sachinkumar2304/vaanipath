from deep_translator import GoogleTranslator

def test_lang(code, name):
    try:
        translator = GoogleTranslator(source='en', target=code)
        res = translator.translate("Hello world")
        print(f"✅ {name} ({code}): {res}")
    except Exception as e:
        print(f"❌ {name} ({code}) Failed: {e}")

print("Testing Google Translate Support...")
test_lang('doi', 'Dogri')
test_lang('gom', 'Konkani (Goan)')
test_lang('kok', 'Konkani (Generic)')
test_lang('brx', 'Bodo')
test_lang('mai', 'Maithili')
test_lang('mni', 'Manipuri')
test_lang('sat', 'Santali')
test_lang('bho', 'Bhojpuri')
