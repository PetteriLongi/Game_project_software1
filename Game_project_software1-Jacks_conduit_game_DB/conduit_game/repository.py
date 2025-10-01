# conduit_game/repository.py
from typing import List, Tuple, Optional
from .db import get_connection
from .models import AirportChoice
import random
from rich.console import Console
console = Console()

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

def fetch_random_airports_excl_hel(n: int) -> List[AirportChoice]:
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
    airports = [
        AirportChoice(id=row[0], name=row[1], iata=row[2], icao=row[3], country=row[4], lat=row[5], lon=row[6])
        for row in rows
    ]
    return airports

def create_bloody_note(airports: List[AirportChoice]):
    selected_airports = random.sample(airports, 4)
    bloody_note = f"""
    __
 /                          \
|   ████    ████    ████    |
|  ██████  ██████  ██████   |
| ████████ ████████ ██████  |
| ████████ ████████ ██████  |
|   {selected_airports[0]}
{selected_airports[1]}
{selected_airports[2]}
{selected_airports[3]}  |
|   ████████████████████    |
|   ████████████████████    |
|   ████████████████████    |
|                          ██████
|  ██████████████████████████  |
 ___/
    |      |     |     |    |
    |  [ ] | [ ] |  [ ] | [ ]|
    |__|__|||
    """
    console.print(bloody_note)
