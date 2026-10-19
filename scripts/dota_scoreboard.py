"""OCR the Dota 2 top-bar score and clock from frame crops.
Usage: python3 scripts/dota_scoreboard.py <crop_dir> <step_seconds> <out.json>
Crops are 200x45 px of the 1080p top bar (x 860-1060): radiant kills, clock, dire kills.
"""
import json, os, re, sys
import cv2
from rapidocr_onnxruntime import RapidOCR

crop_dir, step, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
ocr = RapidOCR()
rows = []
for i, f in enumerate(sorted(os.listdir(crop_dir))):
    res, _ = ocr(cv2.imread(os.path.join(crop_dir, f)))
    row = {"t": i * step}
    for box, text, _conf in res or []:
        x = box[0][0]
        if re.fullmatch(r"-?\d{1,2}:\d\d", text):
            row["clock"] = text
        elif text.isdigit():
            row["radiant" if x < 80 else "dire"] = int(text)
    rows.append(row)
json.dump(rows, open(out, "w"))
print(len(rows), "frames")
