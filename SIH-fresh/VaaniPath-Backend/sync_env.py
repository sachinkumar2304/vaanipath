import os

# Paths
backend_env = r"d:\project-1\SIH-fresh\VaaniPath-Backend\.env"
localizer_env = r"d:\project-1\SIH-fresh\VaaniPath-Localizer\.env"

# Read Backend Keys
cloudinary_config = {}
if os.path.exists(backend_env):
    with open(backend_env, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, val = line.strip().split('=', 1)
                if key.startswith('CLOUDINARY_'):
                    cloudinary_config[key] = val

# Read Localizer Keys (to keep Gemini key)
gemini_config = {}
if os.path.exists(localizer_env):
    with open(localizer_env, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                parts = line.strip().split('=', 1)
                if len(parts) == 2:
                    key, val = parts
                    if key.startswith('GEMINI_'):
                        gemini_config[key] = val

# Write merged config to Localizer .env
with open(localizer_env, 'w') as f:
    f.write("# Cloudinary Configuration (Synced from Backend)\n")
    for key, val in cloudinary_config.items():
        f.write(f"{key}={val}\n")
    
    f.write("\n# Gemini API Configuration\n")
    for key, val in gemini_config.items():
        f.write(f"{key}={val}\n")
        
print("✅ Synced Cloudinary keys from Backend to Localizer!")
print(f"Cloudinary Keys found: {list(cloudinary_config.keys())}")
print(f"Gemini Keys preserved: {list(gemini_config.keys())}")
