"""Build a HyperFrames short-form composition in the styles/reel-2.md look.

Usage: python3 scripts/build_reel.py <plan.json>

The plan lists cuts from source footage plus how each one looks. This script
pre-cuts every clip with ffmpeg (looks like duotone are baked in, so renders are
seek-safe), joins the voice audio, times captions from the word transcript and
writes index.html into the plan's HyperFrames project.

Plan keys:
  project      HyperFrames project dir (index.html is written here)
  source       default footage file
  transcript   faster-whisper JSON from scripts/transcribe.py (for `source`)
  keywords     words shown alone in orange
  clips[]      {in, out, look, zoom, x, y, caps, wipe, src, audio}
    look: speaker | red | black | bw | broll | card
    caps: single | phrase | stack | keys (keywords only) | none
  fix          {"HEARD": "MEANT"} caption word corrections
    wipe: true puts the red ink wipe on the cut into this clip
    src/audio: other footage for b-roll; audio "source" keeps the voice from
               `source` at in/out, "none" leaves the clip silent (default source)
"""
import json, math, os, re, subprocess, sys

W, H, FPS = 1080, 1920, 30
ORANGE = "linear-gradient(180deg,#FFC229 0%,#FF7A00 55%,#FF5A00 100%)"
LOOKS = {
    # baked into the clip file
    "speaker": "",
    "broll": "",
    "card": "",
    "bw": "hue=s=0,eq=contrast=1.25:brightness=-0.03,",
    "black": "hue=s=0,eq=brightness=-0.32:contrast=0.9,",
    "red": "format=gray,format=rgb24,lutrgb=r='lerp(110,255,val/255)':g='lerp(4,214,val/255)':b='lerp(2,120,val/255)',",
}


def sh(*cmd):
    subprocess.run(cmd, check=True)


def clean(w):
    return re.sub(r"[^\w'’%$-]", "", w).upper()


def rough_edge(n, amp, seed):
    """Deterministic jagged offsets for torn/ink edges."""
    out = []
    for i in range(n + 1):
        t = i / n
        v = sum(math.sin(t * f * 2 * math.pi + seed * k) / f for k, f in enumerate((3, 7, 13, 29, 53), 1))
        out.append(v * amp)
    return out


def ink_band_path():
    """A wide band with torn leading/trailing edges, centred on 0,0, moving along (-1, 1)/√2."""
    D = math.hypot(W / 2, H / 2)
    L, P, n = 2.4 * D, 1.3 * D, 60
    a = math.sqrt(0.5)
    m, p = (-a, a), (a, a)
    lead, trail = rough_edge(n, 0.09 * D, 1.7), rough_edge(n, 0.09 * D, 4.1)
    pts = []
    for i in range(n + 1):
        v = -P + 2 * P * i / n
        u = L / 2 + lead[i]
        pts.append((u * m[0] + v * p[0], u * m[1] + v * p[1]))
    for i in range(n, -1, -1):
        v = -P + 2 * P * i / n
        u = -L / 2 + trail[i]
        pts.append((u * m[0] + v * p[0], u * m[1] + v * p[1]))
    return "M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in pts) + "Z", L / 2 + D + 0.1 * D


def torn_corner_path(corner):
    """Black torn shape for a corner of red beats (tl or br)."""
    n, edge = 30, rough_edge(30, 40, 2.3 if corner == "tl" else 5.9)
    pts = [(0, 0)]
    for i in range(n + 1):
        t = i / n
        x, y = 520 * (1 - t), 360 * t
        pts.append((x + edge[i], y + edge[i] * 0.6))
    pts.append((0, 360))
    if corner == "br":
        pts = [(W - x, H - y) for x, y in pts]
    return "M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in pts) + "Z"


