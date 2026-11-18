"""Turn failed QC checks (automated + visual) into a retry prompt amendment.
Usage: python tools/diagnose.py <attempt_stem>   e.g. CP-001_rotary_telephone_a01
Reads qc/<stem>.auto_qc.json and qc/<stem>.visual_review.json, prints the amendment text
and the decision: RETRY (attempts left) or ESCALATE (budget used up). Never auto-accepts a failure.
"""
import sys, json, re
from pathlib import Path

FIX = {
    "safe_margin": "Shrink the whole drawing so there is a wide empty white margin (about 8% of the page) on all four sides; nothing may come close to any edge.",
    "not_cropped": "The drawing touches or leaves the frame. Make the whole object smaller and fully inside the frame.",
    "no_stray_grey": "Use pure black lines on pure white only. No grey tones, shading, soft edges or fills.",
    "white_background": "Background must be pure white with no tint, texture or paper effect.",
    "no_tiny_regions": "Remove tiny specks, dots and very small enclosed shapes. Every enclosed area must be big enough to colour with a thick marker.",
    "stroke_thick_enough": "Make the outlines thicker and bold.",
    "stroke_consistent": "Use one single uniform line thickness everywhere; no thin hairlines.",
    "dial_has_10_holes": "The dial must have exactly 10 equal round finger holes evenly spaced in a ring around a centre disc.",
    "enough_regions": "Show every component from the structure list as its own clearly separated enclosed shape.",
}
VISUAL = {
    "stray_marks": "Do not draw any stray lines, tick marks, hooks or flourishes that are not part of an object component. In particular delete the two small curved hook lines above the handset ends; the handset outline must be a clean closed shape with nothing sticking out of it.",
    "handset_cradle_overlap": "Draw the handset resting on top of the cradle with its two ends clearly sitting above the cradle prongs; no outlines crossing through each other, every part fully separated by white space.",
}

stem = sys.argv[1]
root = Path(__file__).resolve().parent.parent
auto = json.loads((root / "qc" / f"{stem}.auto_qc.json").read_text(encoding="utf-8"))
vis_p = root / "qc" / f"{stem}.visual_review.json"
vis = json.loads(vis_p.read_text(encoding="utf-8")) if vis_p.exists() else {"findings": []}
fixes = [FIX[k] for k in auto.get("failed", []) if k in FIX]
fixes += [VISUAL[f["id"]] for f in vis["findings"] if f["severity"] == "fail" and f["id"] in VISUAL]
fixes += [f["note"] for f in vis["findings"] if f["severity"] == "fail" and f["id"] not in VISUAL]
fixes = list(dict.fromkeys(fixes))
n = int(re.search(r"_a(\d+)$", stem).group(1))
max_attempts = json.loads((root / "specs" / "CP-001.json").read_text(encoding="utf-8"))["retry_policy"]["max_attempts_per_image"]
if not fixes:
    print("DECISION: NO FAILURES - eligible for accept (owner still approves the set)")
elif n >= max_attempts:
    print(f"DECISION: ESCALATE - attempt {n}/{max_attempts} used, unresolved: {fixes}")
else:
    print(f"DECISION: RETRY (attempt {n+1} of {max_attempts})")
    print("AMENDMENT:\nRedo the same image with these corrections, keeping everything else the same. " + " ".join(fixes))
