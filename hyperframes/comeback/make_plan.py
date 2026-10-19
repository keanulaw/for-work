"""Writes plan.json for the comeback edit. Kill times come from media/cb_score.json (score OCR)."""
import json

items = []
def card(*lines, dur=2.2, sfx=None, bg="#000"):
    items.append({"card": list(lines), "dur": dur, "sfx": sfx or [[0, "whoosh", 0.8]], "bg": bg})

def fight(k, pre=10, post=4, slow=False, text=(), emoji=(), sfx=(), freeze=None, zoom=1.35, shake=True):
    """k = recording time of the kill. Optional slow-mo of the 1.5 s around it, then a freeze frame."""
    if slow:
        a, b = k - pre, k - 1.0
        items.append({"clip": [a, b], "zoom": [[b - a - 1.2, zoom, 50, 42, 0.5]]})
        it = {"clip": [k - 1.0, k + 0.8], "speed": 0.5, "zoom": [[0, zoom + 0.15, 50, 42, 0.3]],
              "shake": [[2.0, 0.35]] if shake else [], "sfx": [[1.9, "vine_boom", 0.9]]}
        items.append(it)
        rest = [k + 0.8, k + post]
    else:
        rest = [k - pre, k + post]
        it = None
    main = {"clip": rest, "text": [], "emoji": [], "sfx": list(sfx)}
    off = 0 if slow else pre
    main["zoom"] = [] if slow else [[max(0, off - 1.4), zoom, 50, 42, 0.45], [off + 1.2, 1.0, 50, 50, 0.6]]
    if shake and not slow:
        main["shake"] = [[off - 0.2, 0.35]]
    main["text"] = [[off + a, d, t, p] for a, d, t, p in text]
    main["emoji"] = [[off + a, d, e, x, y] for a, d, e, x, y in emoji]
    main["sfx"] = [[off + a, n, g] for a, n, g in sfx]
    items.append(main)
    if freeze:
        items.append({"freeze": rest[1], "dur": freeze[0], "zoom": 1.25, "text": freeze[1], "emoji": freeze[2] if len(freeze) > 2 else [],
                      "sfx": freeze[3] if len(freeze) > 3 else [[0, "record_scratch", 0.9]]})

# cold open: the team wipe, then rewind
fight(2740, pre=9, post=1.5, slow=True,
      freeze=(2.2, [[0, 2.2, "HOW DID WE GET HERE?", "bottom"]], [[0.2, 2.0, "🤨", 82, 30]]))
card("THE COMEBACK", "DOWN 10 KILLS AT MINUTE 25", "we're dire btw", dur=3.2, sfx=[[0, "bass_drop", 0.9]])
card("PART 1", "GETTING FARMED", dur=2.0)

# act 1: early game pain (radiant kills)
fight(305, pre=10, post=4, text=[[0, 2.2, "IT'S JUST LANING BRO", "top"]])
fight(609, pre=9, post=4, text=[[0.3, 2.5, "bro 💀", "small"]], emoji=[[0.4, 1.8, "💀", 80, 32]], sfx=[[0.3, "vine_boom", 0.9]])
fight(642, pre=7, post=4, sfx=[[0, "vine_boom", 0.8]], emoji=[[0.1, 1.5, "😭", 20, 30]])
fight(704, pre=8, post=4, text=[[0, 2.2, "WHAT IS HAPPENING", "top"]])
fight(841, pre=16, post=4, text=[[-6, 2, "MINUTE 14", "small"], [0.2, 3, "3 DEATHS IN 15 SECONDS", "bottom"]],
      sfx=[[0.3, "sad_trombone", 0.9]], freeze=(1.6, [[0, 1.6, "R 12 — D ???", "mid"]], [[0.2, 1.4, "📉", 78, 30]]))
