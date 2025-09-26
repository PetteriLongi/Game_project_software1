# game_db.py — simple, beginner-friendly single file
# Flow:
#   • Start at HEL (HEL is NOT in the 10 travel options)
#   • Each run picks 10 random airports (excluding HEL); 5 secretly have conduits
#   • Main menu uses numbers (1,2,3,9). Help is still 'H'. Rest is 'R'.
#   • Inventory shows Markka and all 10 airports with IATA, ICAO, distance, cost
#   • After you ARRIVE at a conduit airport: show "strange presence" and offer to close
#   • Visited airports become "VISITED" and you cannot return to them

import sys
import random
from dataclasses import dataclass
from typing import List, Tuple, Optional

import mariadb
from geopy.distance import geodesic  # pip install geopy


# --------- EASY SETTINGS (tweak here) ----------
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "gameuser"
DB_PASS = "yourpassword"      # <-- change this
DB_NAME = "flight_game"       # "flight_game" (airports), fallback attempts "conduit_game"

RATE_PER_KM = 0.01             # Markka per km (lower to make travel cheaper)
REWARD_MARKKA = 100           # reward for closing a conduit
SANITY_LOSS = 5               # sanity penalty when closing a conduit
START_MARKKA = 5000           # starting money
START_SANITY = 100            # starting sanity
START_HP = 100                # starting health


# --------- DB CONNECT ----------
def get_connection():
    try:
        conn = mariadb.connect(
            user="gameuser",
            password="yourpassword",
            host="localhost",
            database="flight_game",
            port=3306,
        )
        return conn
    except mariadb.Error as e:
        print(f"[DB] connect error: {e}")
        sys.exit(1)


# --------- data access helpers ----------
def _row_to_tuple(row):
    # Expecting: id, name, iata, icao, country, lat, lon
    # row can be a tuple/list already
    return (
        row[0],          # id
        row[1],          # name
        row[2],          # iata
        row[3],          # icao (gps_code / ident)
        row[4],          # country
        row[5],          # lat
        row[6],          # lon
    )


def _select_one(cur, sql: str):
    cur.execute(sql)
    return cur.fetchone()


def _select_all(cur, sql: str):
    cur.execute(sql)
    return cur.fetchall()


def fetch_hel() -> Tuple[int, str, str, str, str, Optional[float], Optional[float]]:
    """
    Return HEL row as (id, name, iata, icao, country, lat, lon).

    We try the 'flight_game.airport' schema first.
    If it fails, we try a fallback matching your earlier CSV schema ('conduit_game.airports').
    """
    conn = get_connection()
    cur = conn.cursor()

    row = None

    # Try flight_game.airport (has gps_code)
    try:
        row = _select_one(cur, """
            SELECT id, name, iata_code, COALESCE(gps_code, ident) AS icao, iso_country,
                   latitude_deg, longitude_deg
            FROM airport
            WHERE iata_code = 'HEL'
            LIMIT 1;
        """)
    except mariadb.Error:
        row = None

    # Fallback: conduit_game.airports (no gps_code -> try ident/local_code if available)
    if not row:
        try:
            row = _select_one(cur, """
                SELECT id, name, iata_code,
                       COALESCE(gps_code, ident, local_code, '') AS icao,
                       iso_country, latitude_deg, longitude_deg
                FROM airports
                WHERE iata_code = 'HEL'
                LIMIT 1;
            """)
        except mariadb.Error:
            row = None

    conn.close()

    if not row:
        raise RuntimeError("HEL not found in any known airport table.")
    return _row_to_tuple(row)


