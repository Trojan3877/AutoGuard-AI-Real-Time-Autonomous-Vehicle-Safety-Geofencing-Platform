import requests

GOOGLE_API_KEY = "YOUR_KEY"

def check_geofence(lat, lon):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}&key={GOOGLE_API_KEY}"
    response = requests.get(url).json()

    # Example logic: allow only within certain region
    for result in response["results"]:
        if "Ohio" in str(result):
            return True
    return False
