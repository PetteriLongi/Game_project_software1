#test
# doomclock_game.py
# ============================================================
# Doom Clock Combat Demo — standalone, no external libraries
# ============================================================

import random
from typing import Callable, Dict, List, Optional, Tuple

# ------------------------------------------------------------
# Utility: colored status bars
# -------------------------------------------------------
def draw_bar(label: str, current: int, maximum: int,
            bar_length: int = 20, color: str = "default",
            name_width: int = 12) -> str:
    ratio = max(0.0, min(1.0, (current / maximum) if maximum else 0.0))
    filled = int(ratio * bar_length)
    empty = bar_length - filled

    if color == 'hp':
        col = '\033[92m' if ratio > 0.6 else '\033[93m' if ratio > 0.3 else '\033[91m'
    elif color == 'sanity':
        col = '\033[94m'
    elif color == 'doom':
        # hotter as time runs out
        col = '\033[92m' if ratio > 0.75 else '\033[93m' if ratio > 0.5 else '\033[95m' if ratio > 0.25 else '\033[91m'
    else:
        col = '\033[0m'

    reset = '\033[0m'
    bar = f'{col}{"#" * filled}{"-" * empty}{reset}'
    return f'{label:<{name_width}}: [{bar}] {int(current)}/{int(maximum)}'


# ------------------------------------------------------------
# Core data objects (minimal but complete)
# ------------------------------------------------------------
class Weapon:
    def __init__(self, name: str, attack_range: Tuple[int, int], weapon_type: str = "melee", description: str = ""):
        self.name = name
        self.attack_range = attack_range
        self.weapon_type = weapon_type  # "melee" or "gun"
        self.description = description

class Consumable:
    def __init__(self, name: str, description: str, quantity: int = 1):
        self.name = name
        self.description = description
        self.quantity = quantity

    def use(self, player: dict) -> str:
        """Override in specific item subclasses."""
        return "\033[93mNothing happens.\033[0m"

class Bullets(Consumable):
    def __init__(self, quantity: int):
        super().__init__("Bullets", "A box of ammunition.", quantity)

class Bandage(Consumable):
    def __init__(self, amount: int = 5, quantity: int = 1):
        super().__init__("Bandage", f"Heal {amount} HP.", quantity)
        self.amount = amount

    def use(self, player: dict) -> str:
        if self.quantity <= 0:
            return "\033[93mNo bandages left.\033[0m"
        self.quantity -= 1
        healed = min(self.amount, player["max_hp"] - player["hp"])
        player["hp"] += healed
        return f"\033[92mYou apply a bandage and heal {healed} HP.\033[0m"

class Tonic(Consumable):
    def __init__(self, amount: int = 5, quantity: int = 1):
        super().__init__("Calming Tonic", f"Restore {amount} Sanity.", quantity)
        self.amount = amount

    def use(self, player: dict) -> str:
        if self.quantity <= 0:
            return "\033[93mNo tonic left.\033[0m"
        self.quantity -= 1
        restored = min(self.amount, player["max_sanity"] - player["sanity"])
        player["sanity"] += restored
        return f"\033[94mYou drink a tonic and restore {restored} Sanity.\033[0m"

class Manifestation:
    def __init__(self, name: str, sanity_cost: int, description: str, power: Callable[[dict, "Enemy"], str]):
        self.name = name
        self.sanity_cost = sanity_cost
        self.description = description
        self._power = power

    def use_skill(self, player: dict, target: "Enemy") -> str:
        if player["sanity"] < self.sanity_cost:
            return "\033[93mNot enough Sanity!\033[0m"
        player["sanity"] -= self.sanity_cost
        return self._power(player, target)

class Enemy:
    def __init__(self, name: str, hp: int, attack: Tuple[int, int],
                 description: str = "", special_attack: Optional[Callable[..., None]] = None):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.attack = attack
        self.description = description
        self.special_attack = special_attack  # (self, target) or (self, player)

    def __repr__(self):
        return f"<Enemy {self.name} {self.hp}/{self.max_hp}>"


# ------------------------------------------------------------
# Doom Clock (100 → 0)
# ------------------------------------------------------------
Log = List[str]
MilestoneFn = Callable[[dict, list, Log], None]
OnZeroFn = Callable[[dict, list, Log], None]

