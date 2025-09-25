# ==========================================
# IMPORTS
# ==========================================
import random
from typing import Callable, Dict, List, Optional

# If these classes exist elsewhere in your codebase, remove these stubs.
# They are here only so this file runs stand-alone.
class Weapon: ...
class Consumable: ...
# Enemy is expected to have: name, hp, max_hp, attack (tuple), description, special_attack (callable|None)

# ==========================================
# DRAW BAR (adds 'doom' color)
# ==========================================
def draw_bar(label, current, maximum, bar_length=20, color="default", name_width=12):
    ratio = current / maximum if maximum > 0 else 0
    filled = int(ratio * bar_length)
    empty = bar_length - filled

    if color == 'hp':
        col = '\033[92m' if ratio > 0.6 else '\033[93m' if ratio > 0.3 else '\033[91m'
    elif color == 'sanity':
        col = '\033[94m'
    elif color == 'doom':
        # As time runs out, the bar gets hotter
        col = '\033[92m' if ratio > 0.75 else '\033[93m' if ratio > 0.5 else '\033[95m' if ratio > 0.25 else '\033[91m'
    else:
        col = '\033[0m'

    reset = '\033[0m'
    bar = f'{col}{"#" * filled}{"-" * empty}{reset}'
    return f'{label:<{name_width}}: [{bar}] {int(current)}/{int(maximum)}'


# ==========================================
# DOOM CLOCK (100 → 0 countdown)
# ==========================================
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