def main(plan_path):
    plan = json.load(open(plan_path))
    proj = plan["project"]
    clips_dir = os.path.join(proj, "assets", "clips")
    os.makedirs(clips_dir, exist_ok=True)
    words = [w for seg in json.load(open(plan["transcript"])) for w in seg["words"]]
    keywords = {k.upper() for k in plan.get("keywords", [])}

    # 1. cut clips and voice
    t, timeline, audio_parts = 0.0, [], []
    for i, c in enumerate(plan["clips"]):
        src = c.get("src", plan["source"])
        dur = round((c["out"] - c["in"]) * FPS) / FPS
        name = f"c{i:02d}.mp4"
        vf = (LOOKS[c.get("look", "speaker")] +
              f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},format=yuv420p")
        sh("ffmpeg", "-v", "error", "-y", "-ss", f"{c['in']:.3f}", "-i", src, "-t", f"{dur:.3f}",
           "-vf", vf, "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", os.path.join(clips_dir, name))
        # voice comes from `source`; b-roll from other files needs audio_in to keep the voice running
        a_in = c.get("audio_in", None if c.get("src") else c["in"])
        silent = c.get("audio") == "none" or a_in is None
        audio_parts.append((None if silent else plan["source"], a_in or 0, dur))
        timeline.append(dict(c, file=name, start=round(t, 4), dur=dur, idx=i))
        t += dur
    total = round(t, 4)

    parts, filt = [], []
    for k, (a_src, a_in, dur) in enumerate(audio_parts):
        if a_src:
            parts += ["-ss", f"{a_in:.3f}", "-t", f"{dur:.3f}", "-i", a_src]
            filt.append(f"[{len(filt)}:a]aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.01,afade=t=out:st={dur-0.012:.3f}:d=0.012[a{k}]")
        else:
            parts += ["-f", "lavfi", "-t", f"{dur:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
            filt.append(f"[{len(filt)}:a]anull[a{k}]")
    labels = "".join(f"[a{k}]" for k in range(len(audio_parts)))
    filt.append(f"{labels}concat=n={len(audio_parts)}:v=0:a=1,loudnorm=I=-14:TP=-1.5:LRA=11[out]")
    sh("ffmpeg", "-v", "error", "-y", *parts, "-filter_complex", ";".join(filt), "-map", "[out]",
       "-ar", "48000", os.path.join(proj, "assets", "voice.wav"))

    # 2. captions: one timed block per caption state
    caps = []

    def add(start, end, html, pos):
        if end - start >= 1 / FPS:
            caps.append((round(start, 4), round(end - start, 4), html, pos))

    def span(w, cls):
        return f'<span class="{cls}">{w}</span>'

    for c in timeline:
        mode = c.get("caps", "phrase")
        if mode == "none" or (c.get("src") and "audio_in" not in c):
            continue
        a_in = c.get("audio_in", c["in"])
        ws = [(clean(w["w"]), w["s"] - a_in + c["start"], w["e"] - a_in + c["start"])
              for w in words if a_in - 0.05 <= w["s"] < a_in + c["dur"] - 0.05]
        merged = []
        for w in ws:
            if w[0] in ("%", "") and merged:
                merged[-1] = (merged[-1][0] + w[0], merged[-1][1], w[2])
            elif w[0]:
                merged.append(w)
        ws = [(plan.get("fix", {}).get(w, w), s, e) for w, s, e in merged]
        end_of_clip = c["start"] + c["dur"]
        pos = "mid" if c.get("look") in ("black", "bw", "broll") else "chest"
        starts = [w[1] for w in ws] + [end_of_clip]
        if mode == "keys":
            for j, (w, s, e) in enumerate(ws):
                if w in keywords:
                    add(max(s, c["start"]), min(starts[j + 1], end_of_clip), span(w, "big o"), pos)
        elif mode == "single":
            for j, (w, s, e) in enumerate(ws):
                add(max(s, c["start"]), min(starts[j + 1], end_of_clip), span(w, "big o"), pos)
        elif mode == "stack":
            n = len(ws)
            cut1, cut2 = max(1, n // 3), max(2, 2 * n // 3)
            for j in range(n):
                lines = []
                for lo, hi, cls in ((0, cut1, "sm w"), (cut1, cut2, "lg w"), (cut2, n, "md o")):
                    seg = [ws[k][0] for k in range(lo, min(hi, j + 1))]
                    if seg:
                        lines.append(f'<div class="line">{span(" ".join(seg), cls)}</div>')
                add(max(ws[j][1], c["start"]), min(starts[j + 1], end_of_clip), "".join(lines), "mid")
        else:  # phrase: build up to 3 words, keywords alone in orange
            phrase = []
            for j, (w, s, e) in enumerate(ws):
                stop = min(starts[j + 1], end_of_clip)
                if w in keywords:
                    phrase = []
                    add(max(s, c["start"]), stop, span(w, "big o"), pos)
                    continue
                if len(phrase) >= 3:
                    phrase = []
                phrase.append(w)
                add(max(s, c["start"]), stop, span(" ".join(phrase), "md w"), pos)

    # 3. html
    band, travel = ink_band_path()
    el, js = [], []
    for c in timeline:
        look = c.get("look", "speaker")
        z, x, y = c.get("zoom", 1.0), c.get("x", 0), c.get("y", 0)
        cid = f"v{c['idx']:02d}"
        timing = f'data-start="{c["start"]}" data-duration="{c["dur"]}"'
        if look in ("red", "card"):
            bg = "#E3170A" if look == "red" else "#000"
            el.append(f'<div id="bg{c["idx"]:02d}" class="clip bg" {timing} style="background:{bg}"></div>')
            # zoom inside the card by cropping the picture, so the card itself keeps its size
            ins = (1 - 1 / z) * 50
            el.append(f'<video id="{cid}" class="clip card" src="assets/clips/{c["file"]}" {timing} data-media-start="0" '
                      f'muted playsinline style="object-view-box:inset({ins - y / 19.2:.2f}% {ins - x / 10.8:.2f}% {ins + y / 19.2:.2f}% {ins + x / 10.8:.2f}%)"></video>')
            if look == "red":
                el.append(f'<svg id="torn{c["idx"]:02d}" class="clip torn" {timing} viewBox="0 0 {W} {H}"><path d="{torn_corner_path("tl")}"/>'
                          f'<path d="{torn_corner_path("br")}"/></svg>')
        else:
            el.append(f'<video id="{cid}" class="clip full" src="assets/clips/{c["file"]}" {timing} data-media-start="0" '
                      f'muted playsinline style="transform:scale({z}) translate({x}px,{y}px)"></video>')
    for i, c in enumerate(timeline):
        if c.get("wipe") and i:
            w0 = round(c["start"] - 3 / FPS, 4)
            wid = f"ink{i:02d}"
            el.append(f'<svg id="{wid}" class="clip ink" data-start="{w0}" data-duration="{round(6 / FPS, 4)}" '
                      f'viewBox="{-W/2} {-H/2} {W} {H}"><g class="band"><path d="{band}"/></g></svg>')
            k = travel * math.sqrt(0.5)
            js.append(f'tl.fromTo("#{wid} .band",{{x:{k:.0f},y:{-k:.0f}}},{{x:{-k:.0f},y:{k:.0f},duration:{6/FPS:.4f},ease:"none"}},{w0});')
    el.append(f'<div id="vignette" class="clip vignette" data-start="0" data-duration="{total}"></div>')
    for k, (s, d, html, pos) in enumerate(caps):
        el.append(f'<div id="cap{k:03d}" class="clip cap {pos}" data-start="{s}" data-duration="{d}"><div class="capin">{html}</div></div>')
    el.append(f'<audio id="voice" src="assets/voice.wav" data-start="0" data-duration="{total}" data-has-audio="true"></audio>')

    page = f"""<!doctype html>
<html lang="en" data-resolution="portrait">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width={W}, height={H}" />
<script src="assets/gsap.min.js"></script>
<style>
@font-face {{ font-family: "Mont"; src: url("assets/montserrat-latin-900-normal.woff2") format("woff2"); font-weight: 900; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #000; }}
#root {{ position: relative; width: {W}px; height: {H}px; overflow: hidden; background: #000; }}
.clip {{ position: absolute; inset: 0; width: {W}px; height: {H}px; }}
video.full {{ object-fit: cover; transform-origin: 50% 40%; }}
video.card {{ left: 54px; top: 115px; width: 972px; height: 1690px; object-fit: cover; border-radius: 44px; }}
.torn path {{ fill: #000; }}
.ink {{ z-index: 50; overflow: visible; }}
.ink path {{ fill: #E3170A; }}
.vignette {{ z-index: 40; background: radial-gradient(ellipse 75% 62% at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,.55) 85%, rgba(0,0,0,.85) 100%); }}
.cap {{ z-index: 60; display: flex; justify-content: center; align-items: center; }}
.cap.chest {{ align-items: flex-start; padding-top: 1080px; }}
.capin {{ text-align: center; font-family: "Mont", sans-serif; font-weight: 900; text-transform: uppercase;
  letter-spacing: -0.035em; line-height: 0.95; filter: drop-shadow(0 6px 14px rgba(0,0,0,.65)); max-width: 960px; }}
.capin .line {{ display: block; }}
.w {{ color: #fff; }}
.o {{ background: {ORANGE}; -webkit-background-clip: text; background-clip: text; color: transparent; }}
.sm {{ font-size: 64px; }} .md {{ font-size: 92px; }} .lg {{ font-size: 140px; }} .big {{ font-size: 150px; }}
.bg {{ z-index: 0; }}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="{W}" data-height="{H}">
{chr(10).join(el)}
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
window.__timelines["main"] = tl;
tl.seek(0);
</script>
</body>
</html>
"""
    open(os.path.join(proj, "index.html"), "w").write(page)
    print(f"{len(timeline)} clips, {len(caps)} caption states, {total:.2f}s")


if __name__ == "__main__":
    main(sys.argv[1])
