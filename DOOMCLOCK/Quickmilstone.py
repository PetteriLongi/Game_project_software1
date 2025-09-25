def on_zero(player, enemies, log):
    log.append("\033[91mThe sky opens — you lose.\033[0m")

def at_75(player, enemies, log):
    log.append("\033[95m[75] The chanting grows louder; reality shudders.\033[0m")

def at_50(player, enemies, log):
    log.append("\033[95m[50] Sigils flare; enemies feel stronger.\033[0m")
    for e in enemies:
        if hasattr(e, "attack"):
            e.attack = (e.attack[0] + 1, e.attack[1] + 1)

def at_25(player, enemies, log):
    log.append("\033[95m[25] The veil thins; your mind frays (-5 Sanity).\033[0m")
    if player:
        player["sanity"] = max(0, player["sanity"] - 5)

doom_clock = DoomClock(
    start=100,
    milestones={75: at_75, 50: at_50, 25: at_25},
    on_zero=on_zero
)
# …then call: combat(player, enemies, doom_clock=doom_clock)
# make it so that it takes the at25 and so on from the % of the amount in doom clock *
#for example if the doom clock was 100: 75% would be 75 or if it was 1000 then 25% would be 250 for the event to trigger
#this makes the code much more reliable and robust
