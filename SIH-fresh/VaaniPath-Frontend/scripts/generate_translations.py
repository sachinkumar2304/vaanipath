import json
import os
from deep_translator import GoogleTranslator
import time

def translate_text(text, target_lang):
    if target_lang == 'en': return text
    try:
        # Use deep_translator
        return GoogleTranslator(source='auto', target=target_lang).translate(text)
    except Exception as e:
        print(f"Error translating '{text}' to {target_lang}: {e}")
        return text

def translate_dict(data, target_lang):
    new_data = {}
    for key, value in data.items():
        if isinstance(value, dict):
            new_data[key] = translate_dict(value, target_lang)
        elif isinstance(value, str):
            new_data[key] = translate_text(value, target_lang)
    return new_data

locales_dir = "../src/i18n/locales"
os.makedirs(locales_dir, exist_ok=True)

# English base
en_data = {
  "common": {
    "login": "Login",
    "signup": "Sign Up",
    "logout": "Logout",
    "settings": "Settings",
    "profile": "Profile",
    "home": "Home",
    "dashboard": "Dashboard",
    "myCourses": "My Courses",
    "browseCourses": "Browse Courses",
    "uploadContent": "Upload Content",
    "createQuiz": "Create Quiz",
    "studentDoubts": "Student Doubts",
    "askDoubts": "Ask Doubts",
    "community": "Community",
    "rewards": "Rewards",
    "aiRoadmap": "AI Roadmap",
    "podcast": "Podcast",
    "feedback": "Feedback",
    "studentLogin": "Student Login",
    "teacherLogin": "Teacher Login",
    "getStarted": "Get Started",
    "welcome": "Welcome",
    "points": "Points",
    "language": "Language",
    "enrolled": "Enrolled",
    "viewCourse": "View Course",
    "continueLearning": "Continue Learning",
    "completed": "Completed",
    "totalVideos": "Total Videos",
    "totalStudents": "Students Enrolled",
    "totalViews": "Total Views",
    "recentCourses": "Recent Courses",
    "createCourse": "Create Course",
    "uploadVideo": "Upload Video",
    "courseTitle": "Course Title",
    "description": "Description",
    "selectLanguage": "Select Language",
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete",
    "edit": "Edit",
    "submit": "Submit",
    "next": "Next",
    "previous": "Previous",
    "search": "Search",
    "filter": "Filter",
    "all": "All",
    "loading": "Loading...",
    "error": "Error",
    "success": "Success"
  },
  "header": {
    "title": "VAANIपथ"
  },
  "landing": {
    "heroTitle": "Learn in Your Language",
    "heroSubtitle": "AI-powered multilingual education platform",
    "features": "Features",
    "testimonials": "Testimonials",
    "pricing": "Pricing",
    "contact": "Contact",
    "multilingualSupport": "Multilingual Support",
    "multilingualDesc": "Learn in your preferred language with support for Hindi, Bengali, Telugu, Tamil, Marathi, and more",
    "videoLectures": "Video Lectures",
    "videoLecturesDesc": "High-quality video content translated to your local language in real-time",
    "expertTeachers": "Expert Teachers",
    "expertTeachersDesc": "Learn from experienced educators from across India",
    "regionalContent": "Regional Content",
    "regionalContentDesc": "Content tailored to your region and cultural context",
    "aiTranslation": "AI-powered instant translation",
    "selfPaced": "Learn at your own pace",
    "progressTracking": "Progress tracking and certificates",
    "interactiveLearning": "Interactive learning experience",
    "mobileFriendly": "Mobile-friendly platform",
    "freeAccess": "Free and accessible education",
    "aiPoweredBadge": "AI-Powered Multilingual Learning",
    "learnInYour": "Learn in Your",
    "localLanguage": "Local Language",
    "heroDescription": "VAANIपथ translates vocational content into regional Indian languages, making quality education accessible to everyone, everywhere. Experience the future of learning today.",
    "whyChoose": "Why Choose",
    "educationBoundaries": "Education Should Have",
    "noBoundaries": "No Boundaries",
    "missionStatement": "We believe every student deserves access to quality education in their mother tongue. VAANIपथ uses advanced AI to make this a reality, bridging the gap between aspiration and opportunity.",
    "globalStandard": "Global Standard",
    "readyToStart": "Ready to Start Learning?",
    "joinStudents": "Join thousands of students transforming their future with VaaniPath.",
    "createAccount": "Create Your Account",
    "copyright": "© 2025 VAANIपथ. Making Vocational Skills accessible in every language."
  },
  "auth": {
    "email": "Email",
    "password": "Password",
    "confirmPassword": "Confirm Password",
    "name": "Name",
    "forgotPassword": "Forgot Password?",
    "dontHaveAccount": "Don't have an account?",
    "alreadyHaveAccount": "Already have an account?",
    "loginTitle": "Login to your account",
    "signupTitle": "Create your account",
    "studentPortal": "Student Portal",
    "teacherPortal": "Teacher Portal",
    "studentSubtitle": "Continue your learning journey",
    "teacherSubtitle": "Manage your courses and inspire students",
    "welcomeBack": "Welcome Back",
    "readyToLearn": "Ready to learn something new today?",
    "joinVaaniPath": "Join VaaniPath",
    "createAccountDesc": "Create your free account to get started",
    "educatorLogin": "Educator Login",
    "enterCredentials": "Please enter your credentials",
    "secureAccess": "Secure Access",
    "teacherAccessNote": "Teacher accounts are administratively managed. Contact support for access issues.",
    "backToHome": "Back to Home",
    "startLearning": "Start Learning",
    "loggingIn": "Logging in...",
    "createFreeAccount": "Create Free Account",
    "creatingAccount": "Creating Account...",
    "loginToDashboard": "Login to Dashboard",
    "verifying": "Verifying...",
    "fullName": "Full Name",
    "emailAddress": "Email Address",
    "studentEmail": "Student Email",
    "confirm": "Confirm",
    "preferredLanguage": "Preferred Language",
    "selectLanguage": "Select your language",
    "state": "State",
    "city": "City",
    "region": "Region"
  },
  "dashboard": {
    "welcomeMessage": "Ready to continue your learning journey? Pick up where you left off or discover something new.",
    "noDescription": "No description available"
  },
  "myCourses": {
    "title": "My Courses",
    "subtitle": "Continue your learning journey",
    "loading": "Loading your courses...",
    "untitled": "Untitled Course",
    "videos": "videos",
    "done": "done",
    "progress": "Progress",
    "continue": "Continue Learning",
    "noCourses": "No courses yet",
    "enrollPrompt": "Enroll in courses to start your learning journey",
    "browse": "Browse Courses"
  },
  "footer": {
    "description": "AI-powered multilingual content localization engine making education accessible in your native language.",
    "quickLinks": "Quick Links",
    "contactDevelopers": "Contact Developers",
    "connectWithUs": "Connect With Us",
    "home": "Home",
    "courses": "Courses",
    "community": "Community",
    "feedback": "Feedback",
    "allRightsReserved": "All rights reserved."
  },
  "browseCourses": {
    "title": "Discover Courses",
    "subtitle": "Browse and enroll in courses to start learning",
    "searchPlaceholder": "Search courses...",
    "subject": "Subject",
    "allSubjects": "All Subjects",
    "language": "Language",
    "allLanguages": "All Languages",
    "loading": "Loading courses...",
    "enrolled": "Enrolled",
    "by": "by",
    "noDescription": "No description provided",
    "noCourses": "No courses found",
    "adjustFilters": "Try adjusting your search or filters"
  },
  "teacherDashboard": {
    "welcomeTeacher": "Welcome",
    "subtitle": "Manage your courses and inspire students across India",
    "createCourse": "Create Course",
    "createCourseDesc": "Start a new course",
    "myCourses": "My Courses",
    "manageContent": "Manage your content",
    "analytics": "Analytics",
    "viewPerformance": "View performance",
    "studentDoubts": "Student Doubts",
    "answerQuestions": "Answer questions",
    "totalVideos": "Total Videos",
    "totalStudents": "Total Students",
    "totalViews": "Total Views",
    "recentCourses": "Recent Courses",
    "viewAll": "View All",
    "edit": "Edit",
    "view": "View",
    "students": "students",
    "noCourses": "No courses yet",
    "createFirst": "Create your first course to get started"
  }
}

