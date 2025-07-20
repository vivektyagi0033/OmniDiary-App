import requests
import json
from PIL import Image
import io

# Load holidays data
with open("events/holidays.json") as f:
    holidays = json.load(f)["events"]

# Download and resize icons
for holiday in holidays:
    query = holiday["name"].replace(" ", "+")
    try:
        # Fetch from open-source emoji/pixel art API
        response = requests.get(f"https://api.pixelarticons.com/icons/{query.lower()}")
        img = Image.open(io.BytesIO(response.content))
        img = img.resize((32, 32))
        img.save(f"sprites/{holiday['name'].lower().replace(' ', '_')}.png")
    except:
        print(f"Skipped {holiday['name']} (no icon found)")
