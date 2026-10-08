from math import asin, cos, radians, sin, sqrt


def distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    a = sin(radians(lat2 - lat1) / 2) ** 2 + (
        cos(radians(lat1)) * cos(radians(lat2)) * sin(radians(lon2 - lon1) / 2) ** 2
    )
    return 6371.0088 * 2 * asin(sqrt(min(1, a)))