class DoomClock:
    """
    Countdown Doom Clock.
    Starts at 'start' (default 100) and decreases each turn until 0.
    Milestones trigger when thresholds are crossed.
    """

    def __init__(self, name: str = "Doom ⏳", start: int = 100,
                 milestones: Optional[Dict[int, MilestoneFn]] = None,
                 on_zero: Optional[OnZeroFn] = None):
        self.name = name
        self.start = int(start)
        self.ticks = int(start)
        self.milestones = milestones or {}
        self._hit = set()
        self.on_zero = on_zero
        self.resolved = False

    def countdown(self, n: int = 1, player: Optional[dict] = None,
                  enemies: Optional[list] = None, log: Optional[Log] = None,
                  reason: Optional[str] = None) -> bool:
        prev = self.ticks
        self.ticks = max(0, self.ticks - int(n))
        if log is not None and reason:
            log.append(f"\033[95m[Doom -{n}] {reason}\033[0m")

        # Fire milestones crossed this tick (e.g., crossing 75 from 76→74)
        for threshold in sorted(self.milestones.keys(), reverse=True):
            if prev >= threshold > self.ticks and threshold not in self._hit:
                self._hit.add(threshold)
                cb = self.milestones[threshold]
                if callable(cb):
                    cb(player or {}, enemies or [], log or [])

        if not self.resolved and self.ticks == 0:
            self.resolved = True
            if callable(self.on_zero):
                self.on_zero(player or {}, enemies or [], log or [])
            return True
        return False

    def add_time(self, n: int = 1, log: Optional[Log] = None, reason: Optional[str] = None):
        self.ticks = min(self.start, self.ticks + int(n))
        if log is not None and reason:
            log.append(f"\033[94m[Doom +{n}] {reason}\033[0m")

    def reset(self):
        self.ticks = self.start
        self._hit.clear()
        self.resolved = False


