# Edit log: Stress Lie – Reel 2 style (HyperFrames v1)

- **Date:** 2026-10-19
- **Brief:** [briefs/stress-lie-reel2.md](../briefs/stress-lie-reel2.md) (redone in HyperFrames instead of invideo)
- **Project:** `hyperframes/stress-lie/` (edit plan: `plan.json`, built with `scripts/build_reel.py`)
- **Source length / file size:** raw 566.3s / 1.19 GB (Drive), 1080×1920 HEVC 23.976 fps
- **Output:** `hyperframes/stress-lie/renders/stress-lie-reel2-v1.mp4`, 1080×1920, 30 fps, 28.1s, 52.8 MB, -15 LUFS

## Timestamps used (source)
Hook 301.74–305.40 ("Your heart isn't actually a muscle. It's 60% nerve fiber") → 270.40–278.56 → 278.90–285.32 (voice over b-roll) → 287.06–288.86 → 289.48–290.80 → 291.36–298.10 → 298.58–301.30 ("It's a nerve.")

B-roll: YPO keynote IMG_6856 @60s (card), ice plunge IMG_9447 @2s and IMG_9452 @10s (full frame).

## What was done
- Full transcript with faster-whisper small.en (`scripts/transcribe.py`); picked the 4:30–5:05 heart/nerve moment
- Cold-open hook with single orange words, then a red ink wipe into a red duotone card on "60% nerve fiber"
- Jump cuts, punch-ins alternating 100% / 125–138%, no animated zooms
- Captions: Montserrat 900, orange gradient keywords, building white phrases, hard cut-on per word; a stacked block on "your body's nervous system is compressing"
- Black beat on "heart attack" (keywords only), red ink wipe into the red card for the payoff
- Torn black corners on red beats, vignette throughout, hard-cut ending on "NERVE"
- Voice loudness-normalised to -14 LUFS (measures -15 integrated in the render)

## Exports made
| Version | Type | File |
|---|---|---|
| v1 | MP4 1080×1920 | hyperframes/stress-lie/renders/stress-lie-reel2-v1.mp4 |

## Issues / limits hit
- Transcript says "dropped out of a heart attack" (likely "drop dead"); that clip shows only HEART / ATTACK to avoid a wrong caption
- No music or SFX (none provided)
- A 1-frame caption overlap at state boundaries came from float rounding; captions are now snapped to whole frames