# Hindi Translations
hi_data = {
    "common": {
        "login": "लॉगिन", "signup": "साइन अप", "logout": "लॉग आउट", "settings": "सेटिंग्स",
        "profile": "प्रोफाइल", "home": "होम", "dashboard": "डैशबोर्ड", "myCourses": "मेरे कोर्स",
        "browseCourses": "कोर्स ब्राउज़ करें", "uploadContent": "कंटेंट अपलोड करें", "createQuiz": "क्विज़ बनाएं",
        "studentDoubts": "छात्रों के सवाल", "askDoubts": "सवाल पूछें", "community": "कम्युनिटी",
        "rewards": "इनाम", "aiRoadmap": "AI रोडमैप", "podcast": "पॉडकास्ट", "feedback": "फीडबैक",
        "studentLogin": "छात्र लॉगिन", "teacherLogin": "शिक्षक लॉगिन", "getStarted": "शुरू करें",
        "welcome": "स्वागत है", "points": "अंक", "language": "भाषा", "enrolled": "नामांकित",
        "viewCourse": "कोर्स देखें", "continueLearning": "सीखना जारी रखें", "completed": "पूरा हुआ",
        "totalVideos": "कुल वीडियो", "totalStudents": "कुल छात्र", "totalViews": "कुल व्यूज",
        "recentCourses": "हाल के कोर्स", "createCourse": "कोर्स बनाएं", "uploadVideo": "वीडियो अपलोड करें",
        "courseTitle": "कोर्स का शीर्षक", "description": "विवरण", "selectLanguage": "भाषा चुनें",
        "save": "सेव करें", "cancel": "रद्द करें", "delete": "हटाएं", "edit": "एडिट करें",
        "submit": "सबमिट करें", "next": "अगला", "previous": "पिछला", "search": "खोजें",
        "filter": "फिल्टर", "all": "सभी", "loading": "लोड हो रहा है...", "error": "त्रुटि", "success": "सफल"
    },
    "header": {"title": "VAANIपथ"},
    "landing": {
        "heroTitle": "अपनी भाषा में सीखें", "heroSubtitle": "AI-संचालित बहुभाषी शिक्षा मंच",
        "features": "विशेषताएं", "testimonials": "प्रशंसापत्र", "pricing": "मूल्य निर्धारण", "contact": "संपर्क",
        "multilingualSupport": "बहुभाषी समर्थन",
        "multilingualDesc": "अपनी पसंदीदा भाषा में सीखें, हिंदी, बंगाली, तेलुगु, तमिल, मराठी और अधिक के समर्थन के साथ",
        "videoLectures": "वीडियो व्याख्यान",
        "videoLecturesDesc": "वास्तविक समय में आपकी स्थानीय भाषा में अनुवादित उच्च गुणवत्ता वाली वीडियो सामग्री",
        "expertTeachers": "विशेषज्ञ शिक्षक",
        "expertTeachersDesc": "भारत भर के अनुभवी शिक्षकों से सीखें",
        "regionalContent": "क्षेत्रीय सामग्री",
        "regionalContentDesc": "आपके क्षेत्र और सांस्कृतिक संदर्भ के अनुरूप सामग्री",
        "aiTranslation": "AI-संचालित तत्काल अनुवाद",
        "selfPaced": "अपनी गति से सीखें",
        "progressTracking": "प्रगति ट्रैकिंग और प्रमाण पत्र",
        "interactiveLearning": "इंटरैक्टिव सीखने का अनुभव",
        "mobileFriendly": "मोबाइल-फ्रेंडली प्लेटफॉर्म",
        "freeAccess": "मुफ्त और सुलभ शिक्षा",
        "aiPoweredBadge": "AI-संचालित बहुभाषी शिक्षा",
        "learnInYour": "अपनी",
        "localLanguage": "स्थानीय भाषा में सीखें",
        "heroDescription": "VAANIपथ व्यावसायिक सामग्री का क्षेत्रीय भारतीय भाषाओं में अनुवाद करता है, जिससे गुणवत्तापूर्ण शिक्षा सभी के लिए, हर जगह सुलभ हो जाती है। आज ही सीखने के भविष्य का अनुभव करें।",
        "whyChoose": "क्यों चुनें",
        "educationBoundaries": "शिक्षा में होनी चाहिए",
        "noBoundaries": "कोई सीमा नहीं",
        "missionStatement": "हम मानते हैं कि हर छात्र अपनी मातृभाषा में गुणवत्तापूर्ण शिक्षा का हकदार है। VAANIपथ इसे वास्तविकता बनाने के लिए उन्नत AI का उपयोग करता है, आकांक्षा और अवसर के बीच की खाई को पाटता है।",
        "globalStandard": "वैश्विक मानक",
        "readyToStart": "सीखना शुरू करने के लिए तैयार हैं?",
        "joinStudents": "हजारों छात्रों के साथ जुड़ें जो VaaniPath के साथ अपना भविष्य बदल रहे हैं।",
        "createAccount": "अपना खाता बनाएं",
        "copyright": "© 2025 VAANIपथ. हर भाषा में व्यावसायिक कौशल सुलभ बनाना।"
    },
    "auth": {
        "email": "ईमेल", "password": "पासवर्ड", "confirmPassword": "पासवर्ड की पुष्टि करें", "name": "नाम",
        "forgotPassword": "पासवर्ड भूल गए?", "dontHaveAccount": "खाता नहीं है?", "alreadyHaveAccount": "पहले से खाता है?",
        "loginTitle": "अपने खाते में लॉगिन करें", "signupTitle": "अपना खाता बनाएं"
    },
    "dashboard": {
        "welcomeMessage": "अपनी सीखने की यात्रा जारी रखने के लिए तैयार हैं? जहां छोड़ा था वहां से शुरू करें या कुछ नया खोजें।",
        "noDescription": "कोई विवरण उपलब्ध नहीं है"
    },
    "myCourses": {
        "title": "मेरे कोर्स",
        "subtitle": "अपनी सीखने की यात्रा जारी रखें",
        "loading": "आपके कोर्स लोड हो रहे हैं...",
        "untitled": "शीर्षकहीन कोर्स",
        "videos": "वीडियो",
        "done": "पूरा हुआ",
        "progress": "प्रगति",
        "continue": "सीखना जारी रखें",
        "noCourses": "अभी तक कोई कोर्स नहीं",
        "enrollPrompt": "अपनी सीखने की यात्रा शुरू करने के लिए कोर्स में नामांकन करें",
        "browse": "कोर्स ब्राउज़ करें"
    }
}

