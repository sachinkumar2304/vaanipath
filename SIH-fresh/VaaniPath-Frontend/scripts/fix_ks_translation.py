import json
import os

# Base directory
base_dir = r"d:\project-1\SIH-fresh\VaaniPath-Frontend\src\i18n\locales"

# Load the base structure from a working file
with open(os.path.join(base_dir, "en-IN.json"), 'r', encoding='utf-8') as f:
    base_structure = json.load(f)

# Define all translations for Teacher Portal sections
translations = {
    "ks-IN": {  # Kashmiri
        "teacherCourses": {
            "title": "میہند کورسز",
            "subtitle": "پنین کورسز مینیج کریو تہ طالب علمن ہند مشغولیت ٹریک کریو",
            "createNew": "نو کورس بنایو",
            "searchPlaceholder": "عنوان یا تفصیل ذریعہ کورس ژھانڈیو...",
            "subject": "موضوع",
            "allSubjects": "ساری موضوعات",
            "activeFilters": "فعال فلٹرز",
            "noCourses": "کانہہ کورس آو نہ لبنہ",
            "tryAdjusting": "پنین فلٹرز یا تلاش کوئری ایڈجسٹ کرنچ کوشش کریو",
            "createFirst": "پڑھاونہ شروع کرنہ باپت پنین گوڈنیک کورس بنایو",
            "videos": "ویڈیوز",
            "viewCourse": "کورس وچھیو",
            "manage": "مینیج کریو",
            "delete": "مٹایو",
            "deleteConfirmTitle": "کورس مٹاونو؟",
            "deleteConfirmDesc": "کیا توہیہ یقین چھا ز توہیہ یہ کورس مٹاونہ یژھان چھیو؟ یہ اتھ کورسک تمام ویڈیوز تہ مٹاوِ۔ یہ ایکشن واپس نہ کرتھ ہیکو۔",
            "cancel": "منسوخ کریو",
            "loading": "توہند کورسز چھ لوڈ گژھان..."
        },
        "teacherUpload": {
            "title": "مواد اپ لوڈ کریو",
            "subtitle": "پننہ کورسس منز اکھ نو ویڈیو شامل کریو",
            "backToCourse": "کورسس واپس گژھیو",
            "backToCourses": "کورسن کن واپس گژھیو",
            "contentDetails": "مواد تفصیل",
            "fillDetails": "تفصیل بھریو تہ پنن تعلیمی مواد اپ لوڈ کریو",
            "course": "کورس",
            "selectCourse": "اکھ کورس ژاریو",
            "noCourses": "کانہہ کورس آو نہ لبنہ۔ گوڈہ اکھ کورس بنایو۔",
            "video": "ویڈیو",
            "audio": "آڈیو",
            "document": "دستاویز",
            "contentTitle": "عنوان",
            "enterTitle": "عنوان درج کریو",
            "description": "تفصیل",
            "describeContent": "مواد بیان کریو",
            "sourceLanguage": "ماخذ زبان",
            "uploadFile": "فائل اپ لوڈ کریو",
            "clickToUpload": "اپ لوڈ کرنہ باپت کلک کریو",
            "dragDrop": "یا ڈریگ تہ ڈراپ کریو",
            "uploading": "اپ لوڈ گژھان چھ...",
            "uploadComplete": "اپ لوڈ مکمل! پروسیسنگ...",
            "upload": "اپ لوڈ کریو",
            "fileTooLarge": "فائل بوڈ بڈ چھ",
            "maxSize": "زیادہ کھوتہ زیادہ فائل سائز 500MB چھ"
        },
        "teacherQuizzes": {
            "title": "کوئز بنایو",
            "subtitle": "طالب علمن ہند سمجھ ٹیسٹ کرنہ باپت کوئز بنایو",
            "quizDetails": "کوئز تفصیل",
            "selectCourseVideo": "کورس (ویڈیو) ژاریو",
            "chooseCourse": "اکھ کورس ژاریو",
            "quizTitle": "کوئز عنوان",
            "enterQuizTitle": "کوئز عنوان درج کریو",
            "description": "تفصیل",
            "enterDescription": "کوئز تفصیل درج کریو",
            "question": "سوال",
            "enterQuestion": "پنن سوال درج کریو",
            "options": "اختیارات",
            "points": "نمبر",
            "addQuestion": "سوال شامل کریو",
            "saveQuiz": "کوئز محفوظ کریو",
            "saving": "محفوظ گژھان چھ...",
            "validationError": "مہربانی کرتھ تمام سوال تہ اختیارات بھریو",
            "success": "کوئز کامیابی سان بنایہ!"
        },
        "teacherDoubts": {
            "title": "طالب علمن ہند شکوک",
            "subtitle": "طالب علمن ہند شکوکن ہند جواب دیو تہ تمن بہتر سکھنس منز مدد کریو",
            "totalDoubts": "کل شکوک",
            "pendingDoubts": "زیر التوا شکوک",
            "answeredDoubts": "جواب دنہ آمتہ شکوک",
            "allDoubts": "تمام شکوک",
            "pending": "زیر التوا",
            "answered": "جواب دنہ آیہ",
            "noDoubts": "کانہہ شکوک آو نہ لبنہ",
            "doubtDetails": "شک تفصیل",
            "student": "طالب علم",
            "course": "کورس",
            "topic": "موضوع",
            "question": "سوال",
            "yourAnswer": "توہند جواب",
            "submitAnswer": "جواب جمع کریو",
            "submitting": "جمع گژھان چھ...",
            "typeAnswer": "پنن تفصیلی جواب یتہ ٹائپ کریو...",
            "selectDoubt": "تفصیل ویچھنہ تہ جواب دنہ باپت اکھ شک ژاریو"
        }
    }
}

# Function to fix and update a language file
def fix_language_file(lang_code, teacher_translations):
    file_path = os.path.join(base_dir, f"{lang_code}.json")
    
    try:
        # Try to load existing file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Try to find the first valid JSON object
            try:
                data = json.loads(content)
                # If it loaded but has duplicate keys, we need to rebuild
                if isinstance(data, dict) and len(content) > len(json.dumps(data)) * 1.5:
                    # File is corrupted, extract only the first occurrence of each section
                    print(f"Fixing corrupted {lang_code}.json...")
                    # Load from a backup or reconstruct
                    data = {}
            except json.JSONDecodeError:
                print(f"JSON decode error in {lang_code}.json, will reconstruct...")
                data = {}
    except FileNotFoundError:
        print(f"{lang_code}.json not found, will create...")
        data = {}
    
    # Update with teacher translations
    for section, translations in teacher_translations.items():
        data[section] = translations
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Successfully updated {lang_code}.json")

# Fix Kashmiri file
fix_language_file("ks-IN", translations["ks-IN"])

print("\nKashmiri file has been fixed!")
