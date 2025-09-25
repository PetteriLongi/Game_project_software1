import random


# ==========================================
# Enemy Class
# ==========================================

class Enemy:
    """
    Represents an enemy in the game.
    Each enemy has a name, difficulty level, health points (HP),
    attack range, optional special attack, and a description.
    """
    def __init__(self, name, difficulty, hp, attack, special_attack=None, description=""):
        self.name = name                    # Enemy's name
        self.difficulty = difficulty        # Difficulty rating (can be used for scaling loot, XP, etc.)
        self.hp = hp                        # Current health
        self.max_hp = hp                    # Maximum health
        self.attack = attack                # Tuple (min_damage, max_damage) for regular attack
        self.special_attack = special_attack  # Optional function for special abilities
        self.description = description      # Description for flavor text

    def take_turn(self, player):
        """
        Called when the enemy takes its turn in combat.
        Decides whether to use special attack or normal attack.
        """
        if self.special_attack and random.random() < 0.3:   # 30% chance to use special attack
            self.special_attack(self, player)
        else:
            dmg = random.randint(*self.attack)              # Random damage in the attack range
            player["hp"] -= dmg
            print(f"\n{self.name} strikes you for {dmg} damage.!")


# ==========================================
# Special Attacks for Enemies
# ==========================================

def apostle_buff(enemy, player):
    """
    Special attack for Apostles.
    Heals the enemy a small random amount.
    """
    heal = random.randint(3, 6)
    enemy.hp = min(enemy.max_hp, enemy.hp + heal)
    print(f'\n{enemy.name} chants a hymn, regaining {heal} health')


def priest_curse(enemy, player):
    """
    Special attack for High Priests.
    Reduces the player's sanity.
    """
    dmg = random.randint(4, 8)
    player["sanity"] = max(0, player["sanity"] - dmg)
    print(f"\n{enemy.name} invokes a dark curse!")
    print(f"Your sanity is reduced by {dmg}!")


def whisperer_psychic(enemy, player):
    """
    Special attack for Whisperers.
    Deals minor HP and sanity damage.
    """
    dmg = random.randint(5, 10)
    player["hp"] -= dmg
    player["sanity"] = max(0, player["sanity"] - 2)
    print(f"\n{enemy.name} whispers forbidden truths...")
    print(f"You take {dmg} psychic damage and lose 2 sanity!")


def abomination_crush(enemy, player):
    """
    Special attack for Abominations.
    Deals high HP damage.
    """
    dmg = random.randint(8, 14)
    player["hp"] -= dmg
    print(f"\n{enemy.name} crushes you with monstrous strength for {dmg} damage!")



# ==========================================
# Enemy Library
# ==========================================

# This is a dictionary of all predefined enemies in the game.
# Each entry can be used to spawn a fresh copy of that enemy.
enemy_library = {
    # Difficulty 1: Cultists
    "Cultist": Enemy("Cultist", difficulty=1, hp=20, attack=(3, 6), description="Fanatical servant of the cult."),

    # Difficulty 2: Apostles
    "Apostle": Enemy("Apostle", difficulty=2, hp=28, attack=(4, 7), special_attack=apostle_buff,
                     description="Disciple that heals itself with hymns."),

    # Difficulty 3: High Priests
    "High Priest": Enemy("High Priest", difficulty=3, hp=35, attack=(5, 9), special_attack=priest_curse,
                         description="Leader who curses your sanity."),

    # Difficulty 4: Whisperers
    "Whisperer": Enemy("Whisperer", difficulty=4, hp=30, attack=(4, 10), special_attack=whisperer_psychic,
                       description="Maddening voice that eats away at your mind."),

    # Difficulty 5: Abominations
    "Abomination": Enemy("Abomination", difficulty=5, hp=50, attack=(6, 12), special_attack=abomination_crush,
                         description="Horrific mutation of flesh and shadow."),
}

# ==========================================
# Helper function to create fresh enemy instances
# ==========================================

def create_enemy(name):
    """
    Creates a new instance of an enemy based on the template in the enemy library.
    This ensures each enemy starts with full HP and default stats.
    """
    template = enemy_library[name]
    return Enemy(
        template.name,
        template.difficulty,
        template.max_hp,  # Reset HP to full
        template.attack,
        template.special_attack,
        template.description
    )