# Bengali Translations
bn_data = {
    "common": {
        "login": "লগইন", "signup": "সাইন আপ", "logout": "লগ আউট", "settings": "সেটিংস",
        "profile": "প্রোফাইল", "home": "হোম", "dashboard": "ড্যাশবোর্ড", "myCourses": "আমার কোর্স",
        "browseCourses": "কোর্স ব্রাউজ করুন", "uploadContent": "কন্টেন্ট আপলোড", "createQuiz": "কুইজ তৈরি করুন",
        "studentDoubts": "ছাত্রদের প্রশ্ন", "askDoubts": "প্রশ্ন জিজ্ঞাসা করুন", "community": "কমিউনিটি",
        "rewards": "পুরস্কার", "aiRoadmap": "AI রোডম্যাপ", "podcast": "পডকাস্ট", "feedback": "মতামত",
        "studentLogin": "ছাত্র লগইন", "teacherLogin": "শিক্ষক লগইন", "getStarted": "শুরু করুন",
        "welcome": "স্বাগতম", "points": "পয়েন্ট", "language": "ভাষা", "enrolled": "নথিভুক্ত",
        "viewCourse": "কোর্স দেখুন", "continueLearning": "শেখা চালিয়ে যান", "completed": "সম্পন্ন",
        "totalVideos": "মোট ভিডিও", "totalStudents": "মোট ছাত্র", "totalViews": "মোট ভিউ",
        "recentCourses": "সাম্প্রতিক কোর্স", "createCourse": "কোর্স তৈরি করুন", "uploadVideo": "ভিডিও আপলোড",
        "courseTitle": "কোর্সের শিরোনাম", "description": "বিবরণ", "selectLanguage": "ভাষা নির্বাচন করুন",
        "save": "সংরক্ষণ", "cancel": "বাতিল", "delete": "মুছুন", "edit": "সম্পাদনা",
        "submit": "জমা দিন", "next": "পরবর্তী", "previous": "পূর্ববর্তী", "search": "অনুসন্ধান",
        "filter": "ফিল্টার", "all": "সব", "loading": "লোড হচ্ছে...", "error": "ত্রুটি", "success": "সফল"
    },
    "header": {"title": "VAANIपथ"},
    "landing": {
        "heroTitle": "আপনার নিজের ভাষায় শিখুন", "heroSubtitle": "AI-চালিত বহুভাষিক শিক্ষা প্ল্যাটফর্ম",
        "features": "বৈশিষ্ট্য", "testimonials": "প্রশংসাপত্র", "pricing": "মূল্য", "contact": "যোগাযোগ"
    },
    "auth": {
        "email": "ইমেল", "password": "পাসওয়ার্ড", "confirmPassword": "পাসওয়ার্ড নিশ্চিত করুন", "name": "নাম",
        "forgotPassword": "পাসওয়ার্ড ভুলে গেছেন?", "dontHaveAccount": "অ্যাকাউন্ট নেই?", "alreadyHaveAccount": "ইতিমধ্যে একটি অ্যাকাউন্ট আছে?",
        "loginTitle": "আপনার অ্যাকাউন্টে লগইন করুন", "signupTitle": "আপনার অ্যাকাউন্ট তৈরি করুন"
    }
}

