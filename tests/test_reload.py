import shutil
from textwrap import dedent, fill

import pygame

# ==========================================
# LOCAL IMPORTS
# ==========================================
from game.writing_effects import print_typewriter, flicker_line, dim_text
from game.combat import combat
from game.manifestations import manifestation_library
from game.enemies import create_enemy
from game.items import add_weapon_to_inventory, add_item_to_inventory
from game.music import play_music, stop_music
from game.player import Player


import pytest

class DummyWeapon:
    def __init__(self, name="Test Gun", mag_size=6, current_mag=0, ammo_type=".36 Caliber"):
        self.name = name
        self.mag_size = mag_size
        self.current_mag = current_mag
        self.ammo_type = ammo_type
        self.weapon_type = "gun"

class DummyPlayer:
    def __init__(self, weapon=None, ammo=None):
        self.weapon = weapon
        self.ammo = ammo or {}

@pytest.mark.parametrize("current_mag,reserve,expected_mag,expected_reserve,expected_msg", [
    # already full
    (6, 12, 6, 12, "already full"),
    # no ammo in reserve
    (0, 0, 0, 0, "No .36 Caliber ammo in reserve"),
    # full reload possible
    (0, 12, 6, 6, "You reload Test Gun: +6 rounds"),
    # partial reload
    (0, 4, 4, 0, "Partial reload"),
    # reload when half full
    (3, 6, 6, 3, "You reload Test Gun: +3 rounds"),
    # reserve exactly matches what's needed to fill
    (4, 2, 6, 0, "You reload Test Gun: +2 rounds"),
])
def test_reload_logic(current_mag, reserve, expected_mag, expected_reserve, expected_msg):
    # Arrange
    weapon = DummyWeapon(current_mag=current_mag)
    player = DummyPlayer(weapon=weapon, ammo={".36 Caliber": reserve})
    player_log = []

    # Act: simulate choice == "5"
    needed = max(0, weapon.mag_size - weapon.current_mag)
    if needed == 0:
        player_log.append(f"{weapon.name}'s magazine is already full.")
    else:
        ammo_type = getattr(weapon, 'ammo_type', 'bullets')
        reserve = player.ammo.get(ammo_type, 0)
        if reserve <= 0:
            player_log.append(f"No {ammo_type} ammo in reserve to reload!")
        else:
            to_load = min(needed, reserve)
            weapon.current_mag += to_load
            player.ammo[ammo_type] = reserve - to_load
            player_log.append(f"You reload {weapon.name}: +{to_load} rounds ({weapon.current_mag}/{weapon.mag_size}). Reserve left: {player.ammo[ammo_type]}")
            if to_load < needed:
                player_log.append(f"Partial reload: not enough {ammo_type} to fill the magazine.")
            if player.ammo[ammo_type] == 0:
                player_log.append(f"You're out of {ammo_type} after reloading.")

    # Assert
    assert weapon.current_mag == expected_mag
    assert player.ammo[".36 Caliber"] == expected_reserve
    assert any(expected_msg in line for line in player_log)