def fetch_random_airports_excl_hel(n: int = 10) -> List[Tuple[int, str, str, str, str, Optional[float], Optional[float]]]:
    """
    Return n random airports excluding HEL.
    Each row: (id, name, iata, icao, country, lat, lon)
    """
    conn = get_connection()
    cur = conn.cursor()

    rows = []
    # Try flight_game.airport
    try:
        rows = _select_all(cur, f"""
            SELECT id, name, iata_code,
                   COALESCE(gps_code, ident) AS icao,
                   iso_country, latitude_deg, longitude_deg
            FROM airport
            WHERE iata_code <> 'HEL' AND iata_code IS NOT NULL AND iata_code <> ''
            ORDER BY RAND()
            LIMIT {int(n)};
        """)
    except mariadb.Error:
        rows = []

    if not rows:
        # Fallback to conduit_game.airports
        try:
            rows = _select_all(cur, f"""
                SELECT id, name, iata_code,
                       COALESCE(gps_code, ident, local_code, '') AS icao,
                       iso_country, latitude_deg, longitude_deg
                FROM airports
                WHERE iata_code <> 'HEL'
                ORDER BY RAND()
                LIMIT {int(n)};
            """)
        except mariadb.Error:
            rows = []

    conn.close()
    return [_row_to_tuple(r) for r in rows]


# --------- In-memory state ----------
@dataclass
class AirportChoice:
    id: int
    name: str
    iata: str
    icao: str
    country: str
    lat: Optional[float]
    lon: Optional[float]
    conduit: bool = False
    visited: bool = False
    conduit_closed: bool = False
    revealed_conduit: bool = False  # becomes True only after we arrive


@dataclass
class RunState:
    # current location (starts at HEL; HEL is not in airports list)
    current_id: int
    current_name: str
    current_iata: str
    current_icao: str
    current_country: str
    current_lat: Optional[float]
    current_lon: Optional[float]

    # the 10 choices for this run (excluding HEL)
    airports: List[AirportChoice]

    # player stats
    markka: int = START_MARKKA
    sanity: int = START_SANITY
    hp: int = START_HP


def start_new_run(seed: Optional[int] = None) -> RunState:
    """Make a new run: HEL start, 10 random airports (excluding HEL), 5 hidden conduits."""
    hel_id, hel_name, hel_iata, hel_icao, hel_country, hel_lat, hel_lon = fetch_hel()
    rows = fetch_random_airports_excl_hel(10)
    choices = [AirportChoice(*r) for r in rows]

    rng = random.Random(seed) if seed is not None else random
    if len(choices) >= 5:
        for idx in rng.sample(range(len(choices)), 5):
            choices[idx].conduit = True

    return RunState(
        current_id=hel_id,
        current_name=hel_name,
        current_iata=hel_iata or "",
        current_icao=hel_icao or "",
        current_country=hel_country,
        current_lat=hel_lat,
        current_lon=hel_lon,
        airports=choices,
        markka=START_MARKKA,
        sanity=START_SANITY,
        hp=START_HP,
    )


# --------- Simple helpers ----------
def _coords(lat, lon):
    if lat is None or lon is None:
        return None
    return (lat, lon)


def distance_km(state: RunState, a: AirportChoice) -> Optional[float]:
    cur = _coords(state.current_lat, state.current_lon)
    tgt = _coords(a.lat, a.lon)
    if cur is None or tgt is None:
        return None
    return geodesic(cur, tgt).km


def travel_cost_from_current(state: RunState, a: AirportChoice) -> Optional[int]:
    km = distance_km(state, a)
    if km is None:
        return None
    # round to int but not below 1
    cost = int(round(RATE_PER_KM * km))
    if cost < 1:
        cost = 1
    return cost

# ========== DISPLAY CONFIG (easy to tweak) ==========
USE_ANSI = True                      # Turn colors on/off globally
COLOR_VISITED = "\033[92m"           # bright/“neon” green
COLOR_CONDUIT_CLOSED = "\033[91m"    # corrupted red
ANSI_STRIKE = "\033[9m"
ANSI_RESET = "\033[0m"

def colorize(text: str, *, color: str | None = None, strike: bool = False) -> str:
    """Wrap text with ANSI color/strike if enabled."""
    if not USE_ANSI:
        return text
    start = ""
    if color:
        start += color
    if strike:
        start += ANSI_STRIKE
    if not start:
        return text
    return f"{start}{text}{ANSI_RESET}"