# Marathi Translations
mr_data = {
    "common": {
        "login": "लॉगिन", "signup": "साइन अप", "logout": "लॉग आउट", "settings": "सेटिंग्ज",
        "profile": "प्रोफाइल", "home": "होम", "dashboard": "डॅशबोर्ड", "myCourses": "माझे कोर्सेस",
        "browseCourses": "कोर्सेस ब्राउझ करा", "uploadContent": "सामग्री अपलोड करा", "createQuiz": "क्विझ तयार करा",
        "studentDoubts": "विद्यार्थ्यांचे प्रश्न", "askDoubts": "प्रश्न विचारा", "community": "समुदाय",
        "rewards": "बक्षिसे", "aiRoadmap": "AI रोडमॅप", "podcast": "पॉडकास्ट", "feedback": "प्रतिक्रिया",
        "studentLogin": "विद्यार्थी लॉगिन", "teacherLogin": "शिक्षक लॉगिन", "getStarted": "सुरू करा",
        "welcome": "स्वागत आहे", "points": "गुण", "language": "भाषा", "enrolled": "नोंदणीकृत",
        "viewCourse": "कोर्स पहा", "continueLearning": "शिकणे सुरू ठेवा", "completed": "पूर्ण",
        "totalVideos": "एकूण व्हिडिओ", "totalStudents": "एकूण विद्यार्थी", "totalViews": "एकूण व्ह्यूज",
        "recentCourses": "अलीकडील कोर्सेस", "createCourse": "कोर्स तयार करा", "uploadVideo": "व्हिडिओ अपलोड करा",
        "courseTitle": "कोर्सचे शीर्षक", "description": "वर्णन", "selectLanguage": "भाषा निवडा",
        "save": "जतन करा", "cancel": "रद्द करा", "delete": "काढून टाका", "edit": "संपादित करा",
        "submit": "सबमिट करा", "next": "पुढील", "previous": "मागील", "search": "शोधा",
        "filter": "फिल्टर", "all": "सर्व", "loading": "लोड होत आहे...", "error": "त्रुटी", "success": "यशस्वी"
    },
    "header": {"title": "VAANIपथ"},
    "landing": {
        "heroTitle": "आपल्या भाषेत शिका", "heroSubtitle": "AI-समर्थित बहुभाषिक शिक्षण प्लॅटफॉर्म",
        "features": "वैशिष्ट्ये", "testimonials": "प्रशंसापत्रे", "pricing": "किंमत", "contact": "संपर्क"
    },
    "auth": {
        "email": "ईमेल", "password": "पासवर्ड", "confirmPassword": "पासवर्डची पुष्टी करा", "name": "नाव",
        "forgotPassword": "पासवर्ड विसरलात?", "dontHaveAccount": "खाते नाही?", "alreadyHaveAccount": "आधीच खाते आहे?",
        "loginTitle": "आपल्या खात्यात लॉगिन करा", "signupTitle": "आपले खाते तयार करा"
    }
}

# Tamil Translations
ta_data = {
    "common": {
        "login": "உள்நுழைய", "signup": "பதிவு செய்க", "logout": "வெளியேறு", "settings": "அமைப்புகள்",
        "profile": "சுயவிவரம்", "home": "முகப்பு", "dashboard": "டாஷ்போர்டு", "myCourses": "எனது படிப்புகள்",
        "browseCourses": "படிப்புகளை உலாவுக", "uploadContent": "உள்ளடக்கத்தை பதிவேற்றவும்", "createQuiz": "வினாடி வினா உருவாக்கவும்",
        "studentDoubts": "மாணவர் சந்தேகங்கள்", "askDoubts": "சந்தேகங்களைக் கேளுங்கள்", "community": "சமூகம்",
        "rewards": "வெகுமதிகள்", "aiRoadmap": "AI சாலை வரைபடம்", "podcast": "பாட்காஸ்ட்", "feedback": "கருத்து",
        "studentLogin": "மாணவர் உள்நுழைவு", "teacherLogin": "ஆசிரியர் உள்நுழைவு", "getStarted": "தொடங்குங்கள்",
        "welcome": "வரவேற்கிறோம்", "points": "புள்ளிகள்", "language": "மொழி", "enrolled": "பதிவுசெய்யப்பட்டது",
        "viewCourse": "படிப்பைப் பார்க்கவும்", "continueLearning": "கற்றலைத் தொடரவும்", "completed": "முடிந்தது",
        "totalVideos": "மொத்த வீடியோக்கள்", "totalStudents": "மொத்த மாணவர்கள்", "totalViews": "மொத்த பார்வைகள்",
        "recentCourses": "சமீபத்திய படிப்புகள்", "createCourse": "படிப்பை உருவாக்கவும்", "uploadVideo": "வீடியோவை பதிவேற்றவும்",
        "courseTitle": "படிப்பு தலைப்பு", "description": "விளக்கம்", "selectLanguage": "மொழியைத் தேர்ந்தெடுக்கவும்",
        "save": "சேமி", "cancel": "ரத்துசெய்", "delete": "அழி", "edit": "திருத்து",
        "submit": "சமர்ப்பிக்கவும்", "next": "அடுத்து", "previous": "முந்தைய", "search": "தேடு",
        "filter": "வடிகட்டி", "all": "அனைத்தும்", "loading": "ஏற்றுகிறது...", "error": "பிழை", "success": "வெற்றி"
    },
    "header": {"title": "VAANIपथ"},
    "landing": {
        "heroTitle": "உங்கள் மொழியில் கற்றுக்கொள்ளுங்கள்", "heroSubtitle": "AI-இயங்கும் பன்மொழி கல்வி தளம்",
        "features": "அம்சங்கள்", "testimonials": "சான்றுகள்", "pricing": "விலை", "contact": "தொடர்பு"
    },
    "auth": {
        "email": "மின்னஞ்சல்", "password": "கடவுச்சொல்", "confirmPassword": "கடவுச்சொல்லை உறுதிப்படுத்தவும்", "name": "பெயர்",
        "forgotPassword": "கடவுச்சொல்லை மறந்துவிட்டீர்களா?", "dontHaveAccount": "கணக்கு இல்லையா?", "alreadyHaveAccount": "ஏற்கனவே கணக்கு உள்ளதா?",
        "loginTitle": "உங்கள் கணக்கில் உள்நுழையவும்", "signupTitle": "உங்கள் கணக்கை உருவாக்கவும்"
    }
}

