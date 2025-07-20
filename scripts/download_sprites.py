import os
import requests
import json
from PIL import Image, ImageOps
from pathlib import Path
import sys
from datetime import datetime

# ===== CONFIGURATION =====
SPRITES_DIR = "sprites/auto-downloaded"
CUSTOM_DIR = "sprites/custom"
FALLBACK_PATH = "sprites/_fallback.png"

# ===== ENHANCED DIRECTORY CREATION =====
def create_directories():
    """Guaranteed directory setup with validation"""
    try:
        # Remove problematic auto-downloaded folder if exists
        if os.path.exists(SPRITES_DIR):
            for f in os.listdir(SPRITES_DIR):
                os.remove(os.path.join(SPRITES_DIR, f))
        
        # Create fresh directories
        Path(SPRITES_DIR).mkdir(parents=True, exist_ok=True, mode=0o755)
        Path(CUSTOM_DIR).mkdir(parents=True, exist_ok=True, mode=0o755)
        
        print("✅ Directories reset and verified")
        return True
    except Exception as e:
        print(f"❌ Directory setup failed: {str(e)}")
        return False

# ===== SPRITE DOWNLOADER =====
def download_holiday_sprite(holiday_name):
    """Robust sprite download with multiple fallbacks"""
    sprite_name = f"{holiday_name}.png"
    custom_path = os.path.join(CUSTOM_DIR, sprite_name)
    auto_path = os.path.join(SPRITES_DIR, sprite_name)
    
    # 1. Check for custom sprite first
    if os.path.exists(custom_path):
        print(f"⭐ Using custom sprite: {sprite_name}")
        return True
        
    # 2. Attempt API downloads
    api_sources = [
        f"https://game-icons.net/icons/ffffff/000000/1x1/lorc/{holiday_name}.png",
        f"https://api.pixelarticons.com/icons/{holiday_name.replace('_', '-')}"
    ]
    
    for url in api_sources:
        try:
            print(f"🔍 Attempting: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Validate image
            img = Image.open(io.BytesIO(response.content))
            if img.size[0] < 10 or img.size[1] < 10:
                raise ValueError("Invalid image dimensions")
                
            # Process and save
            img = ImageOps.pad(img, (32, 32), method=Image.Resampling.LANCZOS)
            img.save(auto_path, optimize=True)
            print(f"✅ Downloaded: {sprite_name}")
            return True
            
        except Exception as e:
            print(f"⚠️ Failed {url}: {str(e)}")
            continue
    
    # 3. Final fallback
    if os.path.exists(FALLBACK_PATH):
        with open(FALLBACK_PATH, "rb") as src, open(auto_path, "wb") as dst:
            dst.write(src.read())
        print(f"↪️ Used fallback for {sprite_name}")
        return True
        
    raise FileNotFoundError("No sprite sources available")

# ===== MAIN EXECUTION =====
if __name__ == "__main__":
    print(f"\n{datetime.now().isoformat()} Sprite Processor")
    
    if not create_directories():
        sys.exit(1)
        
    try:
        with open("events/holidays.json") as f:
            holidays = json.load(f)["events"]
            
        for holiday in holidays:
            name = holiday["name"].lower().replace(' ', '_').replace("'", "")
            download_holiday_sprite(name)
            
    except Exception as e:
        print(f"💥 Critical error: {str(e)}")
        sys.exit(1)
        
    print("\nSprite processing completed successfully")
