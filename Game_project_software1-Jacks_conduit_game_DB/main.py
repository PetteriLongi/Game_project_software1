# conduit_game/main.py
from conduit_game.services import start_new_run
from conduit_game.ui.menu import game_loop
from conduit_game.repository import create_bloody_note, fetch_random_airports_excl_hel



#This is our H.P Lovecraft inspired software game project!

print("""
##      ## ######## ##        ######   #######  ##     ## ########    ########  #######     ######## ##     ## ########     ######      ###    ##     ## ######## 
##  ##  ## ##       ##       ##    ## ##     ## ###   ### ##             ##    ##     ##       ##    ##     ## ##          ##    ##    ## ##   ###   ### ##       
##  ##  ## ##       ##       ##       ##     ## #### #### ##             ##    ##     ##       ##    ##     ## ##          ##         ##   ##  #### #### ##       
##  ##  ## ######   ##       ##       ##     ## ## ### ## ######         ##    ##     ##       ##    ######### ######      ##   #### ##     ## ## ### ## ######   
##  ##  ## ##       ##       ##       ##     ## ##     ## ##             ##    ##     ##       ##    ##     ## ##          ##    ##  ######### ##     ## ##       
##  ##  ## ##       ##       ##    ## ##     ## ##     ## ##             ##    ##     ##       ##    ##     ## ##          ##    ##  ##     ## ##     ## ##       
 ###  ###  ######## ########  ######   #######  ##     ## ########       ##     #######        ##    ##     ## ########     ######   ##     ## ##     ## ########  
""")

print("HELLO I AM JACK I BIFFED IT AND I SAY BIFFED SINCE IM AUSTRALIAN KANGAROO")

airports = fetch_random_airports_excl_hel(10)


def main():
    print()
    state = start_new_run()
    game_loop(state)

if __name__ == "__main__":
    create_bloody_note(airports)
    main()
    print("\n\n")