# Telugu Translations
te_data = {
    "common": {
        "login": "లాగిన్", "signup": "సైన్ అప్", "logout": "లాగ్ అవుట్", "settings": "సెట్టింగ్‌లు",
        "profile": "ప్రొఫైల్", "home": "హోమ్", "dashboard": "డ్యాష్‌బోర్డ్", "myCourses": "నా కోర్సులు",
        "browseCourses": "కోర్సులను బ్రౌజ్ చేయండి", "uploadContent": "కంటెంట్‌ను అప్‌లోడ్ చేయండి", "createQuiz": "క్విజ్ సృష్టించండి",
        "studentDoubts": "విద్యార్థి సందేహాలు", "askDoubts": "సందేహాలు అడగండి", "community": "కమ్యూనిటీ",
        "rewards": "బహుమతులు", "aiRoadmap": "AI రోడ్‌మ్యాప్", "podcast": "పాడ్‌కాస్ట్", "feedback": "అభిప్రాయం",
        "studentLogin": "విద్యార్థి లాగిన్", "teacherLogin": "టీచర్ లాగిన్", "getStarted": "ప్రారంభించండి",
        "welcome": "స్వాగతం", "points": "పాయింట్లు", "language": "భాష", "enrolled": "నమోదు చేయబడింది",
        "viewCourse": "కోర్సును వీక్షించండి", "continueLearning": "నేర్చుకోవడం కొనసాగించండి", "completed": "పూర్తయింది",
        "totalVideos": "మొత్తం వీడియోలు", "totalStudents": "మొత్తం విద్యార్థులు", "totalViews": "మొత్తం వీక్షణలు",
        "recentCourses": "ఇటీవలి కోర్సులు", "createCourse": "కోర్సును సృష్టించండి", "uploadVideo": "వీడియోను అప్‌లోడ్ చేయండి",
        "courseTitle": "కోర్సు శీర్షిక", "description": "వివరణ", "selectLanguage": "భాషను ఎంచుకోండి",
        "save": "సేవ్ చేయండి", "cancel": "రద్దు చేయండి", "delete": "తొలగించండి", "edit": "సవరించండి",
        "submit": "సమర్పించండి", "next": "తరువాత", "previous": "మునుపటి", "search": "శోధించండి",
        "filter": "ఫిల్టర్", "all": "అన్నీ", "loading": "లోడ్ అవుతోంది...", "error": "లోపం", "success": "విజయం"
    },
    "header": {"title": "VAANIपथ"},
    "landing": {
        "heroTitle": "మీ భాషలో నేర్చుకోండి", "heroSubtitle": "AI-ఆధారిత బహుభాషా విద్యా వేదిక",
        "features": "లక్షణాలు", "testimonials": "ప్రశంసాపత్రాలు", "pricing": "ధర", "contact": "సంప్రదించండి"
    },
    "auth": {
        "email": "ఇమెయిల్", "password": "పాస్‌వర్డ్", "confirmPassword": "పాస్‌వర్డ్‌ను నిర్ధారించండి", "name": "పేరు",
        "forgotPassword": "పాస్‌వర్డ్ మర్చిపోయారా?", "dontHaveAccount": "ఖాతా లేదా?", "alreadyHaveAccount": "ఇప్పటికే ఖాతా ఉందా?",
        "loginTitle": "మీ ఖాతాకు లాగిన్ అవ్వండి", "signupTitle": "మీ ఖాతాను సృష్టించండి"
    }
}

# Gujarati Translations
gu_data = {
    "common": {
        "login": "લોગિન", "signup": "સાઇન અપ", "logout": "લોગ આઉટ", "settings": "સેટિંગ્સ",
        "profile": "પ્રોફાઇલ", "home": "હોમ", "dashboard": "ડેશબોર્ડ", "myCourses": "મારા કોર્સ",
        "browseCourses": "કોર્સ બ્રાઉઝ કરો", "uploadContent": "સામગ્રી અપલોડ કરો", "createQuiz": "ક્વિઝ બનાવો",
        "studentDoubts": "વિદ્યાર્થીઓના પ્રશ્નો", "askDoubts": "પ્રશ્નો પૂછો", "community": "સમુદાય",
        "rewards": "ઇનામો", "aiRoadmap": "AI રોડમેપ", "podcast": "પોડકાસ્ટ", "feedback": "પ્રતિસાદ",
        "studentLogin": "વિદ્યાર્થી લોગિન", "teacherLogin": "શિક્ષક લોગિન", "getStarted": "શરૂ કરો",
        "welcome": "સ્વાગત છે", "points": "પોઈન્ટ્સ", "language": "ભાષા", "enrolled": "નોંધાયેલ",
        "viewCourse": "કોર્સ જુઓ", "continueLearning": "શીખવાનું ચાલુ રાખો", "completed": "પૂર્ણ",
        "totalVideos": "કુલ વિડિઓઝ", "totalStudents": "કુલ વિદ્યાર્થીઓ", "totalViews": "કુલ વ્યૂઝ",
        "recentCourses": "તાજેતરના કોર્સ", "createCourse": "કોર્સ બનાવો", "uploadVideo": "વિડિઓ અપલોડ કરો",
        "courseTitle": "કોર્સ શીર્ષક", "description": "વર્ણન", "selectLanguage": "ભાષા પસંદ કરો",
        "save": "સાચવો", "cancel": "રદ કરો", "delete": "કાઢી નાખો", "edit": "ફેરફાર કરો",
        "submit": "સબમિટ કરો", "next": "આગળ", "previous": "પાછળ", "search": "શોધો",
        "filter": "ફિલ્ટર", "all": "બધા", "loading": "લોડ થઈ રહ્યું છે...", "error": "ભૂલ", "success": "સફળ"
    },
    "header": {"title": "VAANIपथ"},
    "landing": {
        "heroTitle": "તમારી ભાષામાં શીખો", "heroSubtitle": "AI-સંચાલિત બહુભાષી શિક્ષણ પ્લેટફોર્મ",
        "features": "લક્ષણો", "testimonials": "પ્રશંસાપત્રો", "pricing": "કિંમત", "contact": "સંપર્ક"
    },
    "auth": {
        "email": "ઇમેઇલ", "password": "પાસવર્ડ", "confirmPassword": "પાસવર્ડની પુષ્ટિ કરો", "name": "નામ",
        "forgotPassword": "પાસવર્ડ ભૂલી ગયા?", "dontHaveAccount": "ખાતું નથી?", "alreadyHaveAccount": "પહેલેથી જ ખાતું છે?",
        "loginTitle": "તમારા ખાતામાં લોગિન કરો", "signupTitle": "તમારું ખાતું બનાવો"
    }
}

