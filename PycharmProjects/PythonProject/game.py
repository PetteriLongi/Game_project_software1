import sys
import time
def slow_print(text, delay=0.05) :
    """Print text slowly to add horror effect."""
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()

def main_menu():
    while True:
        print("\n" + "=" * 40)
        print("       █▓▒░  Rites of transit  ░▒▓█")
        print("=" * 40)
        print(" [1] Descend into the Unknown (New Game)")
        print(" [2] Whispers of Guidance (Help)")
        print(" [3] Escape the Void (Exit)")
        print("=" * 40)

        choice = input("\nChoose your fate (1-3): ")

        if choice == "1":
            slow_print("\nYou step into the abyss... The horror begins.\n")
            # Here you would call your game start function
            break

        elif choice == "2":
            slow_print("\nThe whispers guide you...")
            # Call Jack’s Help menu function here
            # help_menu()
            print("[Help menu content goes here]\n")

        elif choice == "3":
            slow_print("\nThe void consumes you... Farewell.\n")
            sys.exit()

        else:
            slow_print("The cosmos does not understand your choice... Try again.")


if __name__ == "__main__":
    main_menu()