# ------------------------------------------------------------
# Combat loop (integrated with DoomClock)
# ------------------------------------------------------------
def combat(player: dict, enemies: List[Enemy], doom_clock: Optional[DoomClock] = None) -> bool:
    """
    Turn-based combat between the player and a list of enemies.
    Returns True if the player wins, False otherwise.
    """
    defending = False
    max_name_length = max(len(e.name) for e in enemies) if enemies else 12
    turn_counter = 1

    print(f"\n\033[95m--- COMBAT: {', '.join([e.name for e in enemies])} APPEARS! ---\033[0m")

    while player["hp"] > 0 and any(e.hp > 0 for e in enemies):
        turn_log: Log = []
        print(f"\n\033[96m--- Turn {turn_counter} ---\033[0m")

        # --- Display status bars for player and enemies ---
        enemy_bars = []
        for enemy in enemies:
            if enemy.hp > 0:
                enemy_bars.append(draw_bar(enemy.name, enemy.hp, enemy.max_hp, color='hp', name_width=max_name_length))
            else:
                enemy_bars.append(f'{enemy.name:<{max_name_length}}: [\033[91mDEFEATED\033[0m]')

        player_lines = 2 + (1 if doom_clock else 0)
        total_lines = max(len(enemy_bars), player_lines)

        for i in range(total_lines):
            if i == 0:
                left = draw_bar("Your HP", player["hp"], player["max_hp"], color="hp")
            elif i == 1:
                left = draw_bar("Sanity", player["sanity"], player["max_sanity"], color="sanity")
            elif i == 2 and doom_clock:
                left = draw_bar(doom_clock.name, doom_clock.ticks, doom_clock.start, color="doom")
            else:
                left = " " * 42
            right = enemy_bars[i] if i < len(enemy_bars) else ""
            print(f"{left:<40} || {right}")

        # --- Action menu ---
        print("\nChoose your action:")
        print("1. Attack (physical strike)")
        print("2. Defend (reduce next damage)")
        print("3. Manifest (use a special skill)")
        print("4. Inventory")
        choice = input("> ").strip()

        acted = False

        # =============== PLAYER: ATTACK ======================
        if choice == "1":
            living = [e for e in enemies if e.hp > 0]
            if not living:
                break
            print('\nChoose a target')
            for i, e in enumerate(living, 1):
                print(f'{i}. {e.name} ({e.hp}/{e.max_hp} HP)')
            pick = input("> ").strip()

            if pick.isdigit() and 1 <= int(pick) <= len(living):
                target = living[int(pick) - 1]
                dmg = 0
                weapon = player.get("Weapon")
                weapon_name = "your fists"

                if weapon:
                    weapon_name = weapon.name
                    if weapon.weapon_type == "gun":
                        bullets = next((item for item in player["inventory"]
                                        if isinstance(item, Bullets)), None)
                        if bullets and bullets.quantity > 0:
                            dmg = random.randint(*weapon.attack_range)
                            bullets.quantity -= 1
                            turn_log.append(f"\033[92mYou fire {weapon_name}! ({bullets.quantity} bullets left)\033[0m")
                            if bullets.quantity <= 0:
                                turn_log.append("\033[93mYou have run out of bullets!\033[0m")
                                player["inventory"].remove(bullets)
                        else:
                            turn_log.append("\033[91mNo bullets left! You cannot fire your gun.\033[0m")
                    else:
                        dmg = random.randint(*weapon.attack_range)
                else:
                    dmg = random.randint(*player.get("attack", (1, 3)))

                target.hp = max(0, target.hp - dmg)
                acted = True
                turn_log.append(f"\033[92mYou strike {target.name} with {weapon_name} for {dmg} damage!\033[0m")

                if doom_clock and target.hp == 0:
                    doom_clock.add_time(1, turn_log, reason="Slain foe disrupts the ritual.")
            else:
                turn_log.append("\033[93mYou hesitate and do nothing!\033[0m")

        # =============== PLAYER: DEFEND ======================
        elif choice == "2":
            defending = True
            acted = True
            turn_log.append("\033[94mYou brace yourself for the next attack...\033[0m")

        # =============== PLAYER: MANIFEST ====================
        elif choice == "3":
            if not player.get("manifestations"):
                turn_log.append("\033[93mYou have no manifestations unlocked yet!\033[0m")
            else:
                print("\nChoose a manifestation:")
                for i, m in enumerate(player["manifestations"], 1):
                    print(f"{i}. {m.name} (Cost: {m.sanity_cost}) - {m.description}")
                pick = input("> ").strip()
                if pick.isdigit() and 1 <= int(pick) <= len(player["manifestations"]):
                    chosen = player["manifestations"][int(pick) - 1]
                    living = [e for e in enemies if e.hp > 0]
                    if not living:
                        break
                    print("\nChoose a target:")
                    for i, e in enumerate(living, 1):
                        print(f"{i}. {e.name} ({e.hp}/{e.max_hp} HP)")
                    target_pick = input("> ").strip()
                    if target_pick.isdigit() and 1 <= int(target_pick) <= len(living):
                        target = living[int(target_pick) - 1]
                        result = chosen.use_skill(player, target)
                        acted = True
                        turn_log.append(result)
                        if doom_clock:
                            doom_clock.countdown(1, player, enemies, turn_log, reason="Manifestation strains reality.")
                else:
                    turn_log.append("\033[93mYou hesitate and do nothing!\033[0m")

        # =============== PLAYER: INVENTORY ===================
        elif choice == "4":
            inv = player.get("inventory", [])
            if not inv:
                turn_log.append("\033[93mYour inventory is empty!\033[0m")
            else:
                weapons = [it for it in inv if isinstance(it, Weapon)]
                consumables = [it for it in inv if isinstance(it, Consumable) and not isinstance(it, Weapon)]
                total_items = []
                index = 1

                print("\nInventory:\nWeapons:")
                if weapons:
                    for w in weapons:
                        equipped = ' (equipped)' if player.get("Weapon") is w else ''
                        print(f"{index}. {w.name}{equipped} - {w.description}")
                        total_items.append(w)
                        index += 1
                else:
                    print("  (none)")

                print("\nConsumables:")
                if consumables:
                    for c in consumables:
                        qty = getattr(c, "quantity", None)
                        qty_str = f" x{qty}" if qty is not None else ""
                        print(f"{index}. {c.name}{qty_str} - {c.description}")
                        total_items.append(c)
                        index += 1
                else:
                    print("  (none)")

                print("0. Back to action menu")
                pick = input("\nChoose an item to equip/use (or 0 to back out):\n> ").strip()

                if pick == "0":
                    turn_log.append("\033[94mYou exit the inventory.\033[0m")
                elif pick.isdigit() and 1 <= int(pick) <= len(total_items):
                    selected = total_items[int(pick) - 1]
                    if isinstance(selected, Weapon):
                        player["Weapon"] = selected
                        acted = True
                        turn_log.append(f"\033[92mYou equipped {selected.name}\033[0m")
                    else:
                        result = selected.use(player)
                        if result:
                            acted = True
                            turn_log.append(result)
                        if hasattr(selected, "quantity") and selected.quantity <= 0:
                            turn_log.append(f"\033[91m{selected.name} is depleted and removed!\033[0m")
                            inv.remove(selected)
                else:
                    turn_log.append("\033[93mInvalid choice, doing nothing...\033[0m")

        else:
            turn_log.append("\033[93mYou fumble and lose precious moments!\033[0m")

        # ---------------- ENEMY TURNS ------------------------
        special_happened = False
        for enemy in enemies:
            if enemy.hp <= 0:
                continue

            turn_log.append(f"\033[91m{enemy.name} prepares to act!\033[0m")
            if getattr(enemy, "special_attack", None) and random.random() < 0.3:
                special_happened = True
                # healer style if description hints at it
                if "heal" in enemy.description.lower():
                    allies = [e for e in enemies if e.hp > 0]
                    if allies:
                        target = min(allies, key=lambda x: x.hp)
                        enemy.special_attack(enemy, target)
                        turn_log.append(f"{enemy.name} uses a special ability on {target.name}")
                else:
                    enemy.special_attack(enemy, player)
                    turn_log.append(f"{enemy.name} uses a special ability on you!")
            else:
                dmg = random.randint(*enemy.attack)
                if defending:
                    dmg //= 2
                player["hp"] = max(0, player["hp"] - dmg)
                turn_log.append(f"\033[91m{enemy.name} strikes you for {dmg} damage!\033[0m")

        defending = False

        # ---------------- DOOM PROGRESSION -------------------
        if doom_clock:
            doom_clock.countdown(1, player, enemies, turn_log, reason="Time passes.")
            if not acted:
                doom_clock.countdown(1, player, enemies, turn_log, reason="Hesitation feeds the ritual.")
            if special_happened:
                doom_clock.countdown(1, player, enemies, turn_log, reason="Eldritch power surges.")

            if doom_clock.resolved:
                print("\n\033[91mThe Doom Clock reaches zero. The ritual completes...\033[0m")
                return False

        # ---------------- TURN LOG ---------------------------
        print("\n\033[95m" + "=" * 50 + "\033[0m")
        for entry in turn_log:
            print(entry)
        print("\033[95m" + "=" * 50 + "\033[0m")

        # ---------------- WIN / LOSS -------------------------
        if all(e.hp <= 0 for e in enemies):
            print("\n\033[92mAll enemies have been defeated! Victory is yours!\033[0m")
            return True

        if player["hp"] <= 0:
            break

        turn_counter += 1

    if player["hp"] <= 0:
        print("\n\033[91mYour body collapses... The cult claims another victim.\033[0m")
    return False


