import sys
import time

# Utility Functions
def slow_print(text, delay=0.03):
    """Print text slowly for immersion."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def wait_for_input():
    """Wait for player to press Enter."""
    input("\n[Press Enter to continue...]")

def make_choice(options):
    """Display numbered options and return player’s choice."""
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    while True:
        choice = input("Choose: ")
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return int(choice)
        print("Invalid choice. Try again.")

# Player Stats
player = {
    "sanity": 100,
    "power": 0
}

# Story Functions
def intro():
    slow_print("Arrival at Helsinki Airport...")
    slow_print("The plane lands with a shudder that rattles your molars...")
    slow_print("You step into Helsinki Airport, your footsteps echoing against marble where a hundred others should drown them out...")
    slow_print("The digital departure board flickers, numbers dissolving into static before reassembling.")
    slow_print("A janitor's cart sits abandoned mid-corridor, mop water gone still as glass.")
    slow_print("Ceiling lights buzz and dim in sequence, casting your shadow in three directions at once.")
    slow_print("A child's forgotten teddy bear watches you from a bench with eyes that seem to follow.")
    wait_for_input()
    dark_hallway()

def dark_hallway():
    slow_print("A corridor stretches ahead, marked 'Terminal' in faded letters...")
    slow_print("Your footsteps echo against tile, then suddenly stop—sound swallowed mid-step.")
    slow_print("Twenty feet in, the fluorescent lights end abruptly, leaving a wall of black.")
    slow_print("You squint, but can't make out even the outline of walls beyond—just absence where substance should continue.")
    wait_for_input()
    choice = make_choice([
        "Step inside and investigate",
        "Leave it alone"
    ])
    if choice == 1:
        encounter_with_man()
    else:
        slow_print("Fate loops you back — you cannot escape this path.")
        dark_hallway()

def encounter_with_man():
    slow_print("You step into the black hallway...")
    slow_print("The temperature plummets ten degrees..")
    slow_print("Your lungs strain against air thick as oil...")
    slow_print("Twenty paces in, your shoe squelches in something wet—dark liquid pooling around a crumpled form.")
    slow_print("A hand shoots out, fingers trembling, smearing crimson across your wrist.")
    slow_print("Beneath a torn cassock, chest wounds bubble with each labored breath...")
    slow_print("Yellowed eyes, bloodshot and dilated, find yours with unsettling precision.")
    slow_print("The grip tightens—impossibly strong for someone losing so much blood.")
    slow_print("'I... am Ezekiel,'")
    slow_print("escapes through teeth stained red. ")
    slow_print("'High priest... protector... of this world...'")
    wait_for_input()
    conduit()

def conduit():
    slow_print("Beside the priest you see it.")
    slow_print("Not a machine. Not a sculpture.")
    slow_print("A wound in geometry itself,")
    slow_print("its angles folding inward and outward at once.")
    slow_print("   ")
    slow_print("It hums with a resonance that bypasses your ears,")
    slow_print("vibrating directly in your bones.")
    slow_print("Light and shadow pulse across its surface,")
    slow_print("alive in ways your mind refuses to parse.")
    slow_print("   ")
    slow_print("Ezekiel coughs, blood spattering across your sleeve.")
    slow_print("on His grip your wrist is iron.")
    slow_print('"You must… shut it down. Touch it… before it opens fully..."')
    wait_for_input()
    choice = make_choice([
        "Touch the conduit",
        "Refuse the man"
    ])
    if choice == 1:
        awakening()
    else:
        slow_print('Ezekiel gasps: "You MUST touch it... or all is lost!"')
        conduit()

def awakening():
    slow_print("Your palm meets the surface....")
    slow_print("It is not solid. It is not liquid.")
    slow_print("It is wrong.")
    slow_print("  ")
    slow_print("Agony detonates behind your eyes.")
    slow_print("Visions of stars that should not exist burn themselves into your sight.")
    slow_print("Something vast — something ancient — swivels its awareness toward you.")
    slow_print("   ")
    slow_print("The conduit collapses in on itself,")
    slow_print("a scream of light imploding into silence.")
    slow_print("   ")
    slow_print("But you are not the same.")
    slow_print("Your veins thrum with stolen power.")
    slow_print("Words in no language whisper through your skull.")
    slow_print("Your sanity falters...")
    slow_print("Yet strength fills the void...")
    player["sanity"] -= 20
    player["power"] += 1
    slow_print(f"Sanity now: {player['sanity']} | Power unlocked: {player['power']}")
    wait_for_input()
    shadows_stir()

def shadows_stir():
    slow_print("Ezekiel’s head lolls back,")
    slow_print("but a faint smile clings to his ruined face.")
    slow_print("   ")
    slow_print("Good... you succeeded...")
    slow_print("    ")
    slow_print("His voice trembles on the edge of nothing.")
    slow_print("    ")
    slow_print("The air shifts.")
    slow_print("Where the conduit’s radiance once screamed,")
    slow_print("the shadows now stretch unnaturally long,")
    slow_print("sliding into cracks and corners where no light should reach.")
    slow_print("For the first time in hours — maybe days —")
    slow_print("daylight filters faintly into the hallway.")
    slow_print("     ")
    slow_print("But peace does not follow.")
    slow_print("     ")
    slow_print("A figure bursts from the broken light.")
    slow_print("Cloth robes of black and tattered crimson drape across its frame,")
    slow_print("etched with curling sigils that writhe like living things.")
    slow_print("Chains dangle from its sleeves, rattling in rhythm")
    slow_print("to the low hum of a hymn that never passes its lips.")
    slow_print("The hood slips back, revealing a face locked in rage — veins bulging, eyes fever-bright,")
    slow_print("mouth twisted as if reciting verses too terrible for sound.")
    slow_print("    ")
    slow_print("A cultist of the Order of the Old Ones.")
    slow_print("   ")
    slow_print("It sees you. And it moves.")
    wait_for_input()
    ezekiels_warning()

def ezekiels_warning():
    slow_print("Before the zealot can close the distance, Ezekiel rasps,")
    slow_print("a sudden force behind his fading voice:")
    slow_print('"You must endure yet another hurdle. But fear not… I will guide you."')
    slow_print("   ")
    slow_print("His bloodied hand trembles as he points at your chest.")
    slow_print("   ")
    slow_print('"The conduit marked you. You carry within you.... manifestations.')
    slow_print("Powers pulled from knowledge that no mind should touch.")
    slow_print("I cannot see what gift has taken root first —")
    slow_print("but know this: each manifestation draws on your sanity.")
    slow_print("Spend too much, and you will lose yourself.")
    slow_print('Spend wisely, and you will survive."')
    slow_print("  ")
    slow_print("His words linger, as though pressed into your skull itself.")
    wait_for_input()
    combat_scene()

def combat_scene():
    slow_print("⚔ Combat Tutorial ⚔")
    choice = make_choice([
        "Use manifestation (costs sanity)",
        "Fight physically"
    ])
    if choice == 1:
        player["sanity"] -= 10
        slow_print(f"You unleash power! Sanity drops to {player['sanity']}.")
    else:
        slow_print("You swing wildly, barely surviving the cultist’s assault.")
    wait_for_input()
    aftermath()

def aftermath():
    slow_print("The cultist crumples to the ground, robes pooling like spilled ink...")
    slow_print("The hymn dies in its throat, leaving only the sound of your heartbeat and Ezekiel’s wheezing breath.")
    slow_print("   ")
    slow_print("The corridor is quiet again,")
    slow_print("but your hands tremble — from exertion, from power,")
    slow_print("from something you can no longer deny is inside you.")
    slow_print("   ")
    slow_print("Ezekiel watches, weak eyes gleaming faintly.")
    slow_print('"Yes… you see now. You have survived.')
    slow_print('But survival is only the beginning."')
    wait_for_input()
    #final_words()

def final_words():
    slow_print("His body convulses with another cough, crimson flecking his lips.")
    slow_print("Still, he forces the words out, urgent and deliberate:")
    slow_print("  ")
    slow_print('"You must continue my work.')
    slow_print("The conduits… they are at airports across the world.")
    slow_print('Only you can close them now...."')
    slow_print("    ")
    slow_print("He presses a crumpled, blood-stained note into your palm.")
    slow_print("Scribbled names of airports, written in haste, blur beneath smears of red.")
    slow_print("  ")
    slow_print("His grip slackens.")
    slow_print("With a final ragged breath,")
    slow_print("Ezekiel collapses into silence.")
    slow_print("    ")
    slow_print("The hallway feels colder without his voice.")
    slow_print("And in your hand, the note feels heavier than paper has any right to be.")
    slow_print("")
    wait_for_input()
    #end_game()

def end_game():
    slow_print("GAME OVER – or perhaps just the beginning...")
    slow_print("   ")
    slow_print("............STORY STUFF............")
    slow_print("  ")
    print(f"\nFinal Sanity: {player['sanity']} | Powers: {player['power']}")

# Start the Game
if __name__ == "__main__":
    intro()





