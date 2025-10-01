from ..config import USE_ANSI, COLOR_RESET

COLOURS = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "purple": "\033[95m",
    "magenta": "\033[95m",
    "cyan": "\033[96m",
    "white": "\033[97m",
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "italic" : "\033[3m",

}

def colouring(text, colour=None, style=None):
    colour_code = COLOURS.get(colour, "")
    style_code = COLOURS.get(style, "")
    return f"{style_code}{colour_code}{text}{COLOURS['reset']}"

def colorize(text: str, color: str | None, strike: bool=False) -> str:
    if not USE_ANSI:
        return text
    prefix = ""
    if color:
        prefix += color
    if strike:
        prefix += "\033[9m"  # strikethrough
    return f"{prefix}{text}{COLOR_RESET}"

#print(colouring("fuck", "red","italic"))