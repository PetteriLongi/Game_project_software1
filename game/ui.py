"""
ui.py - Rich-powered terminal UI helpers for the game.

Requires: rich
    pip install rich

Provides helpers to render nicer inventory and headers.
"""

# ==========================================
# IMPORTS
# ==========================================

# Non optional imports
import random
from .music import play_sfx
import pygame
import time
# Detect Rich availability safely here
try:
    from rich.console import Console
    from rich.table import Table
    from rich.columns import Columns
    from rich.panel import Panel
    from rich.text import Text
    from rich.align import Align
    from rich import box
    from rich.console import Console
    console = Console(force_terminal=True)
    
    RICH_AVAILABLE = True
except Exception:
    # Rich not available. Functions that require Rich should only be called when
    # RICH_AVAILABLE is True (checked by the caller, e.g., combat.py). ASCII fallback
    # functions in this module do not depend on Rich.
    Console = None  # type: ignore
    Table = None    # type: ignore
    Panel = None    # type: ignore
    Text = None     # type: ignore
    box = None      # type: ignore
    console = None
    RICH_AVAILABLE = False

def level_up_display(player):
    """Level up the player and render a Rich panel (or ASCII fallback) showing gains."""
    # Snapshot pre-level stats to compute deltas
    prev_level = getattr(player, "level", 1)
    prev_hp_max = getattr(player, "max_hp", 0)
    prev_sanity_max = getattr(player, "max_sanity", 0)
    prev_attack = getattr(player, "base_attack", (0, 0))

    # Perform the actual level-up
    player.level_up()

    # Compute gains
    hp_gain = player.max_hp - prev_hp_max
    sanity_gain = player.max_sanity - prev_sanity_max
    # Show the min-end increase; both ends increase equally in current logic
    attack_gain = player.base_attack[0] - prev_attack[0]

    flavor_text = [
        "You hear whispers in a language you don’t know… yet.",
        "A tingling sensation crawls up your spine.",
        "The veil between worlds thins — and you step through.",
        "Something unseen has taken interest in your growth.",
        "The silence now feels… expectant.",  
    ]
    flavor = random.choice(flavor_text)

    if RICH_AVAILABLE and console is not None:

        level_text = Text.assemble(
            Text("🔺 ASCENSION COMPLETE 🔺\n", style="bold magenta"),
            Text(f"\nYou have reached Level {player.level}!\n", style="bold green"),
            Text(f"\n+{hp_gain} Maximum HP", style="green"),
            Text(f"\n+{sanity_gain} Maximum Sanity", style="cyan"),
            Text(f"\n+{attack_gain} Attack", style="red"),
            Text(f"\n\n{flavor}", style="italic dim"),
        )
        panel_level_up = Panel.fit(
            level_text,
            title="Level Up!",
            title_align="left",
            box=box.DOUBLE,
            border_style="magenta",
            padding=(1, 4),
        )
        console.print(panel_level_up)
        pygame.mixer.music.pause()
        play_sfx("level_up")
        time.sleep(1)
        pygame.mixer.music.unpause()
        console.print(Text("Press Enter to continue...", style="bold magenta"))
        console.input("")
    else:
        # ASCII fallback
        print("\n=== LEVEL UP ===")
        print(f"Now level {player.level}")
        print(f"+{hp_gain} Max HP, +{sanity_gain} Max Sanity, +{attack_gain} Attack")
        input("Press Enter to continue...")
        
# ==========================================
# INVENTORY RENDERING
# ==========================================
def render_inventory(player, weapons_list, consumables_list):
    """Render the player's inventory.

    If Rich is available, use the Rich UI; otherwise, fall back to ASCII output.
    The ordering of items is: weapons first, then consumables.
    Indices are assigned starting from 1, matching selection order in combat_actions.handle_inventory().
    """
    if RICH_AVAILABLE:
        # Build ammo reserves line
        if getattr(player, "ammo", None):
            ammo_str = "\n".join(f"{k}: {v}" for k, v in player.ammo.items())
        else:
            ammo_str = "(none)"

        # Unified Table
        items_table = Table(
            box=box.SIMPLE_HEAVY,
            expand=True,
            show_edge=True,
            header_style="bold magenta",
            border_style="white",
        )
        items_table.add_column("#", justify="right", style="cyan", no_wrap=True)
        items_table.add_column("Name", style="bold white")
        items_table.add_column("Mag", justify="right", style="yellow", no_wrap=True)
        items_table.add_column("Qty", justify="right", style="yellow", no_wrap=True)
        items_table.add_column("Description", style="dim")

        index = 1

        # Weapons
        items_table.add_row("[bold magenta]Weapons[/]", "", "", "",  style="bold magenta")
        for w in weapons_list:
            equipped = player.weapon is w
            name_text = Text(w.name, style="bold white")
            if equipped:
                name_text.append(" (equipped)", style="green")

            mag = f"[{w.current_mag}/{w.mag_size}]" if getattr(w, "weapon_type", "melee") == "gun" else "-"
            qty = "-"
            items_table.add_row(str(index), name_text, mag, qty, w.description)
            index += 1
        
        items_table.add_row("", "", "", "", "")

        # Consumables
        items_table.add_row("[bold magenta]Consumables[/]", "", "", "", style="bold magenta")
        for c in consumables_list:
            mag = "-"
            qty = getattr(c, "quantity", None)
            qty_str = str(qty) if isinstance(qty, int) else "-"
            items_table.add_row(str(index), c.name, mag, qty_str, c.description)
            index += 1

        # Panel with header and ammo reserves
        panel_inventory = Panel.fit(
            Text.assemble(Text("Inventory", style="bold magenta"), "\n", Text(f"Ammo reserves\n{ammo_str}", style="cyan")),
            box=box.SQUARE,
            border_style="magenta"
        )

        # Panel levels
        panel_level = Panel.fit(
            Text.assemble(Text("Level", style="bold magenta"), "\n", Text(f"{player.level}", style="cyan")),
            box=box.SQUARE,
            border_style="magenta"
        )

        console.print(Columns([panel_inventory, panel_level], equal=True))
        console.print()  # spacer

        # Print the unified table 
        console.print(items_table)
        console.print(Text("0. Back to action menu", style="bold cyan"))
        console.print(Text("Type 'u' to unequip current weapon", style="dim cyan"))
    else:
        _render_inventory_ascii(player, weapons_list, consumables_list)


