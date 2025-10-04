# conduit_game/services.py
import random
from typing import Optional
from .config import (
    RATE_PER_KM, REWARD_MARKKA, SANITY_LOSS,
    START_MARKKA, START_SANITY, START_HP,
    NUM_AIRPORT_CHOICES, NUM_CONDUITS
)
from .models import RunState, AirportChoice
from .repository import fetch_hel, fetch_random_airports_excl_hel, create_bloody_note
from .utils.distance import coords, distance_km

# ---- helpers ----
def can_revisit(a: AirportChoice) -> bool:
    # allow revisiting only if conduit exists and not closed
    if a.conduit and not a.conduit_closed:
        return True
    return False

def is_locked(a: AirportChoice) -> bool:
    # visited but NOT an open conduit => locked
    if a.visited and not can_revisit(a):
        return True
    return False

def travel_cost(state: RunState, a: AirportChoice) -> Optional[int]:
    cur = coords(state.current_lat, state.current_lon)
    tgt = coords(a.lat, a.lon)
    km = distance_km(cur, tgt)
    if km is None:
        return None
    # int math + min cost of 1
    cost = int(round(RATE_PER_KM * km))
    if cost < 1:
        cost = 1
    return cost

# ---- core API ----
def start_new_run(seed: int | None = None) -> RunState:
    hel = fetch_hel()
    hel_id = hel.id
    hel_name = hel.name
    hel_iata = hel.iata
    hel_icao = hel.icao
    hel_country = hel.country
    hel_lat = hel.lat
    hel_lon = hel.lon

    rows = fetch_random_airports_excl_hel(NUM_AIRPORT_CHOICES)

    airports: list[AirportChoice] = []
    for r in rows:
        a = AirportChoice(
            id=r.id, name=r.name, iata=r.iata or "", icao=r.icao or "",
            country=r.country or "", lat=r.lat, lon=r.lon,
            conduit=r.conduit, visited=r.visited, conduit_closed=r.conduit_closed
        )
        airports.append(a)

    # pick conduits
    rng = random.Random(seed) if seed is not None else random
    indexes = list(range(len(airports)))
    if len(indexes) >= NUM_CONDUITS:
        chosen = rng.sample(indexes, NUM_CONDUITS)
        for i in chosen:
            airports[i].conduit = True


    bloody_note = create_bloody_note(airports)

    state = RunState(
        current_id=hel_id, current_name=hel_name,
        current_iata=hel_iata, current_icao=hel_icao,
        current_country=hel_country, current_lat=hel_lat, current_lon=hel_lon,
        airports=airports,
        markka=START_MARKKA, sanity=START_SANITY, hp=START_HP, inventory=[bloody_note]
    )
    return state

def rest(state: RunState) -> str:

    state.hp = START_HP
    state.sanity = START_SANITY
    return "You rest… HP and Sanity fully restored."

def travel_to_index(state: RunState, idx: int) -> str:
    n = len(state.airports)
    if idx < 1 or idx > n:
        return f"Choose between 1 and {n}."

    a = state.airports[idx - 1]

    if is_locked(a):
        return "You cannot return there (already visited)."

    cost = travel_cost(state, a)
    if cost is None:
        return "Cannot compute distance/cost for that route."

    if state.markka < cost:
        return f"Not enough Markka (need {cost}, have {state.markka})."


    state.markka -= cost
    state.current_id = a.id
    state.current_name = a.name
    state.current_iata = a.iata
    state.current_icao = a.icao
    state.current_country = a.country
    state.current_lat = a.lat
    state.current_lon = a.lon
    a.visited = True

    msg = f"Arrived at {a.name} ({a.iata or '—'}/{a.icao or '—'}, {a.country})."

    if a.conduit and not a.conduit_closed:
        msg += " You feel a strange presence here."
        choice = input("Close the conduit now? (Y/N): ").strip().lower()
        if choice == "y":
            a.conduit_closed = True
            state.markka += REWARD_MARKKA
            state.sanity = max(0, state.sanity - SANITY_LOSS)
            msg += f" Conduit CLOSED (+{REWARD_MARKKA} Markka, -{SANITY_LOSS} Sanity)."
        else:
            msg += " You leave it be… for now."

    return msg
