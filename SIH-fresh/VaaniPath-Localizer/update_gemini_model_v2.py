import os

localizer_env = r"d:\project-1\SIH-fresh\VaaniPath-Localizer\.env"
new_lines = []

if os.path.exists(localizer_env):
    with open(localizer_env, 'r') as f:
        for line in f:
            if line.startswith("GEMINI_MODEL="):
                new_lines.append("GEMINI_MODEL=gemini-1.5-flash-latest\n")
            else:
                new_lines.append(line)

# Write back
with open(localizer_env, 'w') as f:
    f.writelines(new_lines)

print("✅ Updated GEMINI_MODEL to gemini-1.5-flash-latest in .env")
