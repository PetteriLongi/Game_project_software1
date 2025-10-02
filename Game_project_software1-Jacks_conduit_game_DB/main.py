# conduit_game/main.py
from conduit_game.services import start_new_run
from conduit_game.ui.menu import game_loop
from conduit_game.repository import create_bloody_note, fetch_random_airports_excl_hel
from conduit_game.utils.colors import colouring


#This is our H.P Lovecraft inspired software game project!

print(colouring(
        """
                                                                                                                                                                   
 ██▀███   ██▓▄▄▄█████▓▓█████   ██████     ▒█████    █████▒   ▄▄▄█████▓ ██▀███   ▄▄▄       ███▄    █   ██████  ██▓▄▄▄█████▓        
▓██ ▒ ██▒▓██▒▓  ██▒ ▓▒▓█   ▀ ▒██    ▒    ▒██▒  ██▒▓██   ▒    ▓  ██▒ ▓▒▓██ ▒ ██▒▒████▄     ██ ▀█   █ ▒██    ▒ ▓██▒▓  ██▒ ▓▒        
▓██ ░▄█ ▒▒██▒▒ ▓██░ ▒░▒███   ░ ▓██▄      ▒██░  ██▒▒████ ░    ▒ ▓██░ ▒░▓██ ░▄█ ▒▒██  ▀█▄  ▓██  ▀█ ██▒░ ▓██▄   ▒██▒▒ ▓██░ ▒░        
▒██▀▀█▄  ░██░░ ▓██▓ ░ ▒▓█  ▄   ▒   ██▒   ▒██   ██░░▓█▒  ░    ░ ▓██▓ ░ ▒██▀▀█▄  ░██▄▄▄▄██ ▓██▒  ▐▌██▒  ▒   ██▒░██░░ ▓██▓ ░         
░██▓ ▒██▒░██░  ▒██▒ ░ ░▒████▒▒██████▒▒   ░ ████▓▒░░▒█░         ▒██▒ ░ ░██▓ ▒██▒ ▓█   ▓██▒▒██░   ▓██░▒██████▒▒░██░  ▒██▒ ░     ██▓ 
░ ▒▓ ░▒▓░░▓    ▒ ░░   ░░ ▒░ ░▒ ▒▓▒ ▒ ░   ░ ▒░▒░▒░  ▒ ░         ▒ ░░   ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░░ ▒░   ▒ ▒ ▒ ▒▓▒ ▒ ░░▓    ▒ ░░       ▒▓▒ 
  ░▒ ░ ▒░ ▒ ░    ░     ░ ░  ░░ ░▒  ░ ░     ░ ▒ ▒░  ░             ░      ░▒ ░ ▒░  ▒   ▒▒ ░░ ░░   ░ ▒░░ ░▒  ░ ░ ▒ ░    ░        ░▒  
  ░░   ░  ▒ ░  ░         ░   ░  ░  ░     ░ ░ ░ ▒   ░ ░         ░        ░░   ░   ░   ▒      ░   ░ ░ ░  ░  ░   ▒ ░  ░          ░   
   ░      ░              ░  ░      ░         ░ ░                         ░           ░  ░         ░       ░   ░                ░  
                                                                                                                               ░
        """,
        "red",
        "italic",
    )
)



def main():
    print()
    state = start_new_run()
    game_loop(state)

if __name__ == "__main__":
    main()
    print("\n\n")
    # Color the menu prompt in red + italic
    print(colouring(
        "Choose: [1] Travel  [2] Inventory  [3] Rest  [H] Help  [Q] Quit",
        colour="red",
        style="italic"
    ))

