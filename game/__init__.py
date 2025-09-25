# ==========================================
# IMPORTS: BRINGING IN OTHER MODULES
# ==========================================


# Import the combat function from the combat module
# This function contains the main combat loop where the player fights enemies
from .combat import combat


# Import the Manifestation class and the manifestation_library from manifestations module
# - Manifestation class: used to create new summonable abilities
# - manifestation_library: dictionary of pre-defined manifestations
from .manifestations import manifestation_library, Manifestation


# Import the enemy_library dictionary and create_enemy function from enemies module
# - enemy_library: stores templates for all enemies in the game
# - create_enemy: function to create a fresh enemy instance based on a template
from .enemies import enemy_library, create_enemy

# Import item and weapon utilities from items module
# - weapon_library: stores all available weapons
# - consumable_library: stores all available consumable items (potions, ammo, etc.)
# - add_item_to_inventory: function to add consumables to the player's inventory
# - add_weapon_to_inventory: function to add weapons to the player's inventory
from .items import weapon_library, consumable_library, add_item_to_inventory, add_weapon_to_inventory