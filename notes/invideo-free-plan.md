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