def pad_then_color(text: str, width: int, *, color: str | None = None, strike: bool = False) -> str:
    """
    Pad first (so table alignment is stable), then add ANSI styling.
    This avoids misalignment from invisible escape sequences.
    """
    raw = (text or "")[:width]
    padded = raw + " " * max(0, width - len(raw))
    return colorize(padded, color=color, strike=strike)



# --------- Display ----------
def _fmt(v: Optional[float]) -> str:
    if v is None:
        return "N/A"
    return f"{v:.0f} km"


def _status_text(a: AirportChoice) -> str:
    if a.visited:
        return "VISITED"
    if a.revealed_conduit and not a.conduit_closed:
        return "CONDUIT!"
    if a.revealed_conduit and a.conduit_closed:
        return "CONDUIT CLOSED"
    return ""


def show_inventory(state: RunState):
    print("\n=== INVENTORY ===")
    print(f"Markka: {state.markka} | HP: {state.hp} | Sanity: {state.sanity}")
    print("\nKnown airports (distance / cost):")

    print("+----+-------------------------------+------+------+-Country-+---------+---------+--------------+")
    print("| #  | Airport                       |IATA |ICAO | Country | Dist km | Cost M  | Status       |")
    print("+----+-------------------------------+------+------+-Country-+---------+---------+--------------+")
    for i, a in enumerate(state.airports, start=1):
        km = distance_km(state, a)
        cost = travel_cost_from_current(state, a)
        km_txt = _fmt(km)
        cost_txt = "N/A" if cost is None else f"{cost}"
        status = _status_text(a)
        print(f"| {i:2d} | {a.name[:29]:29} | { (a.iata or '-')[:4]:4} | { (a.icao or '-')[:4]:4} | {a.country[:7]:7} | {km_txt:7} | {cost_txt:7} | {status:12} |")
    print("+----+-------------------------------+------+------+-Country-+---------+---------+--------------+")


def show_help():
    print("""
HELP
  H : Help (this screen)
  1 : Travel
  2 : Inventory
  3 : Rest (restore HP and Sanity)
  9 : Quit

Notes
  • Start at HEL (Helsinki-Vantaa). HEL is not in the 10; you cannot return to HEL.
  • 10 airports each run (excluding HEL); 5 are secret conduits.
  • Travel cost = RATE_PER_KM × distance (rounded, min 1).
  • You only learn a conduit is present after you arrive.
""")


def show_menu():
    print("\nChoose: [1] Travel  [2] Inventory  [3] Rest  [H] Help  [9] Quit")


def show_travel_options(state: RunState):
    # Column widths (adjust anytime)
    W_NUM = 3
    W_NAME = 35
    W_IATA = 5
    W_ICAO = 6       # if you don’t have ICAO, print '-' or remove this column
    W_COUNTRY = 8
    W_DIST = 8
    W_COST = 10

    # Title
    line = "═" * (W_NUM + 1 + W_NAME + 1 + W_IATA + 1 + W_ICAO + 1 + W_COUNTRY + 1 + W_DIST + 1 + W_COST + 6)
    print(f"\n╔{line}╗")
    title = "TERMINAL • DEPARTURES"
    print(f"║ {title:^{len(line)}} ║")
    print(f"╠{line}╣")

    # Header
    header = (
        f"{'#':<{W_NUM}} "
        f"{'Airport':<{W_NAME}} "
        f"{'IATA':<{W_IATA}} "
        f"{'ICAO':<{W_ICAO}} "
        f"{'Country':<{W_COUNTRY}} "
        f"{'Distkm':>{W_DIST}} "
        f"{'Cost (M)':>{W_COST}}"
    )
    print(f"║ {header} ║")
    print(f"╠{line}╣")

    # Rows
    for i, a in enumerate(state.airports, start=1):
        km = distance_km(state, a)
        cost = travel_cost_from_current(state, a)
        km_txt = f"{km:.0f}" if km is not None else "N/A"
        cost_txt = f"{cost}" if cost is not None else "N/A"

        # Decide style for the NAME cell:
        #  - Conduit + CLOSED  -> red strikethrough
        #  - Visited (not a closed conduit) -> neon green strikethrough
        #  - Otherwise -> no style
        if a.conduit and a.conduit_closed:
            name_cell = pad_then_color(a.name, W_NAME, color=COLOR_CONDUIT_CLOSED, strike=True)
        elif a.visited:
            name_cell = pad_then_color(a.name, W_NAME, color=COLOR_VISITED, strike=True)
        else:
            name_cell = f"{(a.name or '')[:W_NAME]:<{W_NAME}}"

        # If you don’t actually have ICAO in your dataclass, replace `a.icao` with '-' or however you store it
        iata = a.iata or "-"
        icao = getattr(a, "icao", "-") or "-"
        country = a.country or "-"

        row = (
            f"{i:<{W_NUM}} "
            f"{name_cell}"
            f" {iata:<{W_IATA}} "
            f"{icao:<{W_ICAO}} "
            f"{country:<{W_COUNTRY}} "
            f"{km_txt:>{W_DIST}} "
            f"{cost_txt:>{W_COST}}"
        )
        print(f"║ {row} ║")

    print(f"╚{line}╝")
    print("(Enter 1-10 to travel. You cannot travel to VISITED entries.)")



