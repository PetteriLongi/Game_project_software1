# ==========================================
# WORLD LOOP + DOOM CLOCK INTEGRATION
# (Rites of Transit — console prototype)
# ==========================================

import random
from typing import List, Optional

# ----- assume these exist in your project -----
# from your_module import combat, DoomClock, draw_bar
# Here are SMALL helpers used by the HUD below:

def hud_bar(label, cur, maxv, color="default"):
    return draw_bar(label, cur, maxv, color=color, name_width=12, bar_length=20)

# ----- simple data holders you can replace with your DB models -----
class Airport:
    def __init__(self, name: str, code: str, region: str):
        self.name = name
        self.code = code
        self.region = region
        self.has_conduit = False
        self.conduit_closed = False

# ==========================================
# GAME STATE
# ==========================================

class GameState:
    def __init__(self, start_airport: Airport, doom_clock: DoomClock):
        self.location: Airport = start_airport
        self.doom: DoomClock = doom_clock

        # Player stats (from your spec)
        self.sanity = 100
        self.max_sanity = 100
        self.markka = 100

        # Progress
        self.closed_conduits = 0
        self.victory_target = 5

        # Inventory / story flags
        self.has_bloodied_note = True
        self.note_airports: List[str] = []   # put 5 IATA strings here
        self.visited: set[str] = set([start_airport.code])
        self.powers = ["Eldritch Sense"]     # tutorial grants this

        # world data
        self.world_airports: List[Airport] = [start_airport]  # fill later from DB

        # last log (for printing after actions)
        self.turn_log: List[str] = []

    # ---------- convenience ----------
    def is_dead(self) -> bool:
        return self.sanity <= 0

    def lost_by_doom(self) -> bool:
        return self.doom.ticks <= 0 and self.doom.resolved

    def won(self) -> bool:
        return self.closed_conduits >= self.victory_target

    def log(self, msg: str):
        self.turn_log.append(msg)

# ==========================================
# WORLD UI / HELP / HUD
# ==========================================

def print_hud(gs: GameState):
    left1 = hud_bar("Sanity", gs.sanity, gs.max_sanity, color="sanity")
    left2 = f"Markka      : {gs.markka}"
    left3 = hud_bar(gs.doom.name, gs.doom.ticks, gs.doom.start, color="doom")
    print("\n\033[96m=== STATUS ===\033[0m")
    print(left1)
    print(left2)
    print(left3)
    print(f"Location    : {gs.location.name} ({gs.location.code})")
    print(f"Conduits    : {gs.closed_conduits}/{gs.victory_target}")

def print_help():
    print("\n\033[94mHELP\033[0m — keyboard only")
    print("[T] Travel  [I] Inventory  [H] Help  [Q] Quit")
    print("During travel you’ll get 3 airport options (Note / nearby / wildcard).")
    print("Travel costs Markka and advances the Doom Clock.")
    print("If a Conduit exists at destination, you may attempt closure.")
    print("Close 5 conduits to win. Doom or Sanity hitting 0 = loss.")
    print("(Showing help does NOT consume a turn.)")

# ==========================================
# TRAVEL OPTION GENERATION (stub to replace with DB logic)
# ==========================================

def pick_travel_options(gs: GameState) -> List[Airport]:
    """
    Returns 3 airports:
    - 1 from Bloodied Note (if any remaining and not visited) or fallback
    - 1 nearby (same region) if available
    - 1 wildcard (anywhere)
    Replace this with real DB-backed selection using your course dataset.
    """
    world = gs.world_airports

    def not_visited(a: Airport) -> bool:
        return a.code not in gs.visited

    # Note pick
    note_candidates = [a for a in world if a.code in gs.note_airports and not_visited(a)]
    if not note_candidates and gs.has_bloodied_note:
        # if the note was "used up", your spec says allow random from DB
        note_candidates = [a for a in world if not_visited(a)]
    note_pick = random.choice(note_candidates) if note_candidates else gs.location

    # Nearby pick
    nearby_candidates = [a for a in world if a.region == gs.location.region and not_visited(a) and a.code != note_pick.code]
    nearby_pick = random.choice(nearby_candidates) if nearby_candidates else note_pick

    # Wildcard
    wildcard_candidates = [a for a in world if not_visited(a) and a.code not in (note_pick.code, nearby_pick.code)]
    wildcard_pick = random.choice(wildcard_candidates) if wildcard_candidates else nearby_pick

    # Ensure 3 unique results (fallback to current if needed)
    options = [note_pick, nearby_pick, wildcard_pick]
    # If duplicates slipped in, pad with current to keep 3 slots
    while len(set(a.code for a in options)) < 3:
        options.append(gs.location)
        options = options[:3]
    return options

