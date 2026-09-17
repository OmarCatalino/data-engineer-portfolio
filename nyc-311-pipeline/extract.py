import os
import requests
import pandas as pd

# --- Configuration ---
BASE_URL = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"
APP_TOKEN = os.environ.get("NYC_OPEN_DATA_APP_TOKEN")  # TODO: set this in your environment before running

headers = {
    "X-App-Token": APP_TOKEN
}

params = {
    "$select": "unique_key, created_date, closed_date, agency, agency_name, complaint_type, descriptor, descriptor_2, location_type, incident_zip, status, due_date, resolution_description, resolution_action_updated_date, community_board, council_district, police_precinct, borough, city, latitude, longitude",
    "$where": "created_date >= '2025-01-01T00:00:00'",  # TODO: pick your actual cutoff date
    "$order": "created_date DESC",
    "$limit": 1000  # keep small for this first test run
}

# --- Request ---
response = requests.get(BASE_URL, headers=headers, params=params)
print(response.status_code)

# TODO: what should happen if status_code isn't 200? Don't just assume success.

data = response.json()
df = pd.DataFrame(data)

print(df.shape)
print(df.columns.tolist())
print(df.head())