// 22 Official Indian Languages
export const INDIAN_LANGUAGES = [
    { code: 'en-IN', name: 'English', native: 'English' },
    { code: 'hi-IN', name: 'Hindi', native: 'हिन्दी' },
    { code: 'bn-IN', name: 'Bengali', native: 'বাংলা' },
    { code: 'te-IN', name: 'Telugu', native: 'తెలుగు' },
    { code: 'mr-IN', name: 'Marathi', native: 'मराठी' },
    { code: 'ta-IN', name: 'Tamil', native: 'தமிழ்' },
    { code: 'gu-IN', name: 'Gujarati', native: 'ગુજરાતી' },
    { code: 'kn-IN', name: 'Kannada', native: 'ಕನ್ನಡ' },
    { code: 'ml-IN', name: 'Malayalam', native: 'മലയാളം' },
    { code: 'or-IN', name: 'Odia', native: 'ଓଡ଼ିଆ' },
    { code: 'pa-IN', name: 'Punjabi', native: 'ਪੰਜਾਬੀ' },
    { code: 'as-IN', name: 'Assamese', native: 'অসমীয়া' },
    { code: 'ur-IN', name: 'Urdu', native: 'اردو' },
    { code: 'sa-IN', name: 'Sanskrit', native: 'संस्कृतम्' },
    { code: 'ks-IN', name: 'Kashmiri', native: 'कॉशुर' },
    { code: 'sd-IN', name: 'Sindhi', native: 'سنڌي' },
    { code: 'ne-IN', name: 'Nepali', native: 'नेपाली' },
    { code: 'kok-IN', name: 'Konkani', native: 'कोंकणी' },
    { code: 'mni-IN', name: 'Manipuri', native: 'মৈতৈলোন্' },
    { code: 'doi-IN', name: 'Dogri', native: 'डोगरी' },
    { code: 'sat-IN', name: 'Santali', native: 'ᱥᱟᱱᱛᱟᱲᱤ' },
    { code: 'mai-IN', name: 'Maithili', native: 'मैथिली' }
] as const;

export type LanguageCode = typeof INDIAN_LANGUAGES[number]['code'];