# ==========================================
# INVENTORY RENDERING (ASCII FALLBACK)
# ==========================================
def _render_inventory_ascii(player, weapons_list, consumables_list):
    """Plain-text inventory rendering used when Rich is unavailable.

    Matches ordering and numbering expected by combat_actions.handle_inventory().
    """
    print("\n=== Inventory ===")

    # Ammo reserves
    print("Ammo reserves:")
    if getattr(player, "ammo", None):
        for k, v in player.ammo.items():
            print(f"  - {k}: {v}")
    else:
        print("  (none)")

    index = 1
    # Weapons section
    print("\nWeapons:")
    if weapons_list:
        for w in weapons_list:
            equipped = (player.weapon is w)
            badge = " (equipped)" if equipped else ""
            if getattr(w, "weapon_type", "melee") == "gun":
                mag = f" [{w.current_mag}/{w.mag_size}]"
            else:
                mag = ""
            print(f"  {index}. {w.name}{badge}{mag} - {w.description}")
            index += 1
    else:
        print("  (none)")

    # Consumables section
    print("\nConsumables:")
    if consumables_list:
        for c in consumables_list:
            qty = getattr(c, "quantity", None)
            qty_str = f" x{qty}" if isinstance(qty, int) else ""
            print(f"  {index}. {getattr(c, 'name', str(c))}{qty_str} - {getattr(c, 'description', '')}")
            index += 1
    else:
        print("  (none)")

    print("\n0. Back to action menu")
    print("Type 'u' to unequip current weapon")
    print("Choose an item to equip/use (0 to back, u to unequip):")


# ========================================
# COLOUR HANDLING
# ========================================

COLOURS = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "purple": "\033[95m",
    "magenta": "\033[95m",
    "cyan": "\033[96m",
    "white": "\033[97m",
    "reset": "\033[0m"
}

def colouring(text, colour):
    return f"{COLOURS[colour]}{text}{COLOURS['reset']}"

def ui_print(text: str, colour: str | None = None):
    if RICH_AVAILABLE and console is not None:
        if colour:
            console.print(Text(str(text), style=colour))
        else:
            console.print(str(text))
    else:
        if colour:
            print(colouring(str(text), colour))
        else:
            print(str(text))

# ==========================================
# COMBAT STATUS BARS (RICH)
# ==========================================
def exp_hint(ratio):
    if ratio > 0.90:
        return "The veil is threadbare. Revelation is imminent"
    elif ratio > 0.75:
        return "Eyes unseen turn in your direction"
    elif ratio > 0.5:
        return "The veil stirs with whispered secrets"
    elif ratio > 0.25:
        return "A faint ripple disturbs the void"
    else:
        return "The void is patient"


def _rich_bar_text(current, maximum, bar_length=20, kind="hp"):
    """Build a Rich Text object representing a colored progress bar.

    kind: 'hp' or 'sanity' to pick color scheme.
    """
    ratio = current / maximum if maximum > 0 else 0
    filled = int(ratio * bar_length)
    empty = bar_length - filled

    text = Text()
    #optional way to do HP and Sanity bars also with cryptic changing symbols, just uncomment these and change if kind to elif kind
    #if kind == "hp":
        #blood_glyphs = "⛆☈❦"
        #flesh_fill = "".join(random.choices(blood_glyphs, k=filled))
        #flesh_empty = "".join("░" for _ in range(empty))
        #text.append(flesh_fill, style="bold red")
        #text.append(flesh_empty, style="dim")

    #elif kind == "sanity":
        #sanity_glyphs = "⌇⌠⌡◈◍⋇"
        #sanity_fill = "".join(random.choices(sanity_glyphs, k=filled))
        #sanity_empty = "".join("░" for _ in range(empty))
        #text.append(sanity_fill, style="bold magenta")
        #text.append(sanity_empty, style="dim")

    if kind == "xp":
        glyphs = "⟁⌖Ϟᛝ☍𒐫"

        obscured = "░▒▓"
        filled_bar = "".join(random.choices(glyphs, k=filled))
        empty_bar = "".join(random.choices(obscured, k=empty))

        text = Text()
        text.append(filled_bar, style="bold purple")
        text.append(empty_bar, style="dim")

    else:
    # Color scheme
        if kind == "hp":
            if ratio > 0.6:
                style = "bold green"
            elif ratio > 0.3:
                style = "bold yellow"
            else:
                style = "bold red"
        elif kind == "sanity":
            # Eldritch vibe for Sanity
            style = "bold magenta"
        elif kind == "xp":
            style = "bold purple"
        else:
            style = "white"
        text.append("█" * filled, style=style)
        text.append("░" * empty, style="dim")
    return text


