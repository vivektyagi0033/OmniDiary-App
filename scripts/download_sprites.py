import os
import requests
from PIL import Image
import io

# Load holidays data
with open("events/holidays.json") as f:
    holidays = json.load(f)["events"]

# Preserve existing template
TEMPLATE_PATH = "sprites/template.aseprite"
os.makedirs("sprites", exist_ok=True)

for holiday in holidays:
    sprite_name = f"{holiday['name'].lower().replace(' ', '_')}.png"
    sprite_path = f"sprites/{sprite_name}"
    
    # Skip if already exists
    if os.path.exists(sprite_path):
        continue
        
    try:
        # Download from open-source API (example)
        response = requests.get(f"https://api.pixelarticons.com/icons/{sprite_name.replace('.png', '')}")
        img = Image.open(io.BytesIO(response.content))
        img = img.resize((32, 32))
        img.save(sprite_path)
        print(f"Downloaded {sprite_name}")
    except:
        print(f"Using template for {sprite_name}")
        # Copy template as fallback
        with open(TEMPLATE_PATH, "rb") as src, open(sprite_path, "wb") as dst:
            dst.write(src.read())