# --------- Game actions ----------
def rest(state: RunState):
    # Simple rest: fully restore HP & sanity (no cost yet)
    before_hp = state.hp
    before_sanity = state.sanity
    state.hp = START_HP
    state.sanity = START_SANITY
    print(f"\nYou rest. HP {before_hp}→{state.hp}, Sanity {before_sanity}→{state.sanity}.")


def travel_to_index(state: RunState, idx: int) -> str:
    # bounds
    if idx < 1 or idx > len(state.airports):
        return "Out of range (choose 1..10)."

    a = state.airports[idx - 1]

    # disallow revisiting
    if a.visited:
        return f"You have already visited {a.name}. You cannot return."

    km = distance_km(state, a)
    cost = travel_cost_from_current(state, a)

    if km is None or cost is None:
        return "Cannot compute distance/cost for that route."

    if state.markka < cost:
        return f"Not enough Markka (need {cost}, have {state.markka})."

    # pay & move
    state.markka -= cost
    state.current_id = a.id
    state.current_name = a.name
    state.current_iata = a.iata or ""
    state.current_icao = a.icao or ""
    state.current_country = a.country
    state.current_lat = a.lat
    state.current_lon = a.lon
    a.visited = True

    msg = f"Arrived at {a.name} ({a.iata or '-'} / {a.icao or '-'}, {a.country})."

    # Conduit reveal only after arrival
    if a.conduit and not a.conduit_closed:
        a.revealed_conduit = True
        msg += " You feel a strange presence here."
        ans = input("Close the conduit now? (Y/N): ").strip().lower()
        if ans == "y":
            a.conduit_closed = True
            state.markka += REWARD_MARKKA
            # sanity goes down but not below zero
            state.sanity = max(0, state.sanity - SANITY_LOSS)
            msg += f" Conduit CLOSED (+{REWARD_MARKKA} Markka, -{SANITY_LOSS} Sanity)."
        else:
            msg += " You leave it be… for now."

    return msg


# --------- Main loop ----------
def main():
    print("Welcome to HELL— Helsinki-Vantaa Airport (HEL)")
    try:
        state = start_new_run()
    except Exception as e:
        print(f"Setup error: {e}")
        return

    while True:
        show_menu()
        cmd = input("> ").strip().lower()

        if cmd == "9":
            print("The world is overrun by darkness… you walk away.")
            break

        elif cmd == "h":
            show_help()

        elif cmd == "2":
            show_inventory(state)

        elif cmd == "3" or cmd == "r":
            rest(state)

        elif cmd == "1":
            show_travel_options(state)
            sel = input("Go to (1-10): ").strip()
            if sel.isdigit():
                idx = int(sel)
                print(travel_to_index(state, idx))
            else:
                print("Please enter a number between 1 and 10.")

        else:
            print("Unknown command. Use 1, 2, 3, R, H, or 9.")


if __name__ == "__main__":
    main()
