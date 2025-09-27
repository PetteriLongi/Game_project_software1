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
from textwrap import dedent, fill

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
    play_music, stop_music, set_volume, load_sfx, play_sfx,
    print_typewriter, flicker_line, dim_text,
)

#reserving channels for SFX
load_sfx("type_key", "Music/SFX/type_key.wav", volume=0.12, channel_id=7)
load_sfx("type_return", "Music/SFX/type_return.wav", volume=0.12, channel_id=6)


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

    # NOTE: Below is an old dictionary-style player example we kept for reference.
    # We now use the Player class above, which is cleaner and easier to extend.
#    player = {
#        "hp": 35,           # Current health
#        "max_hp": 65,       # Max health
#        "sanity": 15,       # Current sanity (mana)
#        "max_sanity": 15,   # Max sanity
#        "attack": (4, 8),   # Physical attack range (min, max)
#        "Weapon": None,
#        "inventory": [],
#        "manifestations": unlocked_manifestations   # List of unlocked manifestations
#    }

    # ==========================================
    # NARRATIVE INTRO (OPTIONAL)
    # ==========================================

    print_typewriter("""The journey leaves you hollow.
Another airport. Another silence where life should be.
But this time, it isn’t empty. 
Figures linger ahead, robes shifting like shadow and blood.
Their chants rise and fall, a hymn that claws at your skin.
Most you recognize, the same cultists who fell in Helsinki.
But one stands apart.
A heavy tome rests in his hands, its pages breathing with symbols that squirm like insects across the paper.
When he speaks, the air itself seems to recoil.

"I am an Apostle of the Hymn." His eyes narrow, fixing you with disbelief.

"What business does a stray civilian have here? How did you breach the veil?"
""", 
    mode="heartbeat",
    glitch_probability=0.02,
    sfx=True,                # enable SFX
    sfx_channel=7,           # channel used when loading
    sfx_key_name="type_key",
    #sfx_return_name="type_return"

    )

    # ==========================================
    # STARTING GEAR (FEEL FREE TO TWEAK)
    # ==========================================
    # Give the player some starting gear and items to try out in combat.
    # You can add more here to experiment.

    add_weapon_to_inventory(player, "Basic dagger")
    add_item_to_inventory(player, "Small Health Potion")
    add_item_to_inventory(player, "Large Health Potion")
    add_item_to_inventory(player, "Small Sanity Potion")
    add_item_to_inventory(player, "Large Sanity Potion")
    add_item_to_inventory(player, "5.56 Caliber", 10)               # AR-15 ammo reserve
    add_item_to_inventory(player, ".36 Caliber", 10)
    add_item_to_inventory(player, "Makkara", 1)
    add_weapon_to_inventory(player, "AR-15", current_mag=13)        # Starts with a full magazine

    # Pause so the player can read the setup text above (optional)
    input("\nPress enter to continue...")

    # ==========================================
    # ENCOUNTER 1
    # ==========================================
    # Prepare the first combat encounter (you can add up to 3 enemies in this list)
    enemies1 = [create_enemy("Abomination")]
    # Start combat with background music for atmosphere
    play_music("music/combat/2022-10-10_-_Right_Behind_You_-_www.FesliyanStudios.com.mp3", volume=0.0)
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
    print('oh no there are even more guys')

    reload_gun(player, consume_turn=False) # A way to reload equipped gun outside of combat by calling this function

    input("\nPress enter to continue...")

    enemies2 = [create_enemy('Apostle'), create_enemy('High Priest'), create_enemy('Cultist')]
    play_music("music/combat/2022-10-10_-_Right_Behind_You_-_www.FesliyanStudios.com.mp3", volume=0.0)
    combat(player, enemies2)
    pygame.mixer.music.fadeout(2000)

# TODO ideas for the future:
# - Add a resting system to recover HP/Sanity between battles
# - Add more guns and ammo types (e.g., shotgun shells)
# - Balance weapons and add more enemy types
# - Expand the player progression and story events
