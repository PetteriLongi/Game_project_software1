# conduit_game/utils/distance.py
from typing import Optional, Tuple
from geopy.distance import geodesic

Coord = Tuple[float, float]

def coords(lat: Optional[float], lon: Optional[float]) -> Optional[Coord]:
    if lat is None or lon is None:
        return None
    return (lat, lon)

def distance_km(a: Optional[Coord], b: Optional[Coord]) -> Optional[float]:
    if a is None or b is None:
        return None
    return geodesic(a, b).km