# Kannada Translations
kn_data = {
    "common": {
        "login": "ಲಾಗಿನ್", "signup": "ಸೈನ್ ಅಪ್", "logout": "ಲಾಗ್ ಔಟ್", "settings": "ಸೆಟ್ಟಿಂಗ್‌ಗಳು",
        "profile": "ಪ್ರೊಫೈಲ್", "home": "ಮುಖಪುಟ", "dashboard": "ಡ್ಯಾಶ್‌ಬೋರ್ಡ್", "myCourses": "ನನ್ನ ಕೋರ್ಸ್‌ಗಳು",
        "browseCourses": "ಕೋರ್ಸ್‌ಗಳನ್ನು ಬ್ರೌಸ್ ಮಾಡಿ", "uploadContent": "ವಿಷಯವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ", "createQuiz": "ರಸಪ್ರಶ್ನೆ ರಚಿಸಿ",
        "studentDoubts": "ವಿದ್ಯಾರ್ಥಿ ಸಂದೇಹಗಳು", "askDoubts": "ಸಂದೇಹಗಳನ್ನು ಕೇಳಿ", "community": "ಸಮುದಾಯ",
        "rewards": "ಬಹುಮಾನಗಳು", "aiRoadmap": "AI ರೋಡ್‌ಮ್ಯಾಪ್", "podcast": "ಪಾಡ್‌ಕ್ಯಾಸ್ಟ್", "feedback": "ಪ್ರತಿಕ್ರಿಯೆ",
        "studentLogin": "ವಿದ್ಯಾರ್ಥಿ ಲಾಗಿನ್", "teacherLogin": "ಶಿಕ್ಷಕ ಲಾಗಿನ್", "getStarted": "ಪ್ರಾರಂಭಿಸಿ",
        "welcome": "ಸ್ವಾಗತ", "points": "ಅಂಕಗಳು", "language": "ಭಾಷೆ", "enrolled": "ನೋಂದಾಯಿಸಲಾಗಿದೆ",
        "viewCourse": "ಕೋರ್ಸ್ ವೀಕ್ಷಿಸಿ", "continueLearning": "ಕಲಿಯುವುದನ್ನು ಮುಂದುವರಿಸಿ", "completed": "ಪೂರ್ಣಗೊಂಡಿದೆ",
        "totalVideos": "ಒಟ್ಟು ವೀಡಿಯೊಗಳು", "totalStudents": "ಒಟ್ಟು ವಿದ್ಯಾರ್ಥಿಗಳು", "totalViews": "ಒಟ್ಟು ವೀಕ್ಷಣೆಗಳು",
        "recentCourses": "ಇತ್ತೀಚಿನ ಕೋರ್ಸ್‌ಗಳು", "createCourse": "ಕೋರ್ಸ್ ರಚಿಸಿ", "uploadVideo": "ವೀಡಿಯೊ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ",
        "courseTitle": "ಕೋರ್ಸ್ ಶೀರ್ಷಿಕೆ", "description": "ವಿವರಣೆ", "selectLanguage": "ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ",
        "save": "ಉಳಿಸಿ", "cancel": "ರದ್ದುಮಾಡಿ", "delete": "ಅಳಿಸಿ", "edit": "ತಿದ್ದುಪಡಿ ಮಾಡಿ",
        "submit": "ಸಲ್ಲಿಸಿ", "next": "ಮುಂದೆ", "previous": "ಹಿಂದೆ", "search": "ಹುಡುಕಿ",
        "filter": "ಫಿಲ್ಟರ್", "all": "ಎಲ್ಲಾ", "loading": "ಲೋಡ್ ಆಗುತ್ತಿದೆ...", "error": "ದೋಷ", "success": "ಯಶಸ್ಸು"
    },
    "header": {"title": "VAANIपथ"},
    "landing": {
        "heroTitle": "ನಿಮ್ಮ ಭಾಷೆಯಲ್ಲಿ ಕಲಿಯಿರಿ", "heroSubtitle": "AI-ಚಾಲಿತ ಬಹುಭಾಷಾ ಶಿಕ್ಷಣ ವೇದಿಕೆ",
        "features": "ವೈಶಿಷ್ಟ್ಯಗಳು", "testimonials": "ಪ್ರಶಂಸಾಪತ್ರಗಳು", "pricing": "ಬೆಲೆ", "contact": "ಸಂಪರ್ಕ"
    },
    "auth": {
        "email": "ಇಮೇಲ್", "password": "ಪಾಸ್‌ವರ್ಡ್", "confirmPassword": "ಪಾಸ್‌ವರ್ಡ್ ದೃಢೀಕರಿಸಿ", "name": "ಹೆಸರು",
        "forgotPassword": "ಪಾಸ್‌ವರ್ಡ್ ಮರೆತಿರಾ?", "dontHaveAccount": "ಖಾತೆ ಇಲ್ಲವೇ?", "alreadyHaveAccount": "ಈಗಾಗಲೇ ಖಾತೆ ಇದೆಯೇ?",
        "loginTitle": "ನಿಮ್ಮ ಖಾತೆಗೆ ಲಾಗಿನ್ ಮಾಡಿ", "signupTitle": "ನಿಮ್ಮ ಖಾತೆಯನ್ನು ರಚಿಸಿ"
    }
}

