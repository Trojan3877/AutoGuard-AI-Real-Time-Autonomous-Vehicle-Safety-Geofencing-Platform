import os

import requests

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")


def check_geofence(lat, lon):
    if not GOOGLE_API_KEY:
        return False
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}&key={GOOGLE_API_KEY}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError):
        return False

    results = data.get("results", [])
    if not results:
        return False

    # Example logic: allow only within certain region
    for result in results:
        if "Ohio" in str(result):
            return True
    return False
