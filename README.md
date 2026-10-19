# Video editing workspace

Edits are done by Claude in invideo's timeline editor (via MCP). This repo holds everything around them.

| Folder | What's in it |
|---|---|
| `briefs/` | One .md per video request |
| `edit-logs/` | One .md per finished edit |
| `styles/` | Reusable presets: captions, titles, pacing, color |
| `prompts/` | Prompts that worked well |
| `scripts/` | Helper code (ffmpeg trims, compression) |
| `notes/` | What we've learned about invideo's tools and limits |
| `media/` | Optional local footage (git-ignored) |

## Start a new edit
1. `cp briefs/_template.md briefs/<video-name>.md`
2. Fill it in (source path, length, aspect ratio, style...).
3. Ask Claude: "Edit `briefs/<video-name>.md`."

Claude reads `CLAUDE.md` for standing rules and writes an edit log to `edit-logs/` when done.

Video, audio, image and Resolve files are never committed.
