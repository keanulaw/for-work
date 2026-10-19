# Edit log: Stress Lie – Reel 2 style

- **Date:** 2026-10-19
- **Brief:** [briefs/stress-lie-reel2.md](../briefs/stress-lie-reel2.md)
- **invideo project:** https://invideo.io/@shannons-workspa-310/the-stress-lie-short-cut
- **Timeline:** https://invideo.io/@shannons-workspa-310/the-stress-lie-short-cut/tree/main/seq-7.1
- **Source length / file size:** 566.3s / 1.17 GB (HEVC, 23.976 fps)
- **Resolution:** 1080×1920, 30 fps, 22.6s

## Timestamps used
Source 102.9–129.2s ("Stress is going to kill you … it's a beautiful business model"), 18 clips with pauses removed:
102.93–104.73, 104.73–106.60, 106.60–108.27, 108.87–111.30, 112.03–115.57, 115.97–117.60, 118.07–121.10, 121.90–124.80, 125.17–127.03, 127.30–129.20

## What was done
- Hook: single orange words "STRESS IS GOING TO", then a red ink wipe at 0.9s into a red duotone card for "KILL YOU"
- Jump cuts with punch-ins alternating 100% / 125–130% (no animated zooms)
- Captions: Montserrat 900, ALL CAPS, shadow, hard cut-on word by word. White phrases build 1–3 words; key words (STRESSFUL, STRESSED, DEALER, CRACK, ADDICTED, MONEY, BUSINESS, MODEL) shown alone in orange
- Black text beat "SO WHAT IS THAT" (7.8–8.4s), then a red ink wipe into the red duotone card "THAT'S LIKE A DRUG DEALER RUNNING A DRUG REHAB CENTER" (8.4–11.3s)
- Red ink wipe: custom GLSL transition ("Red Ink Wipe"), 6 frames, from the top-right with a rough edge
- Red duotone: `tint` (#7A0503 → #FFD27A) + `edge_roundness` 0.06 at 90% scale on a solid #E3170A background
- Vignette: adjustment layer grade, vignette 0.85
- Hard cut ending on "MODEL"
- Audio normalized to -14 LUFS on export

## Exports made
| Version | Type | Link / file |
|---|---|---|
| v1 | video 1080p | https://invideo.io/@shannons-workspa-310/the-stress-lie-short-cut/notebook/seq-8.1 |

## Issues / limits hit
- invideo has no transcription, so I reused the word timings from the earlier "Stress Lie short" captions (source 100–129s only)
- No film or stock b-roll cards (none provided; stock may use credits). No music or SFX
- capture fails on large batches that include custom-transition frames, and on a transition from a disabled clip. Batches of 3 frames work; tint the clip black instead of disabling it