def travel_cost(gs: GameState, src: Airport, dst: Airport) -> int:
    """Very simple placeholder cost. Swap with distance-based cost from your DB."""
    if src.region == dst.region:
        return 8   # nearby
    return 20     # mid/long

# ==========================================
# EVENTS / CONDUITS (stubs you can flesh out)
# ==========================================

def travel_event(gs: GameState):
    """
    Random simple event per spec: fight / check / flavour.
    Keep it deterministic-by-choice for the prototype.
    """
    roll = random.random()
    if roll < 0.33:
        # Cultists at Gate — choice
        print("\nEvent: Cultists at the Gate.")
        print("[A] Confront  [S] Slip past")
        ch = input("> ").strip().lower()
        if ch == "a":
            gs.sanity = max(0, gs.sanity - 3)
            gs.markka += 5
            gs.log("\033[92mYou confront them, scattering the cultists. -3 Sanity, +5 Markka.\033[0m")
        else:
            gs.sanity = max(0, gs.sanity - 1)
            gs.log("\033[94mYou slip past in the crowd. -1 Sanity.\033[0m")

    elif roll < 0.66:
        # Static Interference — a skill check gate
        print("\nEvent: Static Interference.")
        print("[F] Focus (requires Eldritch Sense)  [W] Wait")
        ch = input("> ").strip().lower()
        if ch == "f" and "Eldritch Sense" in gs.powers:
            gs.log("\033[96mYou pierce the noise. A whisper hints at a nearby conduit.\033[0m")
        else:
            gs.log("\033[90mYou wait. Nothing changes.\033[0m")
    else:
        # Flavour
        gs.log("\033[90mA cold draft curls through the terminal. Someone hums an old hymn.\033[0m")

def conduit_check(gs: GameState, airport: Airport):
    """
    30% generic chance OR 100% if the airport is on the Note and not yet cleared.
    """
    guaranteed = (airport.code in gs.note_airports) and (not airport.conduit_closed)
    if guaranteed:
        airport.has_conduit = True
        return

    # otherwise 30% generic
    if not airport.conduit_closed and random.random() < 0.30:
        airport.has_conduit = True
    else:
        airport.has_conduit = False

def attempt_closure(gs: GameState, airport: Airport):
    """
    Prototype closure: deterministic success (you can add a mini-check).
    Effects per spec: -Sanity, +Markka, Doom -1, Gain Power (story beat).
    """
    print("\nConduit hums with alien geometry.")
    print("[1] Attempt Closure  [2] Leave")
    ch = input("> ").strip()
    if ch != "1":
        gs.log("\033[93mYou turn away. The conduit remains.\033[0m")
        return

    # Closure resolves
    airport.conduit_closed = True
    gs.closed_conduits += 1
    gs.sanity = max(0, gs.sanity - 5)
    gs.markka += 10
    gs.doom.countdown(1, None, None, gs.turn_log, reason="Conduit closure ripples time.")
    # grant next power (placeholder)
    new_power = f"Manifestation #{gs.closed_conduits}"
    gs.powers.append(new_power)
    gs.log(f"\033[92mConduit sealed! -5 Sanity, +10 Markka, new Power: {new_power}\033[0m")

# ==========================================
# WORLD LOOP
# ==========================================

