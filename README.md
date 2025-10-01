# Game Project Software 1

Lovecraft-inspired, terminal-based, turn-based RPG written in Python.
Battle cultists and abominations using melee weapons, firearms with magazines and ammo reserves, and eldritch manifestations that consume Sanity.

## Features
- Turn-based combat with a clear, colorized combat log
- Player progression: levels, EXP, HP and Sanity scaling
- Inventory management with equip/use
- Weapons and Items system
  - Melee and firearms
  - Firearms have magazine sizes and use named ammo types
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
- rich (recommended for enhanced UI; without it, the game uses an ASCII UI for inventory and status bars)
- Run through a real terminal for best visuals (Run/Debug consoles often mangle ANSI/Rich output)

Install dependencies:
```bash
pip install pygame rich
```

py -m venv .venv
.\.venv\Scripts\Activate
python -m pip install --upgrade pip
pip install pygame rich  # 'rich' is optional but recommended

### Run the game
From the project root (real terminal recommended):
```bash
python main.py
```

## Project Structure
```
Game_project_software1/
├─ main.py                       # Entry point (demo sequence)
├─ Music/                        # Music & SFX assets (case-sensitive on some systems)
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

## Conventions
- **[imports]**
  - Non-optional imports go at the top of the file (e.g., `random`, `pygame`, `time`).
  - Optional Rich imports are wrapped in a try/except in `game/ui.py` and gated by `RICH_AVAILABLE`.
  - Use lazy imports inside functions to avoid circulars when needed (e.g., `from .ui import level_up_display` in `Player.gain_exp()`).
- **[printing]**
  - Use `ui_print(text, colour=None)` from `game/ui.py` for all user-facing messages (it routes to Rich or ASCII automatically).
  - Prefer passing simple colour names/styles (e.g., `"green"`, `"blue"`, `"bold magenta"`).
- **[SFX]**
  - Register all SFX in `game/sfx_loader.py` via `register_all_sfx()` called from `main.py`.
  - Reference SFX by keys in code using `play_sfx(key)`.
  - Entity fields:
    - `Consumable.sfx_name` (e.g., Eating/Drinking) plays on use.
    - `Weapon.sfx_attack` and `Weapon.sfx_reload` play during attack/reload resolution (not on construction).
    - `Manifestation.sfx_manifest` plays when used.
- **[inventory rules]**
  - Ammo consumables are routed to `player.ammo` by display name (must match `Weapon.ammo_type`).
  - Stacking compares by display name (e.g., `"Small coffee"`) so metadata like SFX is preserved.
- **[combat loop]**
  - Enemy cleanup (removal of defeated) happens at the start of each new player turn to keep `[ DEFEATED ]` visible for the remainder of the round.
- **[naming]**
  - Use `snake_case` for variables/functions, `PascalCase` for classes.
  - Prefer consistent lower_snake_case for SFX keys.
- **[constants/config]**
  - Keep tuning knobs (level-up gains, EXP scaling, volumes) near their usage or extract to module-level constants for clarity.
- **[assets]**
  - Paths under `Music/` are case-sensitive on some systems; keep filenames consistent with loader entries.
  - Ensure you have rights to any assets you add.

## Core Systems
### Player
- Class: `game/player.py` -> `Player`
- Stats: HP, Sanity, Base Attack, Leveling / EXP
- Inventory: list of `Item` objects
- Ammo pool: dictionary on player: `player.ammo = {".36 Caliber": 12, "5.56 Caliber": 30, ...}`
 - Level-up flow:
   - EXP is granted via `Player.gain_exp(amount)`.
   - While EXP ≥ threshold, `level_up_display(player)` (in `game/ui.py`) is called to level and show a Rich panel (ASCII fallback) with gains and an SFX. Music pauses briefly during the panel.

### Items & Weapons
- File: `game/items.py`
- Classes: `Item`, `Weapon`, `Consumable`
- Firearms include:
  - `ammo_type` (e.g., `.36 Caliber`, `5.56 Caliber`)
  - `mag_size` (e.g., 6, 30)
  - `current_mag` (auto-filled when acquired)
- Libraries:
  - `weapon_library` (e.g., Basic dagger, Old revolver, AR-15)
  - `consumable_library` (e.g., Karelian pie, Rye Bread, Small coffee, Large coffee, `.36 Caliber`, `5.56x45mm NATO`, `4.6x30mm`)
- Inventory helpers:
  - `add_weapon_to_inventory(player, name)` (clones a fresh weapon)
  - `add_item_to_inventory(player, name, amount=1)` (routes ammo items into `player.ammo`)
 - SFX fields:
   - Consumables: `sfx_name` (e.g., Eating for healing, Drinking for sanity).
   - Weapons: `sfx_attack`, `sfx_reload`.
   - These are defined in the libraries and cloned onto instances; sounds are triggered at use-time (not at construction).
 - Inventory behavior:
   - Ammo-type consumables are routed to `player.ammo` pools (keyed by the consumable's display name to match `Weapon.ammo_type`).
   - Stacking compares by display name (e.g., `"Small coffee"`), ensuring SFX metadata is preserved.

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
    - Attack SFX are played during the attack resolution using `weapon.sfx_attack`.
    - Reload SFX are played in `reload_gun()` using `weapon.sfx_reload` when a reload occurs.
    - Cleanup timing: defeated enemies are removed at the start of each new player turn so the `[ DEFEATED ]` state is visible for the rest of the round they died.

### Manifestations
- File: `game/manifestations.py`
- Examples: Fear, Rage, Despair (with different costs and effects)
- SFX field: `sfx_manifest` can be set per manifestation; played when used.
### Enemies
- File: `game/enemies.py`
- Each enemy has a difficulty, HP, attack range, optional special attack, and EXP reward.
- Cleanup timing: Defeated enemies are removed at the start of each new player turn. This keeps the "[ DEFEATED ]" state visible for clarity during the remainder of the round in which they died.

### Music
- File: `game/music.py`
- Simple wrappers: `play_music`, `stop_music`, `set_volume`, `init_audio`
- Mixer is initialized lazily on first use (or explicitly via `init_audio()`), so import never crashes on machines without audio.
- Included assets (paths are case-sensitive on some systems):
  - `Music/ambience/Piano_suspence.mp3`
  - `Music/combat/Anxiety.mp3`
  - `Music/combat/Behind_you.mp3`
  - `Music/SFX/*.wav` (slash, shots, reloads, typing)

### SFX Registration
- File: `game/sfx_loader.py`
- Call `register_all_sfx()` from `main.py` to load all SFX keys/paths/volumes at startup.
- Gameplay code triggers sounds via `play_sfx(key)`.

### Terminal UI (Rich + ASCII fallback)
- File: `game/ui.py`
- Inventory and status bars use Rich (tables, colors, “eldritch” themed bars) when available.
- If `rich` is not installed, both inventory and status bars fall back to ASCII.
- Includes simple console colouring helpers: `COLOURS` and `colouring(text, colour)`.
 - Standardized printing: use `ui_print(text, colour=None)` everywhere for consistent Rich/ASCII output.

## Demo Flow (`main.py`)
- Creates a player with the `Fear`, `Hope`, `Rage`, and `Resentment` manifestations
- Gives starter items/weapons (dagger, sword, AR-15, MP7, potions, ammo)
- Runs two combat encounters
- Prints a hint at startup indicating whether Rich UI is enabled or ASCII fallback is in use.

## You can modify the sequence in `main.py` to prototype new encounters or items. Example to add ammo:
- add_item_to_inventory(player, ".36 Caliber", 12)          # Revolver ammo
- add_item_to_inventory(player, "5.56x45mm NATO", 30)       # AR-15 ammo

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
- A store you can visit to buy items and weapons
- standardize the UI to use ui_print() 
- Graceful Defeat handling  (now it just brute forces a sys.exit)

## Requirements File
If you prefer a requirements.txt:
```
pygame>=2.0.0
rich>=13.0.0
```

## Credits
- Audio assets under `Music/` are not created by us. 
- Credits for the music goes to: Pixabay and fesliyanstudios

## License
This project is for educational purposes. Add a LICENSE file if you plan to distribute.

---
