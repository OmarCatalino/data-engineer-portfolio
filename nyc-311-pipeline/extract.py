import os
from datetime import datetime, timedelta
import requests
import pandas as pd

# --- Configuration ---
BASE_URL = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"
APP_TOKEN = os.environ.get("NYC_OPEN_DATA_APP_TOKEN")

DAYS_BACK = 7  # how many days of data to pull per run

# --- Compute the rolling cutoff ---
cutoff = datetime.now() - timedelta(days=DAYS_BACK)
cutoff_str = cutoff.strftime("%Y-%m-%dT%H:%M:%S")
print(f"Pulling records created on/after: {cutoff_str}")

headers = {
    "X-App-Token": APP_TOKEN
}

params = {
    "$select": "unique_key, created_date, closed_date, agency, agency_name, complaint_type, descriptor, descriptor_2, location_type, incident_zip, status, due_date, resolution_description, resolution_action_updated_date, community_board, council_district, police_precinct, borough, city, latitude, longitude",
    "$where": f"created_date >= '{cutoff_str}'",
    "$order": "created_date ASC",
    "$limit": 1000
}

# --- Request ---
response = requests.get(BASE_URL, headers=headers, params=params)
print("Status:", response.status_code)

data = response.json()
df = pd.DataFrame(data)

# --- Enforce a stable schema ---
requested = [c.strip() for c in params["$select"].split(",")]
missing = [c for c in requested if c not in df.columns]
print("Missing columns (before fix):", missing)

df = df.reindex(columns=requested)

print("Shape:", df.shape)
print("Earliest:", df["created_date"].min())
print("Latest:  ", df["created_date"].max())
print("due_date non-null count:", df["due_date"].notna().sum())