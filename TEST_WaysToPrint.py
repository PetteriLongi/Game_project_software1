## testing stuff for the project, this one is for testing atmospheric ways to print text!

#import time
#import sys

#def print_slow_letters(text, delay=0.1):
#    for char in text:
#        sys.stdout.write(char)
#        sys.stdout.flush()
#        time.sleep(delay)
#    print()

#part1 ="""  The plane lands with a shudder.
#	You step into Helsinki Airport.
#	Something feels... wrong.
#	The halls are quiet."""

#pause_duration = 1

#part2 = """\n   Too quiet.
#	Lights flicker above.
#	Shadows stretch longer than they should."""

#print_slow_letters(part1, delay=0.05)
#print_slow_letters("    .", delay=0.1)
#print_slow_letters("    .", delay=0.1)
#print_slow_letters("    .", delay=0.1)
#time.sleep(pause_duration)
#print_slow_letters(part2, delay=0.05)

import time
import sys
import re

text = "	The plane lands with a shudder.  You step into Helsinki Airport. Something feels... wrong. The halls are quiet. Too quiet. Lights flicker above. Shadows stretch longer than they should."
ghost = "🩸"  # you can swap for 💀, ☠️, 👻, etc.

sentences = re.split(r'(?<=[.!?]) +', text)
def ghost_slide(sentence, delay=0.1):
    for i in range(len(sentence)):
        # Build the line: revealed letters + ghost + hidden spaces
        line = sentence[:i] + ghost + " " * (len(sentence) - i - 1)
        sys.stdout.write("\r" +" " * (len(sentence) - i - 1))
        sys.stdout.write("\r" + line)   # overwrite same line
        sys.stdout.flush()
        time.sleep(delay)  # adjust for speed (slower = creepier)
    sys.stdout.write("\r" + sentence + "\n")

for sentence in sentences:
    ghost_slide(sentence)
    time.sleep(0.5)