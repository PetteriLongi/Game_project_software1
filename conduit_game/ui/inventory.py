# conduit_game/ui/inventory.py
from ..models import RunState
from ..services import travel_cost
from ..utils.distance import coords, distance_km

def show_inventory(state: RunState):
    print("\n=== INVENTORY ===")
    print(f"Markka: {state.markka}")
    print(f"HP: {state.hp} | Sanity: {state.sanity}")

    cur = coords(state.current_lat, state.current_lon)

    print("\nAirports (with distance and cost):")
    count = len(state.airports)
    i = 0
    while i < count:
        a = state.airports[i]
        km = distance_km(cur, coords(a.lat, a.lon))
        cost = travel_cost(state, a)
        km_txt = f"{km:.0f} km" if km is not None else "N/A"
        cost_txt = f"{cost} M" if cost is not None else "N/A"
        print(f"{i+1:2d}. {a.name} ({a.iata or '—'}/{a.icao or '—'}, {a.country}) - {km_txt} - {cost_txt}")
        i += 1
    print("==================\n")
