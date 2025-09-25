# ==========================================
# Classes for Items, Weapons, and Consumables
# ==========================================

class Item:
    """
    Base class for all items in the game.
    Represents any object the player can carry/use.
    """
    def __init__(self, name, description, effect=None):
        self.name = name                # Name of the item
        self.description = description  # Short description of the item
        self.effect = effect            # Optional function applied when the item is used

    def use(self, target):
        """
        Use the item on a target (player or enemy).
        If it has an effect function, apply it and return its result as a string.
        """
        if self.effect:
            return self.effect(target)
        else:
            return f"{self.name} has no effect!"

class Weapon(Item):
    """
    Represents a weapon. Inherits from Item because weapons are also items.
    """
    def __init__(self, name, description, attack_range, weapon_type='melee'):
        super().__init__(name, description)  # Initialize Item attributes
        self.attack_range = attack_range     # Tuple (min_attack, max_attack) for damage
        self.weapon_type = weapon_type       # 'melee' or 'gun'

class Consumable(Item):
    """
    Represents consumable items, like potions or ammo.
    Inherits from Item but adds quantity tracking.
    """
    def __init__(self, name, description, effect=None, quantity=1):
        super().__init__(name, description, effect)
        self.quantity = quantity  # How many of this item the player has

    def use(self, player):
        """
        Use the consumable on the player.
        Reduces quantity, applies effect, and returns a message for display.
        """
        if self.quantity > 0:
            self.quantity -= 1
            msg = ""
            if self.effect:
                msg = self.effect(player)   # Call the effect function
            if self.quantity <= 0:
                # Show depletion message in red
                msg += f"\n\033[91m{self.name} is depleted!\033[0m"
            return msg
        else:
            return f"\033[91mYou have no {self.name} left!\033[0m"

# ==========================================
# Functions to add items or weapons to inventory
# ==========================================

def add_weapon_to_inventory(player, weapon_name):
    """
    Adds a weapon from the weapon library to the player's inventory.
    Prints a message to confirm.
    """
    weapon = weapon_library.get(weapon_name)
    if weapon:
        player["inventory"].append(weapon)
        print(f"\nYou obtained a new weapon: {weapon.name}!")
    else:
        print(f"Weapon '{weapon_name}' does not exist in the library.")

def add_item_to_inventory(player, item_name, amount=1):
    """
    Adds a consumable item to the player's inventory.
    If the item already exists, increases the quantity.
    """
    if item_name in consumable_library:
        #check if the player has these already
        for item in player["inventory"]:
            if isinstance(item, Consumable) and item.name == item_name:
                item.quantity += amount
                print(f"You obtained {amount}x {item.name}! You now have: {item.quantity} of these")
                return

        # Otherwise, create a new item and add it
        base_item = consumable_library[item_name]
        new_item = Consumable(base_item.name, base_item.description, base_item.effect, quantity=amount)
        player["inventory"].append(new_item)
        print(f"You obtained {amount}x {new_item.name}!")
    else:
        print(f"Item '{item_name}' does not exist in the library.")

"""ITEM EFFECTS START HERE"""


# ==========================================
# Effects for consumable items
# ==========================================

def heal_hp(player):
    """
    Effect function for Health Potion.
    Restores 10 HP, but not above the player's max HP.
    Returns a formatted string to display in combat.
    """
    amount = 10
    player["hp"] = min(player["max_hp"], player["hp"] + amount)
    return f"\033[92mYou drink a Health Potion and recover {amount} HP!\033[0m"

def restore_sanity(player):
    """
    Effect function for Sanity Potion.
    Restores 10 sanity points.
    Returns a formatted string to display in combat.
    """
    amount = 10
    player["sanity"] = min(player["max_sanity"], player["sanity"] + amount)
    return f"\033[94mYou use a Sanity Potion and restore {amount} sanity!\033[0m"



"""WEAPON AND CONSUMABLE LIBRARIES START HERE"""

# ==========================================
# Weapon and consumable libraries
# ==========================================

# Dictionary of all weapons in the game
weapon_library = {
    "Basic dagger" : Weapon("Basic dagger", "Quick and light, but low damage", attack_range=(7,12), weapon_type='melee'),
    "Old revolver" : Weapon("Old revolver", "It has seen better days but seems to still be usable", attack_range=(10,16), weapon_type='gun'),
    "Jack's hammer" : Weapon("jack's hammer", "jack's beloved hammer of destruction", attack_range=(50,999), weapon_type='melee'),
    # Additional weapons can be added here
}

# Dictionary of all consumable items in the game
consumable_library = {
    "Health Potion": Consumable("Health Potion", "This odd liquid seems to have healing properties", effect=heal_hp, quantity=0),
    "Sanity Potion": Consumable("Sanity Potion", "Restores 10 sanity.", effect=restore_sanity, quantity=0),
    "Bullets": Consumable("Bullets", "Ammo for guns.", effect=None, quantity=0),
    # Additional items like antidotes, elixirs, etc., can be added here
}