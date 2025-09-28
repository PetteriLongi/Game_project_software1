"""
main.py - Demo entry point for the Lovecraft-inspired terminal RPG.

Instructions:
1. Run this file to play the demo encounters.
2. The script sets up the player, prints a short narrative intro, gives starter gear,
   and runs two combat encounters using helpers from the `game/` package.
"""
# ==========================================
# TITLE BANNER (VISUAL FLAIR)
# ==========================================
#This is our H.P Lovecraft inspired software game project!
# Fancy ASCII title for the game (just visual flair)
print("""
##      ## ######## ##        ######   #######  ##     ## ########    ########  #######     ######## ##     ## ########     ######      ###    ##     ## ######## 
##  ##  ## ##       ##       ##    ## ##     ## ###   ### ##             ##    ##     ##       ##    ##     ## ##          ##    ##    ## ##   ###   ### ##       
##  ##  ## ##       ##       ##       ##     ## #### #### ##             ##    ##     ##       ##    ##     ## ##          ##         ##   ##  #### #### ##       
##  ##  ## ######   ##       ##       ##     ## ## ### ## ######         ##    ##     ##       ##    ######### ######      ##   #### ##     ## ## ### ## ######   
##  ##  ## ##       ##       ##       ##     ## ##     ## ##             ##    ##     ##       ##    ##     ## ##          ##    ##  ######### ##     ## ##       
##  ##  ## ##       ##       ##    ## ##     ## ##     ## ##             ##    ##     ##       ##    ##     ## ##          ##    ##  ##     ## ##     ## ##       
 ###  ###  ######## ########  ######   #######  ##     ## ########       ##     #######        ##    ##     ## ########     ######   ##     ## ##     ## ########  
""")

import shutil
import pygame

# ==========================================
# LOCAL IMPORTS
# ==========================================
from game import (
    combat, reload_gun,
    Player,
    manifestation_library,
    create_enemy,
    add_weapon_to_inventory, add_item_to_inventory,
    play_music,
    print_typewriter,
    ui_print,
)
# UI capability flag (for hinting Rich availability to the user)
from game.ui import RICH_AVAILABLE
# Getting all the sound files from sfx_loader and registering them
from game.sfx_loader import register_all_sfx
register_all_sfx()

if __name__ == "__main__":
    # ==========================================
    # PLAYER SETUP
    # ==========================================
    # Create our player character.
    # Start with only the "Fear" manifestation unlocked to keep the tutorial simple.
    unlocked_manifestations = [manifestation_library["Fear"], manifestation_library["Hope"], manifestation_library["Rage"], manifestation_library["Vindication"]]
    player = Player("Hero", unlocked_manifestations)

    # Determine terminal width for nicer wrapping (fallback to 80)
    term_width = shutil.get_terminal_size(fallback=(80, 20)).columns
    wrap_width = max(50, min(100, term_width))

    # Hint Rich availability (so users understand UI mode)
    if not RICH_AVAILABLE:
        print("\nNote: Rich not detected. Using ASCII UI. Install 'rich' for enhanced inventory and status visuals.")
    else:
        print("\nRich UI enabled. Enjoy enhanced inventory and status visuals.")

    # ==========================================
    # NARRATIVE INTRO (OPTIONAL)
    # ==========================================
    play_music("Music/ambience/Piano_suspense.mp3", volume=0.12, loop=True)

    print_typewriter("""The journey leaves you hollow.
Another airport.
Another silence where life should be.
But this time,
it isn’t empty.
Figures linger ahead,
robes shifting like shadow and blood.
Their chants rise and fall,
a hymn that claws at your skin.
Most you recognize,
the same cultists who fell in Helsinki.
But one stands apart.
A heavy tome rests in his hands,
its pages breathing with symbols
that squirm like insects across the paper.
When he speaks,
the air itself seems to recoil.

"I am an Apostle of the Hymn."

His eyes narrow,
fixing you with disbelief.

"What business does a stray civilian have here?
How did you breach the veil?"
""",
        mode="calm", sfx=True, sfx_channel=7, sfx_channel_2=6, sfx_key_name="type_key")

    # ==========================================
    # STARTING GEAR (FEEL FREE TO TWEAK)
    # ==========================================
    # Give the player some starting gear and items to try out in combat.
    # You can add more here to experiment.

    add_weapon_to_inventory(player, "Basic dagger")
    add_weapon_to_inventory(player, "Sword")
    add_item_to_inventory(player, "Small Health Potion")
    add_item_to_inventory(player, "Large Health Potion")
    add_item_to_inventory(player, "Small Sanity Potion")
    add_item_to_inventory(player, "Large Sanity Potion")
    add_item_to_inventory(player, "pistol ammo", 10)               # AR-15 ammo reserve
    add_item_to_inventory(player, "rifle ammo", 10)
    add_item_to_inventory(player, "submachine ammo", 10)
    add_weapon_to_inventory(player, "AR-15", current_mag=13)        # Starts with a full magazine
    add_weapon_to_inventory(player, "MP7", current_mag=14)

    # Pause so the player can read the setup text above (optional)
    #pygame.mixer.music.fadeout(2000) #this causes a 2, second delay before the combat starts
    input("\nPress enter to continue...")
   
    # ==========================================
    # ENCOUNTER 1
    # ==========================================
    # Prepare the first combat encounter (you can add up to 3 enemies in this list)
    enemies1 = [create_enemy("Anatomist")]
    # Start combat with background music for atmosphere
    play_music("Music/combat/Anxiety.mp3", volume=0.12)
    combat(player, enemies1)
    # Fade out the music a bit after combat ends
    pygame.mixer.music.fadeout(2000)
    #stop_music()

    # ==========================================
    # ENCOUNTER 2
    # ==========================================
    # Second encounter setup
    print("\nIt seems you have found something")
    add_weapon_to_inventory(player, "Old revolver")  # Comes with a full magazine
    ui_print('oh no there are even more guys', 'red')

    reload_gun(player, consume_turn=False) # A way to reload equipped gun outside of combat by calling this function

    input("\nPress enter to continue...")

    enemies2 = [create_enemy('Apostle'), create_enemy('High Priest'), create_enemy('Cultist')]
    play_music("Music/combat/Behind_you.mp3", volume=0.12)
    combat(player, enemies2)
    pygame.mixer.music.fadeout(2000)

