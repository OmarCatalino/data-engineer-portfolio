import os
from datetime import datetime, timedelta
import requests

BASE_URL = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"
headers = {"X-App-Token": os.environ.get("NYC_OPEN_DATA_APP_TOKEN")}

cutoff_str = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")

params = {
    "$select": "count(*)",
    "$where": f"created_date >= '{cutoff_str}'",
}

response = requests.get(BASE_URL, headers=headers, params=params)
print("Cutoff:", cutoff_str)
print(response.json())