def draw_status_bars_rich(player, enemies_list):
    """Render player and enemy status bars using Rich with an eldritch theme.

    Layout: two columns — left (player HP/Sanity), right (enemies).
    """
    # Build a two-column grid
    table = Table.grid(expand=True)
    table.add_column(ratio=1)
    table.add_column(ratio=1)
    table.add_column(ratio=1)

    # Left column: player bars stacked
    left = Table.grid(padding=(0, 1))

    hp_bar = _rich_bar_text(player.hp, player.max_hp, kind="hp")
    left.add_row(
        Text("Your HP:"),
        Text.assemble(
            Text("⟨ ", style="dim red"),
            hp_bar,
            Text(" ⟩ ", style="dim red"),
            Text(f"{player.hp}/{player.max_hp}", style="bold")
        )
    )
    # Thin eldritch separator between HP and Sanity
    left.add_row(Text(""), Text(" ", style="dim magenta"))

    san_bar = _rich_bar_text(player.sanity, player.max_sanity, kind="sanity")
    left.add_row(
        Text("Sanity :"),
        Text.assemble(
            Text("⟨ ", style="dim red"),
            san_bar,
            Text(" ⟩ ", style="dim red"),
            Text(f"{player.sanity}/{player.max_sanity}", style="bold")
        )
    )

    left.add_row(Text(""), Text(" ", style="dim magenta"))

    xp_bar = _rich_bar_text(player.exp, player.exp_to_next, kind="xp")
    left.add_row(
        Text("Experience:"),
        Text.assemble(
            Text("⟨ ", style="dim red"),
            xp_bar,
            Text(" ⟩ ", style="dim red"),
        )
    )


    # Right column: one row per enemy
    right = Table.grid(padding=(0, 1))
    for idx, enemy in enumerate(enemies_list):
        if enemy.hp > 0:
            e_bar = _rich_bar_text(enemy.hp, enemy.max_hp, kind="hp")
            right.add_row(
                Text(f"{enemy.name}:") ,
                Text.assemble(
                    Text("⟨ ", style="dim red"),
                    e_bar,
                    Text(" ⟩ ", style="dim red"),
                    Text(f"{enemy.hp}/{enemy.max_hp}", style="bold")
                )
            )
        else:
            right.add_row(Text(f"{enemy.name}:") , Text("[ DEFEATED ]", style="bold red"))
        # Thin separator between enemies, not after the last one
        if idx < len(enemies_list) - 1:
            right.add_row(Text(""), Text(" ", style="dim magenta"))

    table.add_row(left, right)
    console.print(table)

# ==========================================
# COMBAT STATUS BARS (ASCII FALLBACK)
# ==========================================
def draw_status_bars_ascii(player, enemies_list):
    """Print classic ASCII status bars for player and enemies.

    Mirrors the original layout from combat.py, used when Rich is unavailable.
    """
    # Determine max name width for alignment on the right side
    max_name_length = max(len(e.name) for e in enemies_list) if enemies_list else 12

    def draw_bar(label, current, maximum, bar_length=20, color="default", name_width=12):
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
        bar = f"{col}{'#' * filled}{'-' * empty}{reset}"
        return f"{label:<{name_width}}: [{bar}] {current}/{maximum}"

    # Build enemy bars
    enemy_bars = []
    for enemy in enemies_list:
        if enemy.hp > 0:
            enemy_bars.append(draw_bar(enemy.name, enemy.hp, enemy.max_hp, color='hp', name_width=max_name_length))
        else:
            enemy_bars.append(f"{enemy.name}: [\033[91mDEFEATED\033[0m]")

    player_lines = 2  # HP + Sanity
    total_lines = max(len(enemy_bars), player_lines)

    for i in range(total_lines):
        left = (
            draw_bar("Your HP", player.hp, player.max_hp, color="hp") if i == 0 else
            draw_bar("Sanity ", player.sanity, player.max_sanity, color="sanity") if i == 1 else
            " " * 42
        )
        right = enemy_bars[i] if i < len(enemy_bars) else ""
        print(f"{left:<40} || {right}")
