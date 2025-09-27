# conduit_game/utils/colors.py
from . import __init__ as pkg_init  # not required, just for packaging
from ..config import USE_ANSI, COLOR_RESET

def colorize(text: str, color: str | None, strike: bool=False) -> str:
    if not USE_ANSI:
        return text
    prefix = ""
    if color:
        prefix += color
    if strike:
        prefix += "\033[9m"  # strikethrough
    return f"{prefix}{text}{COLOR_RESET}"
