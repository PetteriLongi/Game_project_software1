import random

# ==========================================
# CLASS DEFINITION: MANIFESTATION
# ==========================================

class Manifestation:
    """
    Represents a summonable entity (like a magical or psychic power)
    that the player can use in combat.
    """
    def __init__(self, name, sanity_cost, special_attack, description):
        self.name = name                        # Name of the manifestation
        self.sanity_cost = sanity_cost          # How much sanity (mana) it costs to use
        self.special_attack = special_attack    # Function that runs when used
        self.description = description          # Description shown in menu

    # Method to use the manifestation's skill in combat
    def use_skill(self, player, enemy):
        """
        Attempts to use the manifestation's special ability in combat.

        Args:
            player: Dictionary representing the player (with HP, sanity, inventory, etc.)
            enemy: Enemy object to target

        Returns:
            Result of the special attack, or None if not enough sanity
        """
        if player["sanity"] >= self.sanity_cost:                     # Check if player has enough sanity
            player["sanity"] -= self.sanity_cost                     # Reduce sanity cost
            return self.special_attack(player, enemy)                # Call its special attack function
        else:
            print(f"\nNot enough sanity to summon {self.name}'s power!")
            return None


# ==========================================
# SPECIAL ATTACK FUNCTIONS
# ==========================================

def fear_special(player, enemy):
    """
    Fear manifestation: Deals strong psychic damage to the enemy.
    """
    dmg = random.randint(8, 14)         # Damage range for Fear
    enemy.hp -= dmg                           # Apply damage
    print(f"\nManifestation of Fear whispers horrors into {enemy.name}!")
    print(f"It deals {dmg} psychic damage!")
    return dmg

#Rages special attack
def rage_special(player, enemy):
    """
    Rage manifestation: High damage to enemy but player suffers recoil.
    """
    dmg = random.randint(10, 12)        # Low - High damage
    enemy.hp -= dmg
    recoil = 2                                # But player also takes recoil damage
    player["hp"] -= recoil
    print(f"\nManifestation of Rage erupts in violent fury!")
    print(f"It deals {dmg} damage but you suffer {recoil} recoil.")
    return dmg

#despairs special attack steals HP from the enemy
def despair_special(player, enemy):
    """
    Despair manifestation: Damages enemy and heals the player.
    """
    dmg = random.randint(4, 8)
    enemy.hp -= dmg
    heal = random.randint(3, 6)
    player["hp"] = min(player["max_hp"], player["hp"] + heal)
    print(f"\nManifestation of Despair drains life from {enemy.name}!")
    print(f"It deals {dmg} damage and heals you for {heal}.")
    return dmg

# ==========================================
# MANIFESTATION LIBRARY
# ==========================================

# This dictionary stores all available manifestations for easy access
manifestation_library = {
    "Fear": Manifestation("Fear", sanity_cost=5, special_attack=fear_special, description="Strong psychic damage."),
    "Rage": Manifestation("Rage", sanity_cost=6, special_attack=rage_special, description="High damage but hurts you."),
    "Despair": Manifestation("Despair", sanity_cost=4, special_attack=despair_special, description="Damage + life steal."),
}