# Malayalam Translations
ml_data = {
    "common": {
        "login": "ലോഗിൻ", "signup": "സൈൻ അപ്പ്", "logout": "ലോഗ് ഔട്ട്", "settings": "ക്രമീകരണങ്ങൾ",
        "profile": "പ്രൊഫൈൽ", "home": "ഹോം", "dashboard": "ഡാഷ്ബോർഡ്", "myCourses": "എന്റെ കോഴ്സുകൾ",
        "browseCourses": "കോഴ്സുകൾ ബ്രൗസ് ചെയ്യുക", "uploadContent": "ഉള്ളടക്കം അപ്‌ലോഡ് ചെയ്യുക", "createQuiz": "ക്വിസ് സൃഷ്ടിക്കുക",
        "studentDoubts": "വിദ്യാർത്ഥി സംശയങ്ങൾ", "askDoubts": "സംശയങ്ങൾ ചോദിക്കുക", "community": "കമ്മ്യൂണിറ്റി",
        "rewards": "റിവാർഡുകൾ", "aiRoadmap": "AI റോഡ്മാപ്പ്", "podcast": "പോഡ്കാസ്റ്റ്", "feedback": "അഭിപ്രായം",
        "studentLogin": "വിദ്യാർത്ഥി ലോഗിൻ", "teacherLogin": "അധ്യാപക ലോഗിൻ", "getStarted": "ആരംഭിക്കുക",
        "welcome": "സ്വാഗതം", "points": "പോയിന്റുകൾ", "language": "ഭാഷ", "enrolled": "എൻറോൾ ചെയ്തു",
        "viewCourse": "കോഴ്സ് കാണുക", "continueLearning": "പഠനം തുടരുക", "completed": "പൂർത്തിയായി",
        "totalVideos": "ആകെ വീഡിയോകൾ", "totalStudents": "ആകെ വിദ്യാർത്ഥികൾ", "totalViews": "ആകെ കാഴ്ചകൾ",
        "recentCourses": "സമീപകാല കോഴ്സുകൾ", "createCourse": "കോഴ്സ് സൃഷ്ടിക്കുക", "uploadVideo": "വീഡിയോ അപ്‌ലോഡ് ചെയ്യുക",
        "courseTitle": "കോഴ്സ് ശീർഷകം", "description": "വിവരണം", "selectLanguage": "ഭാഷ തിരഞ്ഞെടുക്കുക",
        "save": "സംരക്ഷിക്കുക", "cancel": "റദ്ദാക്കുക", "delete": "നീക്കം ചെയ്യുക", "edit": "എഡിറ്റ് ചെയ്യുക",
        "submit": "സമർപ്പിക്കുക", "next": "അടുത്തത്", "previous": "മുമ്പത്തേത്", "search": "തിരയുക",
        "filter": "ഫിൽട്ടർ", "all": "എല്ലാം", "loading": "ലോഡ് ചെയ്യുന്നു...", "error": "പിശക്", "success": "വിജയം"
    },
    "header": {"title": "VAANIपथ"},
    "landing": {
        "heroTitle": "നിങ്ങളുടെ ഭാഷയിൽ പഠിക്കുക", "heroSubtitle": "AI-പവർഡ് മൾട്ടി-ലാംഗ്വേജ് വിദ്യാഭ്യാസ പ്ലാറ്റ്ഫോം",
        "features": "സവിശേഷതകൾ", "testimonials": "സാക്ഷ്യപത്രങ്ങൾ", "pricing": "വില", "contact": "ബന്ധപ്പെടുക"
    },
    "auth": {
        "email": "ഇമെയിൽ", "password": "പാസ്‌വേഡ്", "confirmPassword": "പാസ്‌വേഡ് സ്ഥിരീകരിക്കുക", "name": "പേര്",
        "forgotPassword": "പാസ്‌വേഡ് മറന്നോ?", "dontHaveAccount": "അക്കൗണ്ട് ഇല്ലേ?", "alreadyHaveAccount": "ഇതിനകം അക്കൗണ്ട് ഉണ്ടോ?",
        "loginTitle": "നിങ്ങളുടെ അക്കൗണ്ടിലേക്ക് ലോഗിൻ ചെയ്യുക", "signupTitle": "നിങ്ങളുടെ അക്കൗണ്ട് സൃഷ്ടിക്കുക"
    }
}