# ------------------------------------------------------------
# Demo setup (run this file to play a short fight)
# ------------------------------------------------------------
def _demo_special_heal(self: Enemy, ally: Enemy):
    healed = min(4, ally.max_hp - ally.hp)
    ally.hp += healed

def _demo_special_smite(self: Enemy, player: dict):
    dmg = random.randint(3, 6)
    player["hp"] = max(0, player["hp"] - dmg)

def make_demo_player() -> dict:
    revolver = Weapon("Revolver", (4, 8), weapon_type="gun", description="Reliable sidearm.")
    bat = Weapon("Nail Bat", (2, 5), description="Splinters and pain.")
    m1 = Manifestation(
        "Hex Bolt", 3, "Arcane blast of force (3–7 dmg).",
        lambda _p, t: (lambda d: (setattr(t, "hp", max(0, t.hp - d)) or f"\033[95mHex Bolt hits {t.name} for {d}!\033[0m"))(random.randint(3, 7))
    )
    return {
        "name": "Investigator",
        "hp": 20, "max_hp": 20,
        "sanity": 10, "max_sanity": 10,
        "attack": (1, 3),
        "Weapon": revolver,
        "inventory": [revolver, bat, Bullets(6), Bandage(5, 2), Tonic(5, 1)],
        "manifestations": [m1],
    }

def make_demo_enemies() -> List[Enemy]:
    acolyte = Enemy("Acolyte", 10, (1, 3), description="Fanatic with a rusty blade.")
    priest = Enemy("Blood Priest", 14, (2, 4), description="Can heal allies.", special_attack=_demo_special_heal)
    wraith = Enemy("Wailing Wraith", 12, (1, 5), description="Shrieks that scorch the soul.", special_attack=_demo_special_smite)
    return [acolyte, priest, wraith]

def make_demo_clock() -> DoomClock:
    def on_75(_p, _e, log: Log):
        log.append("\033[93mThe sigils glow brighter. You feel watched.\033[0m")

    def on_50(_p, _e, log: Log):
        log.append("\033[93mA low hum fills the chamber. The veil thins.\033[0m")

    def on_25(_p, _e, log: Log):
        log.append("\033[91mCracks rip across reality. You taste iron.\033[0m")

    def on_zero(player: dict, _e, log: Log):
        log.append("\033[91mA rift tears open as the ritual concludes!\033[0m")
        # Optional: instant defeat effect
        player["hp"] = max(0, player["hp"] - player["hp"])

    milestones = {75: on_75, 50: on_50, 25: on_25}
    return DoomClock(start=100, milestones=milestones, on_zero=on_zero)

def main():
    print("\n\033[96mDoom Clock Demo — defeat the cult before time runs out!\033[0m")
    player = make_demo_player()
    enemies = make_demo_enemies()
    clock = make_demo_clock()
    combat(player, enemies, clock)

if __name__ == "__main__":
    main()

