import os
import requests
import json
from PIL import Image
import io
from datetime import datetime

# Configuration - PATHS
SPRITES_DIR = "sprites/auto-downloaded"
CUSTOM_DIR = "sprites/custom"
FALLBACK_PATH = "sprites/_fallback.png"

# Safe directory creation (no error if exists)
# Replace these lines:
# os.makedirs(SPRITES_DIR, exist_ok=True)
# os.makedirs(CUSTOM_DIR, exist_ok=True)

# With:
try:
    os.makedirs(SPRITES_DIR, mode=0o755, exist_ok=True)
    os.makedirs(CUSTOM_DIR, mode=0o755, exist_ok=True)
except Exception as e:
    print(f"Directory notice: {str(e)}")
    # Continue execution even if directories exist


def get_holiday_sprites():
    """Main function to process all holidays"""
    try:
        with open("events/holidays.json") as f:
            holidays = json.load(f).get("events", [])
            
        if not holidays:
            raise ValueError("No holidays found in JSON")
            
        for holiday in holidays:
            process_holiday(holiday)
            
    except Exception as e:
        print(f"Fatal error loading holidays: {str(e)}")
        raise

def process_holiday(holiday):
    """Process individual holiday sprite"""
    try:
        name = holiday["name"].lower().replace(' ', '_')
        sprite_name = f"{name}.png"
        custom_path = os.path.join(CUSTOM_DIR, sprite_name)
        auto_path = os.path.join(SPRITES_DIR, sprite_name)

        # Priority 1: Custom sprite
        if os.path.exists(custom_path):
            print(f"✓ Using custom: {sprite_name}")
            return

        # Priority 2: API download
        download_sprite(name, auto_path)
        
    except KeyError:
        print(f"⚠️ Invalid holiday format: {holiday}")
    except Exception as e:
        print(f"⚠️ Error processing holiday: {str(e)}")

def download_sprite(holiday_name, save_path):
    """Download from API with retry logic"""
    try:
        # Format for pixelarticons API
        api_name = holiday_name.replace('_', '-')
        url = f"https://api.pixelarticons.com/icons/{api_name}"
        
        print(f"⌛ Downloading: {holiday_name}")
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        # Process image
        img = Image.open(io.BytesIO(response.content))
        img = img.resize((32, 32), Image.Resampling.LANCZOS)
        img.save(save_path, optimize=True)
        print(f"✅ Downloaded: {holiday_name}")
        
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Download failed: {holiday_name} - {str(e)}")
        use_fallback(save_path)
    except Exception as e:
        print(f"⚠️ Image processing error: {str(e)}")
        use_fallback(save_path)

def use_fallback(target_path):
    """Copy fallback image with validation"""
    try:
        if not os.path.exists(FALLBACK_PATH):
            raise FileNotFoundError("Fallback image missing")
            
        with open(FALLBACK_PATH, "rb") as src, open(target_path, "wb") as dst:
            dst.write(src.read())
        print(f"↪️ Used fallback for {os.path.basename(target_path)}")
        
    except Exception as e:
        print(f"❌ Critical fallback failure: {str(e)}")
        raise

if __name__ == "__main__":
    print(f"\n{datetime.now().isoformat()} Starting sprite processing")
    get_holiday_sprites()
    print("Sprite processing complete\n")
