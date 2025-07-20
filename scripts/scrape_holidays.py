# scripts/scrape_holidays.py

import requests
import json
from datetime import datetime

# Fetches public holidays for 2024
# response = requests.get("https://date.nager.at/api/v3/PublicHolidays/2024/US")
# with open("events/holidays.json", "w") as f:
#     json.dump(response.json(), f)


def enrich_holiday(holiday):
    # Add app-specific fields
    holiday["icon"] = f"/sprites/{holiday['name'].lower().replace(' ', '_')}.png"
    holiday["category"] = "Federal" if holiday["global"] else "Regional"
    holiday["year"] = datetime.strptime(holiday["date"], "%Y-%m-%d").year
    return holiday

response = requests.get("https://date.nager.at/api/v3/PublicHolidays/2024/US")
holidays = [enrich_holiday(h) for h in response.json()]

with open("events/holidays.json", "w") as f:
    json.dump({"last_updated": datetime.utcnow().isoformat(), "events": holidays}, f)
