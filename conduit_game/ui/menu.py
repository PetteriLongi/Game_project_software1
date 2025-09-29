# conduit_game/ui/menu.py
from ..models import RunState
from ..services import travel_to_index, rest
from .inventory import show_inventory
from .travel_board import show_travel_options

def show_commands():
    print("Choose: [1] Travel  [2] Inventory  [3] Rest  [H] Help  [9] Quit")

def show_help():
    print("""
HELP
  [1] Travel      - opens the terminal board (choose 1..10)
  [2] Inventory   - shows Markka / HP / Sanity and distances
  [3] Rest        - fully restore HP and Sanity
  [H] Help        - this help
  [Q] Quit        - quits the game
  [Space bar]      - Skip current line. The rest of that line prints instantly, then normal speed resumes on the next line.
  [Enter]         - Print the rest of the entire text instantly.

Notes
  • Start at HEL; HEL is not among the 10 options; you cannot return to HEL.
  • 10 random airports; 5 are secret conduits.
  • You may revisit an airport only if a conduit there is still open.
  • Travel cost depends on distance.
""")

def game_loop(state: RunState):
    while True:
        show_commands()
        cmd = input("> ").strip().lower()

        if cmd == "q":
            print("The world darkens. Farewell.")
            break

        if cmd == "h":
            show_help()
            continue

        if cmd == "3":
            print(rest(state))
            continue

        if cmd == "2":
            show_inventory(state)
            continue

        if cmd == "1":
            show_travel_options(state)
            sel = input("Go to (1-10): ").strip()
            if sel.isdigit():
                idx = int(sel)
                print(travel_to_index(state, idx))
            else:
                print("Please enter a number between 1 and 10.")
            continue

        print("Unknown command. Use 1,2,3,H, or 9.")