# Punjabi Translations
pa_data = {
    "common": {
        "login": "ਲੌਗਇਨ", "signup": "ਸਾਈਨ ਅੱਪ", "logout": "ਲੌਗ ਆਉਟ", "settings": "ਸੈਟਿੰਗਾਂ",
        "profile": "ਪ੍ਰੋਫਾਈਲ", "home": "ਹੋਮ", "dashboard": "ਡੈਸ਼ਬੋਰਡ", "myCourses": "ਮੇਰੇ ਕੋਰਸ",
        "browseCourses": "ਕੋਰਸ ਬ੍ਰਾਊਜ਼ ਕਰੋ", "uploadContent": "ਸਮੱਗਰੀ ਅੱਪਲੋਡ ਕਰੋ", "createQuiz": "ਕਵਿਜ਼ ਬਣਾਓ",
        "studentDoubts": "ਵਿਦਿਆਰਥੀ ਦੇ ਸਵਾਲ", "askDoubts": "ਸਵਾਲ ਪੁੱਛੋ", "community": "ਭਾਈਚਾਰਾ",
        "rewards": "ਇਨਾਮ", "aiRoadmap": "AI ਰੋਡਮੈਪ", "podcast": "ਪੋਡਕਾਸਟ", "feedback": "ਫੀਡਬੈਕ",
        "studentLogin": "ਵਿਦਿਆਰਥੀ ਲੌਗਇਨ", "teacherLogin": "ਅਧਿਆਪਕ ਲੌਗਇਨ", "getStarted": "ਸ਼ੁਰੂ ਕਰੋ",
        "welcome": "ਜੀ ਆਇਆਂ ਨੂੰ", "points": "ਅੰਕ", "language": "ਭਾਸ਼ਾ", "enrolled": "ਦਾਖਲ",
        "viewCourse": "ਕੋਰਸ ਦੇਖੋ", "continueLearning": "ਸਿੱਖਣਾ ਜਾਰੀ ਰੱਖੋ", "completed": "ਪੂਰਾ ਹੋਇਆ",
        "totalVideos": "ਕੁੱਲ ਵੀਡੀਓ", "totalStudents": "ਕੁੱਲ ਵਿਦਿਆਰਥੀ", "totalViews": "ਕੁੱਲ ਦ੍ਰਿਸ਼",
        "recentCourses": "ਹਾਲੀਆ ਕੋਰਸ", "createCourse": "ਕੋਰਸ ਬਣਾਓ", "uploadVideo": "ਵੀਡੀਓ ਅੱਪਲੋਡ ਕਰੋ",
        "courseTitle": "ਕੋਰਸ ਦਾ ਸਿਰਲੇਖ", "description": "ਵੇਰਵਾ", "selectLanguage": "ਭਾਸ਼ਾ ਚੁਣੋ",
        "save": "ਸੇਵ ਕਰੋ", "cancel": "ਰੱਦ ਕਰੋ", "delete": "ਹਟਾਓ", "edit": "ਸੋਧੋ",
        "submit": "ਜਮ੍ਹਾਂ ਕਰੋ", "next": "ਅਗਲਾ", "previous": "ਪਿਛਲਾ", "search": "ਖੋਜ",
        "filter": "ਫਿਲਟਰ", "all": "ਸਭ", "loading": "ਲੋਡ ਹੋ ਰਿਹਾ ਹੈ...", "error": "ਗਲਤੀ", "success": "ਸਫਲ"
    },
    "header": {"title": "VAANIपथ"},
    "landing": {
        "heroTitle": "ਆਪਣੀ ਭਾਸ਼ਾ ਵਿੱਚ ਸਿੱਖੋ", "heroSubtitle": "AI-ਸੰਚਾਲਿਤ ਬਹੁ-ਭਾਸ਼ਾਈ ਸਿੱਖਿਆ ਪਲੇਟਫਾਰਮ",
        "features": "ਵਿਸ਼ੇਸ਼ਤਾਵਾਂ", "testimonials": "ਪ੍ਰਸ਼ੰਸਾ ਪੱਤਰ", "pricing": "ਕੀਮਤ", "contact": "ਸੰਪਰਕ"
    },
    "auth": {
        "email": "ਈਮੇਲ", "password": "ਪਾਸਵਰਡ", "confirmPassword": "ਪਾਸਵਰਡ ਦੀ ਪੁਸ਼ਟੀ ਕਰੋ", "name": "ਨਾਮ",
        "forgotPassword": "ਪਾਸਵਰਡ ਭੁੱਲ ਗਏ?", "dontHaveAccount": "ਖਾਤਾ ਨਹੀਂ ਹੈ?", "alreadyHaveAccount": "ਪਹਿਲਾਂ ਹੀ ਖਾਤਾ ਹੈ?",
        "loginTitle": "ਆਪਣੇ ਖਾਤੇ ਵਿੱਚ ਲੌਗਇਨ ਕਰੋ", "signupTitle": "ਆਪਣਾ ਖਾਤਾ ਬਣਾਓ"
    }
}

# Mapping of languages
translations = {
    "hi-IN": hi_data,
    "bn-IN": en_data,  # Will be auto-translated
    "mr-IN": en_data,  # Will be auto-translated
    "ta-IN": en_data,  # Will be auto-translated
    "te-IN": en_data,  # Will be auto-translated
    "gu-IN": en_data,  # Will be auto-translated
    "kn-IN": en_data,  # Will be auto-translated
    "ml-IN": en_data,  # Will be auto-translated
    "pa-IN": en_data,  # Will be auto-translated
    # For others, using English as fallback for now to ensure files exist
    "as-IN": en_data,
    "brx-IN": en_data,
    "doi-IN": en_data,
    "ks-IN": en_data,
    "kok-IN": en_data,
    "mai-IN": en_data,
    "mni-IN": en_data,
    "ne-IN": en_data,
    "or-IN": en_data,
    "sa-IN": en_data,
    "sat-IN": en_data,
    "sd-IN": en_data,
    "ur-IN": en_data
}

# Language mapping for Google Translate
lang_map = {
    "hi-IN": "hi",
    "bn-IN": "bn",
    "mr-IN": "mr",
    "ta-IN": "ta",
    "te-IN": "te",
    "gu-IN": "gu",
    "kn-IN": "kn",
    "ml-IN": "ml",
    "pa-IN": "pa",
    "as-IN": "as", # Assamese
    "brx-IN": "en", # Bodo (fallback)
    "doi-IN": "doi", # Dogri
    "ks-IN": "ks", # Kashmiri
    "kok-IN": "gom", # Konkani (Goan) - check code
    "mai-IN": "mai", # Maithili
    "mni-IN": "mni", # Manipuri
    "ne-IN": "ne",
    "or-IN": "or",
    "sa-IN": "sa",
    "sat-IN": "en", # Santali (fallback)
    "sd-IN": "sd",
    "ur-IN": "ur"
}

# Write files
for lang, data in translations.items():
    # If data is en_data (fallback), try to translate it
    final_data = data
    if data == en_data and lang in lang_map and lang_map[lang] != 'en':
        print(f"Auto-translating for {lang} ({lang_map[lang]})...")
        final_data = translate_dict(en_data, lang_map[lang])
    
    file_path = os.path.join(locales_dir, f"{lang}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    print(f"Generated {lang}.json")

# Write English
with open(os.path.join(locales_dir, "en-IN.json"), "w", encoding="utf-8") as f:
    json.dump(en_data, f, ensure_ascii=False, indent=2)
print("Generated en-IN.json")
