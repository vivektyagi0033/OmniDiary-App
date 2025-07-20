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

# ===== DIRECTORIES =====
def safe_mkdir(path):
    """Bulletproof directory creation"""
    try:
        Path(path).mkdir(parents=True, exist_ok=True, mode=0o755)
        print(f"✓ Directory ready: {path}")
        return True
    except Exception as e:
        print(f"❌ Failed to create {path}: {str(e)}")
        return False

if not safe_mkdir(SPRITES_DIR) or not safe_mkdir(CUSTOM_DIR):
    sys.exit(1)

# ===== SPRITE DOWNLOAD =====
def download_sprite(holiday_name):
    """Enhanced downloader with multiple sources and validation"""
    sprite_name = f"{holiday_name}.png"
    custom_path = os.path.join(CUSTOM_DIR, sprite_name)
    auto_path = os.path.join(SPRITES_DIR, sprite_name)

    # 1. Check custom folder first
    if os.path.exists(custom_path):
        print(f"⭐ Using custom sprite: {sprite_name}")
        return True

    # 2. Try downloading if not in auto-downloaded
    if not os.path.exists(auto_path):
        SOURCES = [
            # Primary source
            f"https://api.pixelarticons.com/icons/{holiday_name.replace('_', '-')}",
            # Fallback source
            f"https://game-icons.net/icons/ffffff/000000/1x1/lorc/{holiday_name}.png"
        ]

        for url in SOURCES:
            try:
                print(f"⌛ Attempting download: {url}")
                response = requests.get(url, timeout=15)
                response.raise_for_status()
                
                # Validate image
                img = Image.open(io.BytesIO(response.content))
                if img.size[0] < 16 or img.size[1] < 16:  # Minimum size check
                    raise ValueError("Image too small")
                    
                # Process and save
                img = ImageOps.pad(img, (32, 32), method=Image.Resampling.LANCZOS)
                img.save(auto_path, optimize=True)
                print(f"✅ Downloaded: {sprite_name}")
                return True
                
            except Exception as e:
                print(f"⚠️ Failed {url}: {str(e)}")
                continue

        # 3. Use fallback if all downloads fail
        use_fallback(auto_path)
    return True

def use_fallback(target_path):
    """Copy fallback with validation"""
    try:
        if not os.path.exists(FALLBACK_PATH):
            raise FileNotFoundError("Fallback image missing")
            
        with open(FALLBACK_PATH, "rb") as src, open(target_path, "wb") as dst:
            dst.write(src.read())
        print(f"↪️ Used fallback for {os.path.basename(target_path)}")
    except Exception as e:
        print(f"🔥 Critical fallback error: {str(e)}")
        raise

# ===== MAIN EXECUTION =====
if __name__ == "__main__":
    print(f"\n{datetime.now().isoformat()} Starting sprite processing")
    
    try:
        with open("events/holidays.json") as f:
            holidays = json.load(f)["events"]
            
        for holiday in holidays:
            holiday_name = holiday["name"].lower().replace(' ', '_')
            download_sprite(holiday_name)
            
    except Exception as e:
        print(f"💥 Fatal error: {str(e)}")
        sys.exit(1)
        
    print("Sprite processing complete\n")
