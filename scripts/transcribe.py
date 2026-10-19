"""Word-level transcript with faster-whisper.
Usage: python3 scripts/transcribe.py <audio_or_video> <out.json> [model]
"""
import json, sys
from faster_whisper import WhisperModel

src, out = sys.argv[1], sys.argv[2]
model = WhisperModel(sys.argv[3] if len(sys.argv) > 3 else "small.en", device="cpu", compute_type="int8")
audio = src
if src.endswith(".wav"):
    # 16 kHz mono PCM; bypasses PyAV, whose newer releases break faster-whisper's decoder
    import wave, numpy as np
    with wave.open(src) as w:
        audio = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
segments, _ = model.transcribe(audio, word_timestamps=True, vad_filter=True, beam_size=5)
data = []
for s in segments:
    data.append({"start": s.start, "end": s.end, "text": s.text.strip(),
                 "words": [{"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)} for w in s.words]})
    print(f"[{s.start:7.2f}-{s.end:7.2f}] {s.text.strip()}", flush=True)
json.dump(data, open(out, "w"), indent=1)
