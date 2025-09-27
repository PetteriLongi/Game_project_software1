# Game Project Software 1

Lovecraft-inspired, terminal-based, turn-based RPG written in Python.
Battle cultists and abominations using melee weapons, firearms with magazines and ammo reserves, and eldritch manifestations that consume Sanity.

## Features
- Turn-based combat with a clear, colorized combat log
- Player progression: levels, EXP, HP and Sanity scaling
- Weapons and Items system
  - Melee and firearms
  - Firearms have magazine sizes and use named ammo types
  - Inventory management with equip/use
  - Spawn guns with full, empty, or partial magazines
- Manifestations (skills) that consume Sanity
- Enemy roster with special attacks and EXP rewards
- Background music via Pygame (lazy-initialized, safe on machines without audio)
- Rich-based UI for inventory and status bars with ASCII fallback
  - Unified Inventory table (aligned columns: `# | Name | Mag | Qty | Description`)
  - HP/Sanity/EXP bars; ambient cryptic EXP “whispers” appear in the turn log as you near level-up

## Quick Start
### Requirements
- Python 3.10+
- pygame
- Optional: rich (for enhanced terminal UI)
- RUN THROUGH TERMINAL AND INPUT:python main.py
- running through Run ruins the visual experience 
  due to the limitations in the way Run/Debug console handles ANSI and Rich

Install dependencies:
```bash
pip install pygame
# Optional UI enhancements
pip install rich
```

py -m venv .venv
.\.venv\Scripts\Activate
python -m pip install --upgrade pip
pip install pygame rich  # 'rich' optional

### Run the game
From the project root:
```bash
python main.py
```

## Project Structure
```
Game_project_software1/
├─ main.py                       # Entry point (demo sequence)
├─ music/                        # Music assets (see Credits)
└─ game/
   ├─ __init__.py                # Package API (re-exports: combat, Player, items, enemies, manifestations, music, UI helpers)
   ├─ combat.py                  # Turn-based combat loop and menus (orchestrates actions)
   ├─ combat_actions.py          # Combat helper functions: attack/manifest/inventory, reload_gun, target selection
   ├─ enemies.py                 # Enemy class, specials, library
   ├─ items.py                   # Item/Weapon/Consumable classes, libraries, inventory helpers
   ├─ manifestations.py          # Manifestation class and library
   ├─ music.py                   # Music helpers (play/stop/set volume, lazy init)
   ├─ player.py                  # Player class and leveling
   ├─ ui.py                      # UI helpers: Rich inventory/status bars + ASCII fallbacks
   └─ writing_effects.py         # Typewriter/glitch/etc. text helpers
```

## Core Systems
### Player
- Class: `game/player.py` -> `Player`
- Stats: HP, Sanity, Base Attack, Leveling / EXP
- Inventory: list of `Item` objects
- Ammo pool: dictionary on player: `player.ammo = {".36 Caliber": 12, "5.56 Caliber": 30, ...}`

### Items & Weapons
- File: `game/items.py`
- Classes: `Item`, `Weapon`, `Consumable`
- Firearms include:
  - `ammo_type` (e.g., `.36 Caliber`, `5.56 Caliber`)
  - `mag_size` (e.g., 6, 30)
  - `current_mag` (auto-filled when acquired)
- Libraries:
  - `weapon_library` (e.g., Basic dagger, Old revolver, AR-15)
  - `consumable_library` (e.g., Health Potion, Sanity Potion, `.36 Caliber`, `5.56 Caliber`)
- Inventory helpers:
  - `add_weapon_to_inventory(player, name)` (clones a fresh weapon)
  - `add_item_to_inventory(player, name, amount=1)` (routes ammo items into `player.ammo`)

### Combat
- Files: `game/combat.py`, `game/combat_actions.py`
- Actions per turn:
  1. Attack
  2. Defend
  3. Manifest
  4. Inventory
  5. Reload (for firearms)
- Turn usage rules:
  - Attack/Defend/Manifest/Reload consume the player turn
  - Opening Inventory and picking `0` (Back) does NOT consume the turn
  - Using an item or equipping a weapon from Inventory DOES consume the turn (configurable)
- Firearms:
  - Firing decrements `weapon.current_mag`
  - If the mag is empty, Reload to move rounds from `player.ammo[weapon.ammo_type]` into the mag
  - Combat log shows both mag state and reserve ammo
 - Implementation notes:
   - The main loop lives in `game/combat.py`.
   - Action handlers (`resolve_attack`, `handle_inventory`, `handle_manifestations`, `reload_gun`, `select_target`) live in `game/combat_actions.py` and are imported by the loop.

### Manifestations
- File: `game/manifestations.py`
- Examples: Fear, Rage, Despair (with different costs and effects)

### Enemies
- File: `game/enemies.py`
- Each enemy has a difficulty, HP, attack range, optional special attack, and EXP reward.

### Music
- File: `game/music.py`
- Simple wrappers: `play_music`, `stop_music`, `set_volume`, `init_audio`
- Mixer is initialized lazily on first use (or explicitly via `init_audio()`), so import never crashes on machines without audio.

### Terminal UI (Rich + ASCII fallback)
- File: `game/ui.py`
- Inventory and status bars use Rich (tables, colors, “eldritch” themed bars) when available.
- If `rich` is not installed (or is disabled), the game uses a plain-text fallback for both inventory and status bars.
 - Includes simple console colouring helpers: `COLOURS` and `colouring(text, colour)`.

## Demo Flow (main.py)
- Creates a player with the `Fear` manifestation
- Gives starter items/weapons
- Runs two combat encounters

## You can modify the sequence in `main.py` to prototype new encounters or items. Example to add ammo:
- add_item_to_inventory(player, ".36 Caliber", 12)     # Revolver ammo
- add_item_to_inventory(player, "5.56 Caliber", 30)   # AR-15 ammo

## Controls & Tips
- Choose actions via number keys in combat
- In Inventory:
  - Pick an index to equip a weapon or use a consumable
  - Pick `0` to go back without using a turn
- Guns start with a full magazine when obtained
- Watch the log for reload hints and remaining reserve

Tip: For best visuals, install Rich:
```bash
pip install rich
```

## Adding Content
- Add new weapons to `weapon_library` with appropriate `ammo_type` and `mag_size`
- Add new ammo items to `consumable_library` and update `add_item_to_inventory` routing if needed
- Create new manifestations by defining a function and adding to `manifestation_library`
- Add enemies to `enemy_library` and special attacks as standalone functions

## Known Ideas / TODO
- Rest system (recover HP/Sanity between combats)
- More firearms and ammo types (e.g., shotguns, special rounds)
- Status effects (poison, bleed, fear) 
- Save/Load system
- Sanity Effects (Example: Combat log text gets scrambled when Sanity is low.)
- Randomly trigger audio “glitches” — distorted whispers, reversed sounds, sudden volume spikes.
- critical hits
- Enemies call for reinforcements mid-fight. (Maybe a specific enemy type)
- Some cultists summon eldritch horrors if not killed quickly.
- Boss fights?
- Tension meter (tracking looming horror.(tension meter full maybe a secret boss; 
  looming horror appears) The longer you go without resting, the more “strange events” happen.)

## Requirements File
If you prefer a requirements.txt:
```
pygame>=2.0.0
# Optional
rich>=13.0.0
```

## Credits
- Music: Right Behind You — Fesliyan Studios
  - File path used in demo: `music/combat/2022-10-10_-_Right_Behind_You_-_www.FesliyanStudios.com.mp3`
  - Please ensure you have the proper rights/license to distribute or use this track.

## License
This project is for educational purposes. Add a LICENSE file if you plan to distribute.
