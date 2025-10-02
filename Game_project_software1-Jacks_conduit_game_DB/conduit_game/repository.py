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
    # Define maximum length for the name and the spacing
    max_name_length = max(len(airport.name) for airport in airports)
    line_width = 43  # Width of the line in the ASCII art (can be adjusted as needed)

    # This is the function to format each airport name within a fixed-width space
    def format_airport_line(airport_name: str, line_position: str) -> str:
        # Center the airport name in a field with a specific width
        name_field = f"{airport_name}".center(max_name_length + 3 )  # Adding padding between names
        return f"{line_position}{name_field}{' ' * (line_width - len(name_field) - len(line_position))}"

    # Show all 10 airports instead of just 4
    bloody_note = f"""
[red]      @@#@@                                                                               @*@@      
[red]      %%%@@                                                                               @%%@      
[red]       %@@                                                                                @@%       
[red]        @@                                                                                @%@       
[red]        @@                                                                                @@@       
[red]      @@@%@                                                                              @%@@@      
[red]   %@@@%%@@@@@                                                                        @@@@@@%%%%%   
[red] @@@@@%%#@@@@@@                                                                      @@@@@%@@#%@@%@ 
[red]@@@@@@%%%%%%###%@                                                                  %###%%@%%@%%@@@@@
[red]  @@@%%%%@@@@@@                                                                      @@@@%%%@%@@@@@ 
[red]  @@@%%%@%%%@@@@%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@%%%%%@@@%%%@@@@@@@%@@%%%%%%%%%@@@@@@@@%##@%%%@@@  
[red]  @@@%@@%#%%@@%%%%%%###%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@@@@@@%%%@%%%@@@  
[red]  @@@@@@%#%%@@%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@@@%%#@@@%@@@  
[red]   @@@@@%#%@@@%%%%%%%%%%%%%%%{format_airport_line(airports[0].name, "")} %%%%%%%%%@@@@@@%%#%@@%@@   
[red]   @@@@%%%%@@@%%%%%%%%%%%%%%%%%%%%%%#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@@@@@@%%%@@@@@   
[red]   @@@@%%%%@@@%%%%%%%%%%%%%%%{format_airport_line(airports[1].name, "")} %%%%%%%%%@@@@@%%%%@@@@@   
[red]   @@%@%%%%@@@%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@@@@@@%%%@%@@@@   
[red]   @%#@%%%%@@@%%%%%%%%%%%%%##{format_airport_line(airports[2].name, "")} %%%%%%@%@@@@@@@%@%%%@@@   
[red]   @##@%%%%@@@%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@@@@@%##%@@@   
[red]   @@%@%%%%@@@%%%%%%%%%%%%%%%{format_airport_line(airports[3].name, "")} %%%%%%%%@@@@@@@@%%%%%@@  
[red]   @@@@%%%%@@@@%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@@@@@@@@%%%%%@@@   
[red]   @@@%%%%%@@@%%%%%%%%%%%%%%%{format_airport_line(airports[4].name, "")} %%%%%%@@@@@@@@@%%%%%@@@  
[red]   @@@%%%%%@@@@%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@@@@@@@@@@%%%%%@@@   
[red]   @@@%%%%%@@@%%%%%%%%%%%%%%%{format_airport_line(airports[5].name, "")} %%%%%@%%%@@@@@@%%%%%@@@   
[red]   @@@%%%%%@@@%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@%@@@@@@%%%%%@@@   
[red]   @@@%%%%%@@@%%%%%%%%%%%%%%%{format_airport_line(airports[6].name, "")}%%%%%%%%@%%%%%@@@%%%%@@@   
[red]   @@@%%%%%@@@%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@@@@@%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@@%%%%%@@@   
[red]   @@@%%%%%@@@%%%%%%%%%%%%%%%{format_airport_line(airports[7].name, "")}%%%%%%%%%%%%%%@@%%%%%@@@   
[red]   @@@%%%%%@@@%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@%@@%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@@@%%%%%@@@   
[red]   @@@%%%%%@@@@%%%%%%%%%%%%%%{format_airport_line(airports[8].name, "")}%%%%%%%%%%%%%@@@@%%#%%%@@   
[red]   @@%%##%@@@@%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@@%#%#%@@@   
[red]   @@%%#%%@@@@%%%%%%%%%%%%%%%{format_airport_line(airports[9].name, "")}%%%%%%%%%%%%%@@@@%%%%%@@   
[red]   @@@%##%%@@@%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@@%%###%@@@   
[red]   @@%%#%%%@@@%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@%%#%%%%@@   
[red]   @@@%%%%%@@@%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@%%%%%%@@@   
[red]   @@@%%%%%@@@%%%%%%%%%%%%%%%%%%%%%%%%%%%%@%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@@@@@@%%%%%%@@@   
[red]  @@@@%%%%%@@@@%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@@@%%%%%%@@@   
[red]  @@@%%%%%%@@@@%@%%%%@%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%@@%%%%%%@@@@  
[red]  @@@%%%%%%@@@@@@@@@@@@@%%%%%@@@@@@@@@@@@%%%%%%%@@@@@%%%%%%%%%%%%%%%%%%%%%%%%%%%@@%%%%@@%%%%%%@@@@  
[red]  @@@@@%%@@@@@@@                                                                    @@@@@%%%%@@@@@  
[red]@@@%%@@@@@@@@@@@@                                                                  @@@@@@@@@@@@@@%@@
[red] @@@@%%#%%%%%%@@                                                                    %%%%%@@%%%@@@@@ 
[red]   @@@@%%@@%#%                                                                         #%@@@@@@@@   
[red]      @@@@@                                                                              @@@@@      
[red]        %                                                                                  %@       
[red]       @%+                                                                                +%@       
[red]       @%*                                                                                *%@       
[red]      @@#*+                                                                               *#@@      
[red]      @@###                                                                               ###@@
    """
    return bloody_note