# Edit log: Dota comeback – Rizpol-style meme edit v1

- **Date:** 2026-10-19
- **Brief:** [briefs/comeback-meme.md](../briefs/comeback-meme.md)
- **Project:** `hyperframes/comeback/` (`make_plan.py` → `plan.json` → `scripts/build_meme.py`)
- **Source length / file size:** 2923s (48:43) / 8.76 GB, 1920×1080 60 fps, 3 audio tracks (used track 0, full mix)
- **Output:** `hyperframes/comeback/renders/comeback-v1-share.mp4`, 1920×1080, 30 fps, 7:59, -14 LUFS (master render `comeback-v1.mp4`, 911 MB)

## How moments were found
- Kill score + clock OCR'd from the top bar every 2 s (`scripts/dota_scoreboard.py`, RapidOCR) → kill timeline and the comeback curve
- Voice loudness (tracks 1+2) for hype peaks. Comms are Bisaya; Whisper can't transcribe them reliably, so no subtitles
- Score arc: down 10 by 13.8 min, worst R25–D15 at 25.5 min, lead at 40.6 min (D32–R31), final D40–R34, "Dire Victory" at 46:28 recording time

## Kill moments used (recording seconds)
305, 609, 642, 704, 828–842, 962, 1150, 1180, 1220, 1266, 1528 | 1594, 1640, 1770, 1850, 1890, 2094, 2170, 2356, 2442 | 2562, 2696, 2740, 2745–2795 (push + ancient)

## What was done
- Cold open on the 3-for-0 fight (45 min) → freeze "HOW DID WE GET HERE?" → title card
- Three acts with cards (Getting farmed / The turn / End it) and score cards
- Zoom punch-ins with shake on kills, 0.5× slow-mo + freeze frames with meme text, emoji pops
- Synth SFX (`scripts/meme_sfx.py`): vine boom, whoosh, riser, record scratch, airhorn, ding, sad trombone, bass drop
- Ending: "Dire Victory" slow-mo, airhorns, GG card

## Exports made
| Version | Type | File |
|---|---|---|
| v1 | MP4 1080p30 | hyperframes/comeback/renders/comeback-v1-share.mp4 |

## Issues / limits hit
- OCR misses single-digit scores, so early-game Dire kills are unknown (cards say "R 12 — D ???")
- Captions that guessed at specific heroes or plays were made generic; no music (none provided)
- HyperFrames render of 8 min took 27 min (4 workers, software GPU); output audio landed at -17.4 LUFS, fixed in the share encode
