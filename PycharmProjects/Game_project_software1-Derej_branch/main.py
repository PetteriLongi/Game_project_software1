#This is our H.P Lovecraft inspired software game project!
from game.items import add_weapon_to_inventory, add_item_to_inventory

print("""
##      ## ######## ##        ######   #######  ##     ## ########    ########  #######     ######## ##     ## ########     ######      ###    ##     ## ######## 
##  ##  ## ##       ##       ##    ## ##     ## ###   ### ##             ##    ##     ##       ##    ##     ## ##          ##    ##    ## ##   ###   ### ##       
##  ##  ## ##       ##       ##       ##     ## #### #### ##             ##    ##     ##       ##    ##     ## ##          ##         ##   ##  #### #### ##       
##  ##  ## ######   ##       ##       ##     ## ## ### ## ######         ##    ##     ##       ##    ######### ######      ##   #### ##     ## ## ### ## ######   
##  ##  ## ##       ##       ##       ##     ## ##     ## ##             ##    ##     ##       ##    ##     ## ##          ##    ##  ######### ##     ## ##       
##  ##  ## ##       ##       ##    ## ##     ## ##     ## ##             ##    ##     ##       ##    ##     ## ##          ##    ##  ##     ## ##     ## ##       
 ###  ###  ######## ########  ######   #######  ##     ## ########       ##     #######        ##    ##     ## ########     ######   ##     ## ##     ## ########  
""")

# Import combat function and manifestation library from the package
from game import combat, manifestation_library, create_enemy
from game import weapon_library, consumable_library, add_weapon_to_inventory, add_item_to_inventory

print("TEST")

if __name__ == "__main__":
    # Player starts with only Fear unlocked
    unlocked_manifestations = [manifestation_library["Fear"]]

    player = {
        "hp": 35,           # Current health
        "max_hp": 35,       # Max health
        "sanity": 15,       # Current sanity (mana)
        "max_sanity": 15,   # Max sanity
        "attack": (4, 8),   # Physical attack range (min, max)
        "Weapon": None,
        "inventory": [],
        "manifestations": unlocked_manifestations   # List of unlocked manifestations
    }

    #testing adding a weapon to use in combat
    add_weapon_to_inventory(player, "Basic dagger")
    add_item_to_inventory(player, "Health Potion")
    add_item_to_inventory(player, "Bullets", 10)

    # Enemy group (up to 3)
    enemies1 = [create_enemy("Cultist")]
     # Start combat
    combat(player, enemies1)
    print("\nIt seems you have found something")
    add_weapon_to_inventory(player, "Old revolver")
    print('oh no there are even more guys')

    enemies2 = [create_enemy('Cultist'),create_enemy('High Priest')]
    combat(player, enemies2)

#ADD A SYSTEM THAT YOU CAN RECOVER HP AND SANITY BY RESTING AFTER COMBAT; NOT IN COMBAT
#MAYBE MORE GUNS WITH VARIABLE BULLET TYPES (SHOTGUN, AR)
#RELOAD FUNCTION GUNS; CAN ONLY HOLD SO MANY BULLETS
#JACK WANTED MUSIC IN THE GAME