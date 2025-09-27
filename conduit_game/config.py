# conduit_game/config.py

# ---------- Gameplay tunables ONLY FILE ----------
RATE_PER_KM = 0.5              # Markka per km
REWARD_MARKKA = 100            # Reward for closing a conduit
SANITY_LOSS = 5                # Sanity penalty when closing a conduit
START_MARKKA = 5_000_000       # Starting money
START_SANITY = 100             # Starting sanity
START_HP = 100                 # Starting HP for [3] Rest

NUM_AIRPORT_CHOICES = 10       # How many airports to show (excl. HEL)
NUM_CONDUITS = 5               # How many conduits hidden in those airports

# ---------- DB settings ----------
DB_USER = "gameuser"
DB_PASSWORD = "yourpassword"   # change me
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "flight_game"        # your SQL script created this

# ---------- UI / Colors ----------
USE_ANSI = True  # turn off if terminal is weird

# You can swap these if we want different colors:
COLOR_VISITED = "\033[92m"             # neo green
COLOR_CONDUIT_CLOSED = "\033[91m"      # corrupted red
COLOR_OPEN_CONDUIT = "\033[93m"        # yellow
COLOR_RESET = "\033[0m"
