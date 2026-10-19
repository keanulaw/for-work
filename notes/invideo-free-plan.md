# invideo free plan

## Tested 2026-10-19
- 1080p upload: works
- 1080p export: works, no watermark
- DaVinci Resolve project export: available

## Export caps
_Not yet known._

## Upload size / length limits

## Resolve export quality
### Relinking

### Captions

## Known bugs
- 2026-10-19: media_grab / media_filmstrip return frame URLs on `s3-pro-uploads.invideo.io`, which this cloud session's network blocks. Only `read` on a sequence shows an image (a small 3x3 sheet). Workaround: put the clip on a scratch timeline and use `capture` (returns full frames inline, up to 12 per call).
- 2026-10-19: No transcription tool in invideo MCP (find_models has none). add_captions needs your own text and timings.
- 2026-10-19: `capture` returns render_failed on big batches that include custom-transition frames, and on any frame of a custom transition whose left clip is disabled. Capture 2–3 frames at a time; don't disable clips next to custom transitions.

## Cloud session network (not invideo)
- Drive downloads need `drive.google.com` + `drive.usercontent.google.com` allowed. Takes effect without a new session.
- Hugging Face model downloads also need `*.hf.co` (files come from `us.aws.cdn.hf.co` / `cas-server.xethub.hf.co`).
