# conduit_game/models.py
from dataclasses import dataclass, field
from typing import List, Optional

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

    def __str__(self):
        return f"{self.name} ({self.iata})"

@dataclass
class RunState:
    # current position (starts at HEL)
    current_id: int
    current_name: str
    current_iata: str
    current_icao: str
    current_country: str
    current_lat: Optional[float]
    current_lon: Optional[float]

    # 10 options
    airports: List[AirportChoice]

    # stats
    markka: int
    sanity: int
    hp: int

    # 10 options
    airports: List[AirportChoice]

    # Inventory
    inventory: List[str] = None

    def __post_init__(self):
        if self.inventory is None:
            self.inventory = []
