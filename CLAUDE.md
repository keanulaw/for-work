# CLAUDE.md

## Purpose
Edit any video I bring (any length, type or aspect ratio), working in invideo's timeline editor over MCP. This repo holds briefs, styles, prompts, scripts, notes and edit logs. Edits themselves happen in invideo.

In Claude Code use the full `invideo` MCP server (`mcp__invideo__*`). `invideo_Editor` is meant for the Claude apps only.

## Before editing
- Read the brief in `briefs/` and any style preset it names in `styles/`.
- If length, aspect ratio or style is missing, ask me once in a single short message, then proceed.
- Check `notes/` for known limits and bugs.

## Free plan (tested 2026-10-19)
- 1080p upload and export work. No watermark.
- DaVinci Resolve project export available.
- Export caps: not yet known.
- Log any limit hit in `notes/invideo-free-plan.md`.

## Usage rules
I'm on Claude Pro with limited usage.
- Find moments from audio/transcript where possible, not frame-by-frame.
- Keep frame grabs to the minimum needed.
- No AI generation (b-roll, images, music, voice) unless the brief asks for it. It may use invideo credits.
- One export per version.
- If a tool call fails, retry once, then stop and report.

## Workflow
1. Brief: read `briefs/<name>.md`.
2. Upload: source to invideo (use `scripts/` to trim/compress first if needed).
3. Review: transcript/audio first, frames only if needed.
4. Edit on the timeline.
5. Export 1080p video (+ DaVinci Resolve project if the brief asks).
6. Edit log: copy `edit-logs/_template.md` to `edit-logs/<name>.md` and fill it.

## Style
Keep replies short. Don't explain every step.
