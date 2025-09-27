# conduit_game/repository.py
from typing import List, Tuple, Optional
from .db import get_connection

def fetch_hel() -> Tuple[int, str, str, str, str, Optional[float], Optional[float]]:
    """
    Returns HEL as: (id, name, iata_code, icao_code, iso_country, lat, lon)
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, iata_code, ident as icao_code, iso_country, latitude_deg, longitude_deg
        FROM airport
        WHERE iata_code = 'HEL'
        LIMIT 1;
    """)
    row = cur.fetchone()
    conn.close()
    if not row:
        raise RuntimeError("HEL not found in DB.")
    return row

def fetch_random_airports_excl_hel(n: int) -> List[Tuple[int, str, str, str, str, Optional[float], Optional[float]]]:
    """
    Returns n rows (excluding HEL):
    (id, name, iata_code, icao_code, iso_country, lat, lon)
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"""
        SELECT id, name, iata_code, ident as icao_code, iso_country, latitude_deg, longitude_deg
        FROM airport
        WHERE iata_code <> 'HEL'
        ORDER BY RAND()
        LIMIT {int(n)};
    """)
    rows = cur.fetchall()
    conn.close()
    return rows
