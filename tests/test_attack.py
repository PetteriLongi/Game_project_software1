import pytest
import builtins
import random

from game.combat import combat

class DummyPlayer:
    def __init__(self, weapon=None, ammo=None, base_attack=(3, 3), hp=10, sanity=10):
        self.hp = 10
        self.max_hp = hp
        self.sanity = sanity
        self.max_sanity = sanity
        self.base_attack = base_attack
        self.weapon = weapon
        self.ammo = ammo or {}
        self.manifestations = []
        self.inventory = []
        self.exp = 0
    def gain_exp(self, amount):
        self.exp += amount

class DummyEnemy:
    def __init__(self, name="Dummy Enemy", hp=10):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.exp_reward = 1
        self.exp_awarded = False
    def take_turn(self, player, enemies_list, defending):
        return f"{self.name} does nothing"

class DummyWeapon:
    def __init__(self, name="Test Dagger", attack_range=(5, 5), weapon_type="melee",
                 mag_size=0, current_mag=0, ammo_type=".36 Caliber"):
        self.name = name
        self.attack_range = attack_range
        self.weapon_type = weapon_type
        self.mag_size = mag_size
        self.current_mag = current_mag
        self.ammo_type = ammo_type

def make_input_sequence(inputs):
    it = iter(inputs)
    def _fake_input(_prompt=""):
        return next(it)
    return _fake_input

# --------- Tests ---------

def test_attack_melee_kills_enemy_and_exits(monkeypatch, capsys):
    # Player uses melee weapon with deterministic damage 5
    player = DummyPlayer(weapon=DummyWeapon(name="Knife", attack_range=(5, 5), weapon_type="melee"))
    enemy = DummyEnemy(name="Cultist", hp=5)

    # Input sequence:
    #   "1" -> choose Attack
    #   "1" -> choose first target
    # Enemy will die, combat should print victory and return True
    monkeypatch.setattr(builtins, "input", make_input_sequence(["1", "1"]))

    # Ensure random.randint returns 5 even if code calls it (already set via weapon range)
    monkeypatch.setattr(random, "randint", lambda a, b: 5)

    result = combat(player, [enemy])
    out = capsys.readouterr().out

    assert result is True
    assert enemy.hp == 0  # took 5 damage
    # Check key logs exist
    assert "Choose your action:" in out
    assert "Choose a target" in out
    assert "You strike Cultist with Knife for 5 damage!" in out
    assert "All enemies have been defeated! Victory is yours!" in out

def test_attack_gun_with_ammo_consumes_round_and_deals_damage(monkeypatch, capsys):
    # Gun with 1 round in mag, fixed damage 7
    weapon = DummyWeapon(
        name="Old revolver",
        attack_range=(7, 7),
        weapon_type="gun",
        mag_size=6,
        current_mag=1,
        ammo_type=".36 Caliber",
    )
    player = DummyPlayer(weapon=weapon, ammo={".36 Caliber": 10})
    enemy = DummyEnemy(name="Cultist", hp=10)

    monkeypatch.setattr(builtins, "input", make_input_sequence(["1", "1"]))
    monkeypatch.setattr(random, "randint", lambda a, b: 7)

    # Run one round; enemy won’t die so combat would continue.
    # To avoid a long loop, set enemy HP low enough to die:
    enemy.hp = 7

    result = combat(player, [enemy])
    out = capsys.readouterr().out

    assert result is True
    # Shot consumed 1 round
    assert weapon.current_mag == 0
    # Enemy took 7 damage and died
    assert enemy.hp == 0
    # Log shows gun fire status line and strike line
    assert "You fire Old revolver! (0/6 in mag, 10 in reserve)" in out
    assert "You strike Cultist with Old revolver for 7 damage!" in out

def test_attack_gun_empty_mag_with_ammo_shows_click_and_no_damage(monkeypatch, capsys):
    # Gun with empty mag and reserve > 0
    weapon = DummyWeapon(
        name="Old revolver",
        attack_range=(7, 7),
        weapon_type="gun",
        mag_size=6,
        current_mag=0,
        ammo_type=".36 Caliber",
    )
    player = DummyPlayer(weapon=weapon, ammo={".36 Caliber": 5})
    enemy = DummyEnemy(name="Cultist", hp=10)

    # Attack once, then immediately make enemy die to exit:
    monkeypatch.setattr(builtins, "input", make_input_sequence(["1", "1"]))
    # Even if randint is called, damage should be 0 due to empty mag
    monkeypatch.setattr(random, "randint", lambda a, b: 7)

    # To ensure the loop ends quickly, set enemy HP to 0 after the player turn by
    # modifying enemy.take_turn to kill itself (no-op pattern):
    def no_op_turn(player_, enemies_, defending):
        # kill enemy to break loop (simulate external event)
        enemy.hp = 0
        return "..."
    enemy.take_turn = no_op_turn

    result = combat(player, [enemy])
    out = capsys.readouterr().out

    assert result is True
    # No rounds consumed because mag was empty; damage must be 0
    assert weapon.current_mag == 0
    assert "Click! Your magazine is empty. Reload first." in out
    # There will still be a strike line with 0 damage, per current implementation
    assert "for 0 damage!" in out
    # Enemy was set to 0 hp during enemy turn to terminate the loop

def test_attack_gun_empty_mag_no_ammo_shows_no_ammo(monkeypatch, capsys):
    weapon = DummyWeapon(
        name="Old revolver",
        attack_range=(7, 7),
        weapon_type="gun",
        mag_size=6,
        current_mag=0,
        ammo_type=".36 Caliber",
    )
    player = DummyPlayer(weapon=weapon, ammo={".36 Caliber": 0})
    enemy = DummyEnemy(name="Cultist", hp=10)

    monkeypatch.setattr(builtins, "input", make_input_sequence(["1", "1"]))
    monkeypatch.setattr(random, "randint", lambda a, b: 7)

    # Also force exit quickly
    def no_op_turn(player_, enemies_, defending):
        enemy.hp = 0
        return "..."
    enemy.take_turn = no_op_turn

    result = combat(player, [enemy])
    out = capsys.readouterr().out

    assert result is True
    assert weapon.current_mag == 0
    assert "Click! You have no ammo left." in out