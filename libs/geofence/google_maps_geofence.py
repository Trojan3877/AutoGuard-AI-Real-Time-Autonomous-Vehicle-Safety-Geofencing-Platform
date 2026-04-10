import math
import os

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

def expand_geofence(center_lat, center_lng, radius_meters):
    """
    Dynamically expands geofence radius based on traffic density.
    """
    traffic_factor = 1.2  # Placeholder logic
    adjusted_radius = radius_meters * traffic_factor
    return adjusted_radius

def is_inside_geofence(lat, lng, center_lat, center_lng, radius):
    distance = haversine(lat, lng, center_lat, center_lng)
    return distance <= radius

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi/2)**2 + \
        math.cos(phi1)*math.cos(phi2)*math.sin(delta_lambda/2)**2

    c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R*c
