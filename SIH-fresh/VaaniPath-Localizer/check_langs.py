from deep_translator import GoogleTranslator

try:
    # Get all supported languages
    langs = GoogleTranslator().get_supported_languages(as_dict=True)
    
    # Filter for Indian languages (manual list of common Indian languages/codes)
    indian_codes = [
        'hi', 'mr', 'ta', 'te', 'kn', 'ml', 'bn', 'gu', 'pa', 'ur', 'as', 'ne', 'sa', 'sd', 'or', # The 15 we know
        'doi', 'brx', 'ks', 'gom', 'kok', 'mai', 'mni', 'sat', 'mwr', 'bho', 'bgc', # The ones we use Gemini for
        'lus', 'kha', 'awa', 'hne', 'tcy' # Others: Mizo, Khasi, Awadhi, Chhattisgarhi, Tulu
    ]
    
    print("Supported languages in deep-translator:")
    for name, code in langs.items():
        if code in indian_codes:
            print(f"{name}: {code}")
            
except Exception as e:
    print(f"Error: {e}")