fight(962, pre=8, post=4, emoji=[[0, 1.6, "💀", 50, 30]], sfx=[[0, "vine_boom", 0.8]])
fight(1150, pre=10, post=4, text=[[0, 2.5, "we got caught. again.", "small"]])
fight(1180, pre=8, post=4, sfx=[[0, "vine_boom", 0.9]], emoji=[[0.1, 1.6, "🗿", 82, 30]])
fight(1220, pre=10, post=4, text=[[0, 2.5, "WAIT WE GOT KILLS?", "top"]], sfx=[[0, "ding", 0.7]], emoji=[[0.2, 1.6, "😳", 20, 30]])
fight(1266, pre=10, post=4, text=[[0, 2.0, "nvm", "bottom"]], sfx=[[0, "sad_trombone", 0.8]])
fight(1528, pre=16, post=4, slow=True, freeze=(2.0, [[0, 2.0, "IT'S OVER.", "mid"]], [[0.2, 1.8, "💀", 80, 30]], [[0, "vine_boom", 1.0]]))
card("MINUTE 25", "RADIANT 25 — DIRE 15", "surely it's over", dur=3.0)
card("...OR IS IT?", dur=1.6, sfx=[[0, "riser", 0.8]], bg="#100000")

# act 2: the turn
card("PART 2", "THE TURN", dur=2.0)
fight(1594, pre=14, post=4, slow=True, freeze=(1.8, [[0, 1.8, "DOUBLE KILL?!", "bottom"]], [[0.2, 1.6, "😳", 80, 30]], [[0, "airhorn", 0.8]]))
fight(1640, pre=10, post=4, text=[[0, 2.2, "R 25 — D 19", "small"]], sfx=[[0, "ding", 0.6]])
fight(1770, pre=10, post=4, text=[[0.2, 2.5, "the gap is closing 👀", "small"]])
fight(1850, pre=20, post=5, text=[[0, 2.5, "TEAMFIGHT", "top"]], sfx=[[-0.2, "vine_boom", 0.8]], emoji=[[0.4, 1.6, "🔥", 80, 30]])
fight(1890, pre=10, post=4, text=[[0, 2.5, "R 27 — D 24", "small"]])
fight(2094, pre=16, post=4, text=[[-9, 2, "MINUTE 34", "small"], [0.2, 2.5, "two for us", "bottom"]], sfx=[[0, "ding", 0.6]])
fight(2170, pre=12, post=4, slow=True, freeze=(1.8, [[0, 1.8, "DOUBLE KILL 🗿", "bottom"]], [], [[0, "airhorn", 0.8]]))
fight(2356, pre=10, post=4, text=[[0, 2.5, "R 31 — D 29", "small"]], emoji=[[0.3, 1.6, "👀", 80, 30]])
card("MINUTE 40", "ONE FIGHT AWAY", dur=2.0, sfx=[[0, "riser", 0.7]])
fight(2442, pre=18, post=4, slow=True, freeze=(2.4, [[0, 2.4, "WE'RE AHEAD???", "bottom"]], [[0.2, 2.2, "😭", 80, 30]], [[0, "airhorn", 1.0]]))

# act 3: end it
card("PART 3", "END IT", dur=2.0, sfx=[[0, "bass_drop", 0.8]])
fight(2562, pre=10, post=4, text=[[0, 2, "they're not done yet", "small"]])
fight(2696, pre=22, post=4, text=[[-12, 2.2, "MINUTE 44", "small"], [0.2, 2.5, "R 33 — D 35", "bottom"]], sfx=[[0, "vine_boom", 0.8]], emoji=[[0.3, 1.6, "🔥", 80, 30]])
fight(2740, pre=10, post=3, slow=True, freeze=(2.0, [[0, 2.0, "3 FOR 0", "mid"]], [[0.2, 1.8, "🗿", 80, 30]], [[0, "bass_drop", 1.0]]))
items.append({"clip": [2745, 2770], "text": [[3, 2.5, "PUSH. PUSH. PUSH.", "top"]]})
items.append({"clip": [2770, 2787], "zoom": [[14, 1.3, 50, 40, 0.8]], "text": [[2, 2.5, "R 34 — D 40", "small"]]})
items.append({"clip": [2787, 2795], "speed": 0.5, "zoom": [[0, 1.2, 50, 35, 0.6]], "sfx": [[0, "airhorn", 1.0], [0.6, "airhorn", 0.8]],
              "emoji": [[1.2, 3, "🏆", 85, 70]]})
card("GG", "FROM 10 KILLS DOWN TO DIRE VICTORY", "like if you'd have alt+f4'd at minute 25", dur=4.0, sfx=[[0, "ding", 0.8]])

json.dump({"project": "hyperframes/comeback", "source": "media/comeback.mp4", "audio_stream": 0,
           "sfx_dir": "media/sfx", "items": items}, open("plan.json", "w"), indent=1, ensure_ascii=False)
print(len(items), "items")
