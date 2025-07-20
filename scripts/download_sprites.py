import os
import requests
import json
from PIL import Image, ImageOps
import io
from datetime import datetime
import sys
from pathlib import Path

#from pathlib import Path
#import sys

# 1. New safety wrapper
def safe_mkdir(path):
    try:
        Path(path).mkdir(parents=True, exist_ok=True, mode=0o755)
        print(f"✓ Directory ready: {path}")
    except Exception as e:
        print(f"❌ Critical directory error: {str(e)}")
        sys.exit(1)

# 2. Updated configuration
SPRITES_DIR = "sprites/auto-downloaded"
CUSTOM_DIR = "sprites/custom" 
FALLBACK_PATH = "sprites/_fallback.png"

# 3. Guaranteed directory creation
safe_mkdir(SPRITES_DIR)  # ← New robust version
safe_mkdir(CUSTOM_DIR)   # ← New robust version

# Premium sprite sources (with fallbacks)
SOURCES = [
    # Pixel Articons (primary)
    lambda name: f"https://api.pixelarticons.com/icons/{name.replace('_', '-')}",
    
    # Game-Icons.net (fallback)
    lambda name: f"https://game-icons.net/icons/ffffff/000000/1x1/lorc/{name}.png",
    
    # OpenMoji (secondary fallback)
    lambda name: f"https://openmoji.org/data/color/svg/{EMOJI_MAP.get(name, '1F389')}.svg"
]

# Emoji mapping for holidays
EMOJI_MAP = {
    "christmas_day": "1F384",
    "new_years_day": "1F386",
    "thanksgiving_day": "1F983",
    # Add more mappings as needed
}

def download_sprite(holiday_name, target_dir):
    """Download sprite with multiple source fallbacks"""
    for source in SOURCES:
        try:
            url = source(holiday_name)
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            img = Image.open(io.BytesIO(response.content))
            img = ImageOps.pad(img, (32, 32), method=Image.Resampling.LANCZOS)
            
            target_path = f"{target_dir}/{holiday_name}.png"
            img.save(target_path, optimize=True)
            print(f"Downloaded {holiday_name} to {target_dir}/")
            return True
            
        except Exception as e:
            print(f"Failed {url}: {str(e)}")
            continue
    
    return False

def process_holidays():
    with open("events/holidays.json") as f:
        holidays = json.load(f)["events"]
    
    for holiday in holidays:
        name = holiday["name"].lower().replace(' ', '_')
        
        # 1. Try custom directory first
        if not os.path.exists(f"{CUSTOM_DIR}/{name}.png"):
            # 2. Download to auto-downloaded if not in custom
            if not os.path.exists(f"{SPRITES_DIR}/{name}.png"):
                if not download_sprite(name, SPRITES_DIR):
                    # 3. Use fallback if all downloads fail
                    use_fallback(name)

def use_fallback(holiday_name):
    """Copy fallback image with validation"""
    try:
        if os.path.exists(FALLBACK_PATH):
            target = f"{SPRITES_DIR}/{holiday_name}.png"
            with open(FALLBACK_PATH, "rb") as src, open(target, "wb") as dst:
                dst.write(src.read())
            print(f"Used fallback for {holiday_name}")
    except Exception as e:
        print(f"Fallback failed: {str(e)}")

if __name__ == "__main__":
    print(f"\n{datetime.now().isoformat()} Starting sprite processing")
    process_holidays()
    print("Sprite processing complete\n")
