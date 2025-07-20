import requests
import json

# Fetches public holidays for 2024
response = requests.get("https://date.nager.at/api/v3/PublicHolidays/2024/US")
with open("events/holidays.json", "w") as f:
    json.dump(response.json(), f)
