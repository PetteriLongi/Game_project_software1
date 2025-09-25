import random

from . import enemies
from .items import weapon_library, consumable_library, Weapon, Item, Consumable


# ==========================================
# PLAYER / ENEMY STATUS BARS
# ==========================================

def draw_bar(label, current, maximum, bar_length=20, color="default", name_width=12):
    """
    Draw a colored progress bar for HP or Sanity.

    Args:
        label: Name of the bar (e.g., "Your HP")
        current: Current value
        maximum: Maximum value
        bar_length: Number of characters for the bar
        color: 'hp', 'sanity', or default
        name_width: Width reserved for label

    Returns:
        A string representing the colored bar.
    """
    ratio = current / maximum if maximum > 0 else 0
    filled = int(ratio * bar_length)
    empty = bar_length - filled

    if color == 'hp':
        col = '\033[92m' if ratio > 0.6 else '\033[93m' if ratio > 0.3 else '\033[91m'
    elif color == 'sanity':
        col = '\033[94m'
    else:
        col = '\033[0m'

    reset = '\033[0m'
    bar = f'{col}{"#" * filled}{"-" * empty}{reset}'
    return f'{label:<{name_width}}: [{bar}] {current}/{maximum}'



# ==========================================
# MAIN COMBAT LOOP
# ==========================================

