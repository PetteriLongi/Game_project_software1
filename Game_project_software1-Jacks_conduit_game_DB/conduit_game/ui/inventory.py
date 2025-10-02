from ..utils.colors import colouring
from ..models import AirportChoice
from ..models import RunState
from ..services import travel_cost
from ..utils.distance import coords, distance_km
from rich.console import Console
from rich.table import Table
import random
from dataclasses import dataclass
from typing import List, Tuple, Optional
from ..repository import create_bloody_note, fetch_random_airports_excl_hel
console = Console()


def show_inventory(state: RunState):
    print("\n=== INVENTORY ===")
    print(f"Markka: {state.markka}")
    print(f"HP: {state.hp} | Sanity: {state.sanity}")

    # Display the bloody note if it exists in inventory
    if state.inventory:
        console.print("\n[bold red]BLOODY NOTE:[/bold red]")
        console.print(state.inventory[0])

    cur = coords(state.current_lat, state.current_lon)

    #print("\nAirports (with distance and cost):")
    #count = len(state.airports)
   # i = 0
    #while i < count:
        #a = state.airports[i]
       # km = distance_km(cur, coords(a.lat, a.lon))
       # #cost = travel_cost(state, a)
       # km_txt = f"{km:.0f} km" if km is not None else "N/A"
        #cost_txt = f"{cost} M" if cost is not None else "N/A"
        #print(f"{i+1:2d}. {a.name} ({a.iata or '—'}/{a.icao or '—'}, {a.country}) - {km_txt} - {cost_txt}")
        #i += 1
    #print("==================\n")