# ==========================================
# COMBAT LOOP (integrated with DoomClock)
# ==========================================
def combat(player, enemies, doom_clock: Optional[DoomClock] = None):
    """
    Turn-based combat between the player and a list of enemies.
    Integrated with a 100→0 DoomClock that counts down each round.
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

        # Player side shows HP, Sanity, (and Doom if provided)
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

        acted = False  # track if the player made a meaningful action

        # ========================================
        # PLAYER TURN: ATTACK
        # ========================================
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
                weapon = player.get("Weapon")

                if weapon:
                    weapon_name = getattr(weapon, "name", "weapon")
                    if getattr(weapon, "weapon_type", "melee") == "gun":
                        bullets = next((item for item in player["inventory"]
                                        if isinstance(item, Consumable) and getattr(item, "name", "").lower() == "bullets"), None)
                        if bullets and getattr(bullets, "quantity", 0) > 0:
                            dmg = random.randint(*getattr(weapon, "attack_range", (1, 4)))
                            bullets.quantity -= 1
                            turn_log.append(f"\033[92mYou fire {weapon_name}! ({bullets.quantity} bullets left)\033[0m")
                            if bullets.quantity <= 0:
                                turn_log.append("\033[93mYou have run out of bullets!\033[0m")
                                player["inventory"].remove(bullets)
                        else:
                            turn_log.append("\033[91mNo bullets left! You cannot fire your gun.\033[0m")
                            dmg = 0
                    else:
                        dmg = random.randint(*getattr(weapon, "attack_range", (1, 4)))
                else:
                    dmg = random.randint(*player.get("attack", (1, 3)))
                    weapon_name = "your fists"

                target.hp = max(0, target.hp - dmg)
                acted = True
                turn_log.append(f"\033[92mYou strike {target.name} with {weapon_name} for {dmg} damage!\033[0m")

                # Optional: reward slaying with buying time
                if doom_clock and target.hp == 0:
                    doom_clock.add_time(1, turn_log, reason="Slain foe disrupts the ritual.")
            else:
                turn_log.append("\033[93mYou hesitate and do nothing!\033[0m")

        # ========================================
        # PLAYER TURN: DEFEND
        # ========================================
        elif choice == "2":
            defending = True
            acted = True
            turn_log.append("\033[94mYou brace yourself for the next attack...\033[0m")

        # ========================================
        # PLAYER TURN: MANIFEST
        # ========================================
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
                        # Using manifestations can hasten doom if you want:
                        if doom_clock:
                            doom_clock.countdown(1, player, enemies, turn_log, reason="Manifestation strains reality.")
                else:
                    turn_log.append("\033[93mYou hesitate and do nothing!\033[0m")

        # ========================================
        # PLAYER TURN: INVENTORY
        # ========================================
        elif choice == "4":
            inv = player.get("inventory", [])
            if not inv:
                turn_log.append("\033[93mYour inventory is empty!\033[0m")
            else:
                weapons = [it for it in inv if isinstance(it, Weapon)]
                consumables = [it for it in inv if not isinstance(it, Weapon)]
                total_items = []
                index = 1

                print("\nInventory:\nWeapons:")
                if weapons:
                    for w in weapons:
                        equipped = ' (equipped)' if player.get("Weapon") is w else ''
                        print(f"{index}. {getattr(w, 'name', 'Weapon')}{equipped} - {getattr(w, 'description', '')}")
                        total_items.append(w)
                        index += 1
                else:
                    print("  (none)")

                print("\nConsumables:")
                if consumables:
                    for c in consumables:
                        qty = getattr(c, "quantity", None)
                        qty_str = f" x{qty}" if qty is not None else ""
                        print(f"{index}. {getattr(c, 'name', 'Item')}{qty_str} - {getattr(c, 'description', '')}")
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
                        turn_log.append(f"\033[92mYou equipped {getattr(selected, 'name', 'Weapon')}\033[0m")
                    else:
                        # Expect consumables to implement .use(player) -> str
                        result = selected.use(player)
                        if result:
                            acted = True
                            turn_log.append(result)
                        if hasattr(selected, "quantity") and selected.quantity <= 0:
                            turn_log.append(f"\033[91m{getattr(selected, 'name', 'Item')} is depleted and removed!\033[0m")
                            inv.remove(selected)
                else:
                    turn_log.append("\033[93mInvalid choice, doing nothing...\033[0m")

        else:
            turn_log.append("\033[93mYou fumble and lose precious moments!\033[0m")

        # ========================================
        # ENEMY TURNS
        # ========================================
        special_happened = False
        for enemy in enemies:
            if enemy.hp <= 0:
                continue

            turn_log.append(f"\033[91m{enemy.name} prepares to act!\033[0m")
            if getattr(enemy, "special_attack", None) and random.random() < 0.3:
                special_happened = True
                # Healer style special?
                if "heal" in getattr(enemy, "description", "").lower():
                    allies = [e for e in enemies if e.hp > 0]
                    if allies:
                        target = min(allies, key=lambda x: x.hp)
                        enemy.special_attack(enemy, target)
                        turn_log.append(f"{enemy.name} uses a special ability on {target.name}")
                else:
                    enemy.special_attack(enemy, player)
                    turn_log.append(f"{enemy.name} uses a special ability on you!")
            else:
                dmg = random.randint(*getattr(enemy, "attack", (1, 3)))
                if defending:
                    dmg //= 2
                player["hp"] = max(0, player["hp"] - dmg)
                turn_log.append(f"\033[91m{enemy.name} strikes you for {dmg} damage!\033[0m")

        defending = False

        # ========================================
        # DOOM PROGRESSION (countdown each round)
        # ========================================
        if doom_clock:
            doom_clock.countdown(1, player, enemies, turn_log, reason="Time passes.")
            if not acted:
                doom_clock.countdown(1, player, enemies, turn_log, reason="Hesitation feeds the ritual.")
            if special_happened:
                doom_clock.countdown(1, player, enemies, turn_log, reason="Eldritch power surges.")

            if doom_clock.resolved:
                print("\n\033[91mThe Doom Clock reaches zero. The ritual completes...\033[0m")
                return False

        # ========================================
        # DISPLAY TURN LOG
        # ========================================
        print("\n\033[95m" + "=" * 50 + "\033[0m")
        for entry in turn_log:
            print(entry)
        print("\033[95m" + "=" * 50 + "\033[0m")

        # ========================================
        # CHECK WIN / LOSS
        # ========================================
        if all(e.hp <= 0 for e in enemies):
            print("\n\033[92mAll enemies have been defeated! Victory is yours!\033[0m")
            return True

        if player["hp"] <= 0:
            break

        turn_counter += 1

    if player["hp"] <= 0:
        print("\n\033[91mYour body collapses... The cult claims another victim.\033[0m")
        return False
