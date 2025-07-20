import os
import requests
import json
from PIL import Image
import io
from datetime import datetime

# Configuration
SPRITES_DIR = "sprites/auto-downloaded"
CUSTOM_DIR = "sprites/custom"
FALLBACK_PATH = "sprites/_fallback.png"
os.makedirs(SPRITES_DIR, exist_ok=True)
os.makedirs(CUSTOM_DIR, exist_ok=True)

def get_holiday_sprites():
    """Main function to process all holidays"""
    with open("events/holidays.json") as f:
        holidays = json.load(f)["events"]
    
    for holiday in holidays:
        holiday_name = holiday["name"].lower().replace(' ', '_')
        sprite_name = f"{holiday_name}.png"
        process_holiday_sprite(holiday_name, sprite_name)

def process_holiday_sprite(holiday_name, sprite_name):
    """Handle sprite download/fallback logic"""
    custom_path = f"{CUSTOM_DIR}/{sprite_name}"
    auto_path = f"{SPRITES_DIR}/{sprite_name}"
    
    # Priority 1: Use custom sprite if exists
    if os.path.exists(custom_path):
        print(f"Using custom sprite for {holiday_name}")
        return
        
    # Priority 2: Download from API
    try:
        response = requests.get(
            f"https://api.pixelarticons.com/icons/{holiday_name.replace('_', '-')}",
            timeout=10
        )
        response.raise_for_status()
        
        img = Image.open(io.BytesIO(response.content))
        img = img.resize((32, 32))
        img.save(auto_path)
        print(f"Downloaded {sprite_name}")
        
    except Exception as e:
        print(f"Error downloading {holiday_name}: {str(e)}")
        use_fallback(auto_path)

def use_fallback(target_path):
    """Copy fallback image when downloads fail"""
    try:
        with open(FALLBACK_PATH, "rb") as src, open(target_path, "wb") as dst:
            dst.write(src.read())
        print(f"Used fallback for {target_path}")
    except Exception as e:
        print(f"Critical error with fallback: {str(e)}")

if __name__ == "__main__":
    print(f"{datetime.now().isoformat()} Starting sprite processing")
    get_holiday_sprites()
    print("Sprite processing complete")
