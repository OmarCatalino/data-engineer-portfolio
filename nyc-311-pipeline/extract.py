import os
import time
from datetime import datetime, timedelta
import requests
import pandas as pd

# --- Configuration ---
BASE_URL = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"
APP_TOKEN = os.environ.get("NYC_OPEN_DATA_APP_TOKEN")

DAYS_BACK = 7      # how many days of data to pull per run
PAGE_SIZE = 1000   # rows per request
MAX_PAGES = 200    # safety stop so a bug can't loop forever
MAX_RETRIES = 4    # attempts per page before giving up
RETRY_CODES = {429, 500, 502, 503, 504}  # temporary server errors worth retrying

# --- Compute the rolling cutoff ---
cutoff = datetime.now() - timedelta(days=DAYS_BACK)
cutoff_str = cutoff.strftime("%Y-%m-%dT%H:%M:%S")
print(f"Pulling records created on/after: {cutoff_str}")

headers = {"X-App-Token": APP_TOKEN}

select_cols = "unique_key, created_date, closed_date, agency, agency_name, complaint_type, descriptor, descriptor_2, location_type, incident_zip, status, due_date, resolution_description, resolution_action_updated_date, community_board, council_district, police_precinct, borough, city, latitude, longitude"


def fetch_page(params):
    """Request one page. Retry temporary errors; fail loudly if they don't clear."""
    for attempt in range(1, MAX_RETRIES + 1):
        response = requests.get(BASE_URL, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()

        if response.status_code in RETRY_CODES and attempt < MAX_RETRIES:
            wait = 2 ** attempt   # 2s, 4s, 8s... waits longer each time
            print(f"   status {response.status_code} on attempt {attempt}, retrying in {wait}s...")
            time.sleep(wait)
            continue

        # Not retryable, or out of retries: stop the whole script with a clear message
        raise RuntimeError(
            f"Request failed: status {response.status_code} after {attempt} attempt(s). "
            f"Response: {response.text[:200]}"
        )


# --- Pagination loop ---
all_rows = []
offset = 0
page = 1

while page <= MAX_PAGES:
    params = {
        "$select": select_cols,
        "$where": f"created_date >= '{cutoff_str}'",
        "$order": "created_date ASC, unique_key ASC",
        "$limit": PAGE_SIZE,
        "$offset": offset,
    }

    rows = fetch_page(params)
    print(f"Page {page}: offset={offset}, rows={len(rows)}")

    all_rows.extend(rows)

    if len(rows) < PAGE_SIZE:
        break

    offset += PAGE_SIZE
    page += 1

# --- Build the DataFrame with a stable schema ---
requested = [c.strip() for c in select_cols.split(",")]
df = pd.DataFrame(all_rows).reindex(columns=requested)

print("Shape:", df.shape)
print("Earliest:", df["created_date"].min())
print("Latest:  ", df["created_date"].max())
print("Duplicate unique_keys:", df["unique_key"].duplicated().sum())