def world_loop(gs: GameState):
    """
    Core loop: Travel → Event → Arrival → Conduit → Repeat,
    with Doom Clock counting down on travel turns.
    """
    print("\n\033[95m--- Rites of Transit ---\033[0m")
    while True:
        gs.turn_log.clear()
        print_hud(gs)

        # Win/Loss checks at start of turn
        if gs.won():
            print("\n\033[92mYou closed the final conduit. The world exhales.\033[0m")
            break
        if gs.is_dead():
            print("\n\033[91mYour mind unthreads.\033[0m")
            break
        if gs.lost_by_doom():
            print("\n\033[91mThe sky opens.\033[0m")
            break

        print("\n\033[96mChoose:\033[0m [T] Travel  [I] Inventory  [H] Help  [Q] Quit")
        cmd = input("> ").strip().lower()

        # ---------- HELP (no time passes) ----------
        if cmd == "h":
            print_help()
            continue  # help does not consume a turn; do not tick doom

        # ---------- INVENTORY (prototype) ----------
        if cmd == "i":
            print("\nInventory:")
            print(f" - Bloodied Note: {'Yes' if gs.has_bloodied_note else 'No'}")
            print(" - Ezekiel’s Token")
            print(" - Powers:", ", ".join(gs.powers))
            # inventory browsing does NOT consume doom
            input("(Enter to return) ")
            continue

        # ---------- QUIT ----------
        if cmd == "q":
            print("\n\033[90mReturning to title screen...\033[0m")
            break

        # ---------- TRAVEL ----------
        if cmd == "t":
            # build 3 options
            options = pick_travel_options(gs)
            print("\n\033[96mWhere to?\033[0m")
            for i, ap in enumerate(options, 1):
                cost = travel_cost(gs, gs.location, ap)
                afford = "" if gs.markka >= cost else " [Insufficient funds]"
                tag = "Note" if ap.code in gs.note_airports else ("Nearby" if ap.region == gs.location.region else "Wildcard")
                print(f"{i}. {ap.name} ({ap.code}) - {tag}, Cost {cost}{afford}")

            print("0. Cancel")
            sel = input("> ").strip()
            if sel == "0":
                continue

            if not (sel.isdigit() and 1 <= int(sel) <= len(options)):
                print("\033[93mInvalid selection. Try again.\033[0m")
                continue

            dst = options[int(sel) - 1]
            cost = travel_cost(gs, gs.location, dst)
            if gs.markka < cost:
                print("\033[93mInsufficient funds. Choose another route.\033[0m")
                continue

            # Pay cost
            gs.markka -= cost

            # ---- Doom advances for travel (per spec) ----
            gs.doom.countdown(1, None, None, gs.turn_log, reason="Travel consumes precious time.")

            # Arrival flavour + sustainability fact (placeholder)
            print(f"\nArriving at \033[96m{dst.name} ({dst.code})\033[0m")
            gs.log("\033[90mA banner flaps in recycled airflow. Electric ground vehicles hum.\033[0m")

            # Travel event (fight/check/flavour). If you call combat() here, pass gs.doom.
            travel_event(gs)

            # Move location and mark visited
            gs.location = dst
            gs.visited.add(dst.code)

            # Conduit check
            conduit_check(gs, dst)

            # If conduit present, allow attempt
            if dst.has_conduit and not dst.conduit_closed:
                attempt_closure(gs, dst)

        else:
            print("\033[93mInvalid selection. Try again.\033[0m")
            continue

        # ---------- POST-TURN: LOSS/WIN re-check ----------
        if gs.won():
            print("\n\033[92mYou closed the final conduit. The world exhales.\033[0m")
            break
        if gs.is_dead():
            print("\n\033[91mYour mind unthreads.\033[0m")
            break
        if gs.lost_by_doom():
            print("\n\033[91mThe sky opens.\033[0m")
            break

        # ---------- Show turn log ----------
        if gs.turn_log:
            print("\n\033[95m" + "=" * 50 + "\033[0m")
            for line in gs.turn_log:
                print(line)
            print("\033[95m" + "=" * 50 + "\033[0m")

# ==========================================
# QUICK BOOTSTRAP (replace with your DB)
# ==========================================

def bootstrap_demo(doom_clock: Optional[DoomClock] = None):
    # sample world resembling your spec
    hel = Airport("Helsinki Airport", "HEL", "Nordics")
    arn = Airport("Stockholm Arlanda", "ARN", "Nordics")
    muc = Airport("Munich", "MUC", "Central")
    lhr = Airport("London Heathrow", "LHR", "West")
    cdg = Airport("Paris Charles de Gaulle", "CDG", "West")
    fra = Airport("Frankfurt", "FRA", "Central")

    world = [hel, arn, muc, lhr, cdg, fra]

    # assign a couple of note airports
    note = ["ARN", "MUC", "LHR", "CDG", "FRA"]

    # mark 100% conduit chance for note airports (until cleared)
    # (the actual guarantee is handled in conduit_check)
    for ap in world:
        ap.conduit_closed = False

    # doom clock with milestones (editable)
    if doom_clock is None:
        def on_zero(_, __, log): log.append("\033[91mDoom hits 0 — the sky opens.\033[0m")
        def at_75(_, __, log): log.append("\033[95m[75] Chanting grows louder.\033[0m")
        def at_50(_, __, log): log.append("\033[95m[50] Sigils flare.\033[0m")
        def at_25(_, __, log): log.append("\033[95m[25] Reality buckles.\033[0m")
        doom_clock = DoomClock(start=100, milestones={75: at_75, 50: at_50, 25: at_25}, on_zero=on_zero)

    gs = GameState(start_airport=hel, doom_clock=doom_clock)
    gs.world_airports = world
    gs.note_airports = note

    world_loop(gs)

# if __name__ == "__main__":
#     bootstrap_demo()
