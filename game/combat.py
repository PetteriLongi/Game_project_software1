"""
combat.py - Turn-based combat loop and menus

Usage:
    from game.combat import combat

Quick start:
    from game.player import Player
    from game.enemies import create_enemy
    
    player = Player("Hero", unlocked_manifestations=[])
    enemies = [create_enemy("Cultist"), create_enemy("Apostle")]
    combat(player, enemies)

What this module does:
- Runs the round-based combat loop
- Presents the action menu each turn:
  1) Attack   2) Defend   3) Manifest   4) Inventory   5) Reload
- Resolves enemy turns and special attacks
- Tracks HP/Sanity and prints a colorized turn log

Rendering (UI):
- Status bars and inventory UI are rendered by `game/ui.py`.
  - If Rich is available, uses themed Rich UI (eldritch bars, tables).
  - Otherwise, falls back to plain-text (ASCII) output.

Inputs and data:
- Player is an instance of `game.player.Player` (not a dict).
- Enemies are instances created via `game.enemies.create_enemy(name)`.
- Weapons/Items live in `game.items`; inventory actions are available from the menu.

End conditions:
- Combat ends when all enemies are defeated (victory) or the player HP reaches 0 (defeat).
"""

import random

from .items import Weapon, Item, Consumable
from .ui import exp_hint, colouring
from .ui import draw_status_bars_ascii
from .ui import RICH_AVAILABLE, draw_status_bars_rich
from .combat_actions import select_target, resolve_attack, handle_manifestations, handle_inventory, reload_gun

# ==========================================
# MAIN COMBAT LOOP
# ==========================================
# The combat loop runs in rounds (turns). Each round, the player can choose an action.
# After certain actions (Attack/Defend/Manifest/Reload), enemies take their turns.
# Just opening the Inventory and backing out does NOT spend a turn.

def combat(player, enemies_list):
    """
    Handles turn-based combat between the player and a list of enemies.

    Features:
        - Player actions: Attack, Defend, Manifest, Inventory
        - Enemy actions and special attacks
        - Turn log display
        - HP/Sanity tracking
    """
    defending = False   # When True, the next enemy hit does half damage
    max_name_length = max(len(e.name) for e in enemies_list)
    turn_counter = 1

    print(f"\n\033[95m--- COMBAT: {', '.join([e.name for e in enemies_list])} APPEARS! ---\033[0m")

    while player.hp > 0 and any(e.hp > 0 for e in enemies_list):
        # These logs gather all messages for this round and are printed at the end
        player_log = []
        enemy_log = []
        # If False, we skip enemy actions and do not advance the round counter
        turn_consumed = False

        # --- Turn Header ---
        print(f"\n\033[96m--- Turn {turn_counter} ---\033[0m")

        # --- Display status bars for player and enemies ---
        if RICH_AVAILABLE and draw_status_bars_rich:
            draw_status_bars_rich(player, enemies_list)
        else:
            # Delegate ASCII status bar rendering to UI module
            draw_status_bars_ascii(player, enemies_list)

        # --- Action menu ---
        # Type the number and press Enter to perform an action
        print("\nChoose your action:")
        print("1. Attack (physical strike)")
        print("2. Defend (reduce next damage)")
        print("3. Manifest (use a special skill)")
        print("4. Inventory")
        print("5. Reload (for firearms)")
        choice = input("> ")

        # ========================================
        # PLAYER TURN: ATTACK
        # ========================================

        if choice == "1":
            # Physical attack against a selected enemy target
            turn_consumed = True
            target = select_target(enemies_list, player_log)
            if target:
                resolve_attack(player, target, player_log)


        # ========================================
        # PLAYER TURN: DEFEND
        # ========================================

        elif choice == "2":
            # Reduce damage from the next enemy hit in this round
            turn_consumed = True
            defending = True
            player_log.append(colouring(
                "You brace yourself for the next attack...",
                "blue"
            ))
            player_log.append("")



        # ========================================
        # PLAYER TURN: MANIFEST
        # ========================================

        elif choice == "3":  # Use a Manifestation (special ability)
            turn_consumed = handle_manifestations(player, enemies_list, player_log)


        # ========================================
        # PLAYER TURN: INVENTORY
        # ========================================

        elif choice == "4":
            turn_consumed, msgs = handle_inventory(player)
            player_log.extend(msgs)


        # ========================================
        # PLAYER TURN: RELOAD
        # ========================================

        elif choice == "5":
            # Reload the currently equipped firearm (if any)
            turn_consumed, msgs = reload_gun(player, consume_turn=True)
            player_log.extend(msgs)


        # ========================================
        # ENEMY TURNS (only if player action consumed the turn)
        # ========================================

        if turn_consumed:
            for enemy in enemies_list:
                if enemy.hp <= 0:
                    if not getattr(enemy, "exp_awarded", False):
                        player.gain_exp(enemy.exp_reward)
                        enemy.exp_awarded = True
                    continue

                enemy_log.append(colouring(f"{enemy.name} prepares to act!", "red"))
                msgs = enemy.take_turn(player, enemies_list, defending)
                match msgs:
                    case str():
                        enemy_log.append(msgs)
                    case list():
                        enemy_log.extend(msgs)
                    case _ if msgs:
                        enemy_log.append(str(msgs))
                enemy_log.append("")
                defending = False

        # ========================================
        # AMBIENT EXP HINT (WHISPER)
        # ========================================
        try:
            ratio = player.exp / max(getattr(player, "exp_to_next", 1), 1)
        except Exception:
            ratio = 0.0

        # The closer to level up, the more frequent the whisper
        # Base 12% chance + up to 20% as ratio approaches 1.0
        if random.random() < 0.15 + 0.50 * max(0.0, min(1.0, ratio)):
            player_log.append("") #spacer
            player_log.append(colouring(f"[Whisper] {exp_hint(ratio)}", "magenta"))
        

        # ========================================
        # DISPLAY TURN LOG
        # ========================================
        turn_log = player_log + [""] + enemy_log
        print(colouring("\n" + "=" * 50, "magenta"))
        for entry in turn_log:
            print(entry)
        print(colouring("=" * 50, "magenta"))


        # ========================================
        # CHECK WIN / LOSS
        # ========================================
        if turn_consumed and all(e.hp <= 0 for e in enemies_list):
            print(colouring("\nAll enemies have been defeated! Victory is yours!", "green"))
            return True

        if turn_consumed:
            turn_counter += 1

    # Player has been defeated
    if player.hp <= 0:
        print(colouring("\nYour body collapses... The cult claims another victim.", "red"))
        return False