def combat(player, enemies):
    """
    Handles turn-based combat between the player and a list of enemies.

    Features:
        - Player actions: Attack, Defend, Manifest, Inventory
        - Enemy actions and special attacks
        - Turn log display
        - HP/Sanity tracking
    """
    defending = False   # Flag to reduce damage from enemy attacks
    max_name_length = max(len(e.name) for e in enemies)
    turn_counter = 1

    print(f"\n\033[95m--- COMBAT: {', '.join([e.name for e in enemies])} APPEARS! ---\033[0m")

    while player["hp"] > 0 and any(e.hp > 0 for e in enemies):
        turn_log = []  # Collect all events/messages for this turn

        # --- Turn Header ---
        print(f"\n\033[96m--- Turn {turn_counter} ---\033[0m")

        # --- Display status bars for player and enemies ---
        enemy_bars = []
        for enemy in enemies:
            if enemy.hp > 0:
                enemy_bars.append(draw_bar(enemy.name, enemy.hp, enemy.max_hp, color='hp', name_width=max_name_length))
            else:
                enemy_bars.append(f'{enemy.name}: [\033[91mDEFEATED\033[0m]')

        player_lines = 2  # Number of lines for player bars (HP + Sanity)
        total_lines = max(len(enemy_bars), player_lines)

        for i in range(total_lines):
            left = draw_bar("Your HP", player["hp"], player["max_hp"], color="hp") if i == 0 else \
                   draw_bar("Sanity ", player["sanity"], player["max_sanity"], color="sanity") if i == 1 else \
                   " " * 42
            right = enemy_bars[i] if i < len(enemy_bars) else ""
            print(f"{left:<40} || {right}")

        # --- Action menu ---
        print("\nChoose your action:")
        print("1. Attack (physical strike)")
        print("2. Defend (reduce next damage)")
        print("3. Manifest (use a special skill)")
        print("4. Inventory")
        choice = input("> ")

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
            pick = input("> ")

            if pick.isdigit() and 1 <= int(pick) <= len(living):
                target = living[int(pick) - 1]
                weapon = player.get("Weapon")

                # Handle ranged vs melee weapons
                if weapon:
                    weapon_name = weapon.name
                    if getattr(weapon, "weapon_type", "melee") == "gun":
                        bullets = next((item for item in player["inventory"]
                                        if isinstance(item, Consumable) and item.name.lower() == "bullets"), None)
                        if bullets and bullets.quantity > 0:
                            dmg = random.randint(*weapon.attack_range)
                            bullets.quantity -= 1
                            turn_log.append(f"\033[92mYou fire {weapon.name}! ({bullets.quantity} bullets left)\033[0m")
                            if bullets.quantity <= 0:
                                turn_log.append("\033[93mYou have run out of bullets!\033[0m")
                                player["inventory"].remove(bullets)
                        else:
                            turn_log.append("\033[91mYou have no bullets left! You cannot fire your gun.\033[0m")
                            dmg = 0
                    else:
                        dmg = random.randint(*weapon.attack_range)
                else:
                    dmg = random.randint(*player["attack"])
                    weapon_name = "your fists"

                target.hp -= dmg
                turn_log.append(f"\033[92mYou strike {target.name} with {weapon_name} for {dmg} damage!\033[0m")
            else:
                turn_log.append("\033[93mYou hesitate and do nothing!\033[0m")



        # ========================================
        # PLAYER TURN: DEFEND
        # ========================================

        elif choice == "2":
            defending = True
            turn_log.append("\033[94mYou brace yourself for the next attack...\033[0m")



        # ========================================
        # PLAYER TURN: MANIFEST
        # ========================================

        elif choice == "3":
            if not player["manifestations"]:
                turn_log.append("\033[93mYou have no manifestations unlocked yet!\033[0m")
            else:
                print("\nChoose a manifestation:")
                for i, m in enumerate(player["manifestations"], 1):
                    print(f"{i}. {m.name} (Cost: {m.sanity_cost}) - {m.description}")
                pick = input("> ")
                if pick.isdigit() and 1 <= int(pick) <= len(player["manifestations"]):
                    chosen = player["manifestations"][int(pick) - 1]
                    living = [e for e in enemies if e.hp > 0]
                    if not living:
                        break
                    print("\nChoose a target:")
                    for i, e in enumerate(living, 1):
                        print(f"{i}. {e.name} ({e.hp}/{e.max_hp} HP)")
                    target_pick = input("> ")
                    if target_pick.isdigit() and 1 <= int(target_pick) <= len(living):
                        target = living[int(target_pick) - 1]
                        result = chosen.use_skill(player, target)
                        turn_log.append(result)
                else:
                    turn_log.append("\033[93mYou hesitate and do nothing!\033[0m")



        # ========================================
        # PLAYER TURN: INVENTORY
        # ========================================

        elif choice == "4":
            if not player["inventory"]:
                turn_log.append("\033[93mYour inventory is empty!\033[0m")
            else:
                weapons = [item for item in player["inventory"] if isinstance(item, Weapon)]
                consumables = [item for item in player["inventory"] if not isinstance(item, Weapon)]
                total_items = []
                index = 1

                # Display weapons
                print("\nInventory:\nWeapons:")
                if weapons:
                    for w in weapons:
                        equipped = ' (equipped)' if player.get("Weapon") is w else ''
                        print(f"{index}. {w.name}{equipped} - {w.description}")
                        total_items.append(w)
                        index += 1
                else:
                    print("\nNo weapons available!")

                # Display consumables
                print("\nConsumables:")
                if consumables:
                    for c in consumables:
                        qty = getattr(c, "quantity", None)
                        qty_str = f" x{qty}" if qty is not None else ""
                        print(f"{index}. {c.name}{qty_str} - {c.description}")
                        total_items.append(c)
                        index += 1
                else:
                    print("\nNo consumables available!")

                print("0. Back to action menu")
                pick = input("\nChoose an item to equip/use (or 0 to back out):\n> ").strip()

                if pick == "0":
                    turn_log.append("\033[94mYou exit the inventory.\033[0m")
                    break

                if pick.isdigit():
                    pick = int(pick)
                    if 1 <= pick <= len(total_items):
                        selected = total_items[pick - 1]
                        if isinstance(selected, Weapon):
                            player["Weapon"] = selected
                            turn_log.append(f"\033[92mYou equipped {selected.name}\033[0m")
                        else:
                            result = selected.use(player)
                            if result:
                                turn_log.append(result)
                            if hasattr(selected, "quantity") and selected.quantity <= 0:
                                turn_log.append(f"\033[91m{selected.name} is depleted and removed from your inventory!\033[0m")
                                player["inventory"].remove(selected)
                    else:
                        turn_log.append("\033[93mInvalid choice, doing nothing...\033[0m")
                else:
                    turn_log.append("\033[93mInvalid input, doing nothing...\033[0m")



        # ========================================
        # ENEMY TURNS
        # ========================================

        for enemy in enemies:
            if enemy.hp <= 0:
                continue

            turn_log.append(f"\033[91m{enemy.name} prepares to act!\033[0m")
            # 30% chance for special attack
            if enemy.special_attack and random.random() < 0.3:
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
                    dmg //= 2   # Damage reduction when defending
                player["hp"] -= dmg
                turn_log.append(f"\033[91m{enemy.name} strikes you for {dmg} damage!\033[0m")

        defending = False


        """WRAPPING UP THE COMBAT STARTS HERE"""

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

        turn_counter += 1

    # Player has been defeated
    if player["hp"] <= 0:
        print("\n\033[91mYour body collapses... The cult claims another victim.\033[0m")
        return False