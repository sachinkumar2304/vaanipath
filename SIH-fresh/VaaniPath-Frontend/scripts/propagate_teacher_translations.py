import json
import os
import glob

# Configuration
LOCALES_DIR = r"d:\project-1\SIH-fresh\VaaniPath-Frontend\src\i18n\locales"
SOURCE_FILE = os.path.join(LOCALES_DIR, "hi-IN.json")
EXCLUDE_FILES = ["hi-IN.json", "en-IN.json", "hi-template.json"]

# Sections to propagate
SECTIONS_TO_PROPAGATE = [
    "teacherCourses",
    "teacherUpload",
    "teacherQuizzes",
    "teacherDoubts"
]

def main():
    print(f"Reading source file: {SOURCE_FILE}")
    
    try:
        with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
            source_data = json.load(f)
    except Exception as e:
        print(f"Error reading source file: {e}")
        return

    # Extract sections to propagate
    data_to_propagate = {}
    for section in SECTIONS_TO_PROPAGATE:
        if section in source_data:
            data_to_propagate[section] = source_data[section]
            print(f"Found section '{section}' with {len(source_data[section])} keys.")
        else:
            print(f"WARNING: Section '{section}' not found in source file!")

    if not data_to_propagate:
        print("No data to propagate. Exiting.")
        return

    # Get all JSON files in the directory
    json_files = glob.glob(os.path.join(LOCALES_DIR, "*.json"))
    
    for file_path in json_files:
        file_name = os.path.basename(file_path)
        
        if file_name in EXCLUDE_FILES:
            print(f"Skipping excluded file: {file_name}")
            continue
            
        print(f"Processing {file_name}...")
        
        try:
            # Read existing file
            with open(file_path, 'r', encoding='utf-8') as f:
                target_data = json.load(f)
            
            # Update with new sections
            modified = False
            for section, content in data_to_propagate.items():
                # We overwrite or add the section
                target_data[section] = content
                modified = True
                
            if modified:
                # Write back to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(target_data, f, indent=2, ensure_ascii=False)
                print(f"  Updated {file_name} successfully.")
            else:
                print(f"  No changes needed for {file_name}.")
                
        except Exception as e:
            print(f"  Error processing {file_name}: {e}")

    print("\nPropagation complete!")

if __name__ == "__main__":
    main()
