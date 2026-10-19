"""Build a 16:9 meme-style gameplay edit (Rizpol-like) as a HyperFrames composition.

Usage: python3 scripts/build_meme.py <plan.json>

Plan keys:
  project       HyperFrames project dir
  source        gameplay recording
  audio_stream  which audio stream of `source` to use (default 0, the full mix)
  sfx_dir       folder of WAVs from scripts/meme_sfx.py
  items[]       played in order, each one of:
    {"clip": [in, out], "speed": 1, "zoom": [[at, scale, x%, y%, dur], ...],
     "shake": [[at, dur]], "text": [[at, dur, "TEXT", "top|bottom|mid|small"]],
     "emoji": [[at, dur, "💀", x%, y%]], "sfx": [[at, "vine_boom", gain]], "game_gain": 1}
    {"freeze": t, "dur": 1.5, "zoom": 1.3, "x": 50, "y": 45, "text": [...], "emoji": [...], "sfx": [...]}
    {"card": ["LINE 1", "LINE 2"], "dur": 2, "sfx": [...], "bg": "#000"}
  Times inside an item are relative to the item's start on the output timeline.
"""
import json, os, subprocess, sys

W, H, FPS = 1920, 1080, 30


def sh(*cmd):
    subprocess.run(cmd, check=True)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main(plan_path):
    plan = json.load(open(plan_path))
    proj = plan["project"]
    src = plan["source"]
    astream = plan.get("audio_stream", 0)
    cdir = os.path.join(proj, "assets", "clips")
    os.makedirs(cdir, exist_ok=True)

    t, items, a_inputs, a_filters, sfx_events = 0.0, [], [], [], []

    def add_audio_input(args, filt):
        a_inputs.extend(args)
        k = len(a_filters)
        a_filters.append(filt.format(i=k, o=f"s{k}"))

    for n, it in enumerate(plan["items"]):
        it = dict(it, idx=n, start=round(t, 4))
        if "clip" in it:
            a, b = it["clip"]
            sp = it.get("speed", 1)
            dur = round((b - a) / sp * FPS) / FPS
            name = f"i{n:03d}.mp4"
            vf = f"setpts=PTS/{sp},fps={FPS},scale={W}:{H},format=yuv420p"
            sh("ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", src, "-vf", vf,
               "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", os.path.join(cdir, name))
            atempo = f"atempo={sp}," if sp >= 0.5 else f"atempo=0.5,atempo={sp / 0.5},"
            gain = it.get("game_gain", 1)
            add_audio_input(["-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", src],
                            f"[{{i}}:a:{astream}]{atempo}aresample=48000,aformat=channel_layouts=stereo,volume={gain},"
                            f"afade=t=in:d=0.02,afade=t=out:st={max(0, dur - 0.03):.3f}:d=0.03,apad,atrim=0:{dur:.3f}[{{o}}]")
            it.update(file=name, dur=dur)
        elif "freeze" in it:
            dur = it.get("dur", 1.5)
            name = f"i{n:03d}.png"
            sh("ffmpeg", "-v", "error", "-y", "-ss", f"{it['freeze']:.3f}", "-i", src, "-frames:v", "1",
               "-vf", f"scale={W}:{H}", os.path.join(cdir, name))
            add_audio_input(["-f", "lavfi", "-t", f"{dur:.3f}", "-i", "anullsrc=r=48000:cl=stereo"], "[{i}:a]anull[{o}]")
            it.update(file=name, dur=dur)
        else:
            dur = it.get("dur", 2)
            add_audio_input(["-f", "lavfi", "-t", f"{dur:.3f}", "-i", "anullsrc=r=48000:cl=stereo"], "[{i}:a]anull[{o}]")
            it.update(dur=dur)
        for at, name, *g in it.get("sfx", []):
            sfx_events.append((it["start"] + at, name, g[0] if g else 1.0))
        items.append(it)
        t += it["dur"]
    total = round(t, 4)

    # audio: concat game audio, then lay the SFX on top
    nseg = len(a_filters)
    filt = a_filters + ["".join(f"[s{k}]" for k in range(nseg)) + f"concat=n={nseg}:v=0:a=1[game]"]
    sfx_inputs, mix = [], ["[game]"]
    for j, (at, name, g) in enumerate(sfx_events):
        sfx_inputs += ["-i", os.path.join(plan["sfx_dir"], name + ".wav")]
        k = nseg + j
        ms = int(at * 1000)
        filt.append(f"[{k}:a]volume={g},adelay={ms}|{ms}[x{j}]")
        mix.append(f"[x{j}]")
    filt.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=first,"
                f"alimiter=limit=0.95,loudnorm=I=-14:TP=-1.5:LRA=11[out]")
    sh("ffmpeg", "-v", "error", "-y", *a_inputs, *sfx_inputs, "-filter_complex", ";".join(filt),
       "-map", "[out]", "-ar", "48000", "-t", f"{total:.3f}", os.path.join(proj, "assets", "mix.wav"))

    # html
    el, js = [], []
    shake_seq = [(9, -6), (-8, 5), (6, 8), (-5, -7), (7, -4), (-9, 3), (4, 6), (0, 0)]
    for it in items:
        s, d, n = it["start"], it["dur"], it["idx"]
        timing = f'data-start="{s}" data-duration="{d}"'
        if "clip" in it:
            el.append(f'<video id="v{n:03d}" class="clip media" src="assets/clips/{it["file"]}" {timing} data-media-start="0" muted playsinline></video>')
            target = f"#v{n:03d}"
        elif "freeze" in it:
            z, x, y = it.get("zoom", 1.25), it.get("x", 50), it.get("y", 45)
            el.append(f'<img id="v{n:03d}" class="clip media" src="assets/clips/{it["file"]}" {timing} '
                      f'style="transform-origin:{x}% {y}%" />')
            target = f"#v{n:03d}"
            # freeze punches in hard on the first frame, then creeps
            js.append(f'tl.fromTo("{target}",{{scale:1}},{{scale:{z},duration:0.12,ease:"power3.out"}},{s});')
            js.append(f'tl.to("{target}",{{scale:{z * 1.06:.3f},duration:{max(0.1, d - 0.12):.3f},ease:"none"}},{s + 0.12:.4f});')
            el.append(f'<div id="fz{n:03d}" class="clip freezetint" {timing}></div>')
        else:
            lines = "".join(f'<div class="cardline l{k}">{esc(x)}</div>' for k, x in enumerate(it["card"]))
            el.append(f'<div id="card{n:03d}" class="clip card" {timing} style="background:{it.get("bg", "#000")}">{lines}</div>')
            js.append(f'tl.fromTo("#card{n:03d} .cardline",{{scale:1.6,opacity:0}},{{scale:1,opacity:1,duration:0.18,ease:"back.out(2)",stagger:0.12}},{s});')
            target = None
        for k, (at, zs, x, y, zd) in enumerate(it.get("zoom", []) if "clip" in it else []):
            js.append(f'tl.set("{target}",{{transformOrigin:"{x}% {y}%"}},{s + at:.4f});')
            js.append(f'tl.to("{target}",{{scale:{zs},duration:{zd},ease:"power3.out"}},{s + at:.4f});')
        for at, sd in it.get("shake", []):
            step = sd / len(shake_seq)
            for k, (dx, dy) in enumerate(shake_seq):
                js.append(f'tl.to("{target}",{{x:{dx},y:{dy},duration:{step:.4f},ease:"none"}},{s + at + k * step:.4f});')
        for k, (at, td, text, pos) in enumerate(it.get("text", [])):
            tid = f"t{n:03d}_{k}"
            el.append(f'<div id="{tid}" class="clip meme {pos}" data-start="{s + at:.4f}" data-duration="{td}"><span>{esc(text)}</span></div>')
            js.append(f'tl.fromTo("#{tid} span",{{scale:1.8,rotation:-4}},{{scale:1,rotation:0,duration:0.16,ease:"back.out(2.5)"}},{s + at:.4f});')
        for k, (at, ed, ch, x, y) in enumerate(it.get("emoji", [])):
            eid = f"e{n:03d}_{k}"
            el.append(f'<div id="{eid}" class="clip emoji" data-start="{s + at:.4f}" data-duration="{ed}"><span style="left:{x}%;top:{y}%">{ch}</span></div>')
            js.append(f'tl.fromTo("#{eid} span",{{scale:0,rotation:-25}},{{scale:1,rotation:0,duration:0.22,ease:"back.out(3)"}},{s + at:.4f});')
    el.append(f'<audio id="mix" src="assets/mix.wav" data-start="0" data-duration="{total}" data-has-audio="true"></audio>')

    page = f"""<!doctype html>
<html lang="en" data-resolution="landscape">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width={W}, height={H}" />
<script src="assets/gsap.min.js"></script>
<style>
@font-face {{ font-family: "Anton"; src: url("assets/anton-latin-400-normal.woff2") format("woff2"); }}
@font-face {{ font-family: "Mont"; src: url("assets/montserrat-latin-900-normal.woff2") format("woff2"); font-weight: 900; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #000; }}
#root {{ position: relative; width: {W}px; height: {H}px; overflow: hidden; background: #000; }}
.clip {{ position: absolute; inset: 0; width: {W}px; height: {H}px; }}
.media {{ object-fit: cover; }}
.freezetint {{ z-index: 5; background: radial-gradient(ellipse at center, rgba(0,0,0,0) 45%, rgba(0,0,0,.55) 100%); }}
.card {{ z-index: 30; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px; }}
.cardline {{ font-family: "Mont", sans-serif; font-weight: 900; color: #fff; text-transform: uppercase; font-size: 120px;
  letter-spacing: -0.02em; text-align: center; line-height: 1; }}
.cardline.l1 {{ font-size: 76px; color: #FFD400; }}
.cardline.l2 {{ font-size: 56px; color: #ccc; }}
.meme {{ z-index: 40; display: flex; justify-content: center; pointer-events: none; }}
.meme span {{ display: inline-block; font-family: "Anton", Impact, sans-serif; color: #fff; text-transform: uppercase;
  font-size: 104px; line-height: 1.02; text-align: center; max-width: 1700px;
  -webkit-text-stroke: 7px #000; paint-order: stroke fill; text-shadow: 0 6px 0 #000; }}
.meme.top {{ align-items: flex-start; padding-top: 40px; }}
.meme.bottom {{ align-items: flex-end; padding-bottom: 150px; }}
.meme.mid {{ align-items: center; }}
.meme.small {{ align-items: flex-start; padding-top: 40px; }}
.meme.small span {{ font-size: 64px; -webkit-text-stroke: 5px #000; }}
.meme.yellow span {{ color: #FFD400; }}
.emoji {{ z-index: 45; }}
.emoji span {{ position: absolute; font-size: 220px; line-height: 1; transform-origin: 50% 50%;
  font-family: "Noto Color Emoji", sans-serif; margin-left: -110px; margin-top: -110px; }}
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
    print(f"{len(items)} items, {len(sfx_events)} sfx, {total:.1f}s ({total / 60:.1f} min)")


if __name__ == "__main__":
    main(sys.argv[1])
