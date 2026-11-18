"""Build everything for the collection from specs/CP-001.json accepted attempts:
 1. print files (Letter + A4 PNG/PDF) for any object missing them
 2. one manifest per object (attempt history from qc/ files)
 3. collection-level QC (stroke weight consistency, size consistency) -> qc/CP-001_collection_qc.json
 4. combined PDFs: pages_final/CP-001_<format>_20_pages.pdf
Usage: python tools/build_collection.py
"""
import json, subprocess, sys, hashlib
from pathlib import Path
import numpy as np, cv2
from scipy import ndimage as ndi
import pymupdf

root = Path(__file__).resolve().parent.parent
spec = json.loads((root / "specs" / "CP-001.json").read_text(encoding="utf-8"))
rows = []
for o in spec["objects"]:
    oid, att = o["id"], o["accepted_attempt"]
    stem = f"CP-001_{oid}"
    raw = root / "raw_from_chatgpt" / f"{stem}_{att}.png"
    for fmt in ("US_LETTER", "A4"):
        if not (root / "pages_final" / fmt / f"{stem}.png").exists():
            subprocess.run([sys.executable, str(root / "tools" / "make_print.py"), str(raw), stem], check=True, capture_output=True)
    # manifest
    attempts = []
    for f in sorted((root / "raw_from_chatgpt").glob(f"{stem}_a*.png")):
        n = int(f.stem.split("_a")[-1]); base = f.stem
        auto = json.loads((root / "qc" / f"{base}.auto_qc.json").read_text(encoding="utf-8"))
        vis_p = root / "qc" / f"{base}.visual_review.json"
        vis = json.loads(vis_p.read_text(encoding="utf-8")) if vis_p.exists() else {}
        attempts.append({"n": n, "file": f"raw_from_chatgpt/{f.name}", "sha256_16": hashlib.sha256(f.read_bytes()).hexdigest()[:16],
                         "auto_failed": auto.get("failed", []), "visual_verdict": vis.get("verdict"),
                         "visual_warnings": [x["note"] for x in vis.get("findings", []) if x["severity"] == "warn"],
                         "accepted": f.name == raw.name})
    pq = json.loads((root / "qc" / f"{stem}.print_qc.json").read_text(encoding="utf-8"))
    man = {"product_id": "CP-001", "object_id": oid, "name": o["name"],
           "status": "MASTER_APPROVED" if oid == "rotary_telephone" else "QC_PASSED_PENDING_OWNER",
           "human_approved": oid == "rotary_telephone", "attempts": attempts,
           "retry_budget": {"used": len(attempts), "max": spec["retry_policy"]["max_attempts_per_image"]},
           "print": {k: {"png": v["png"].replace(str(root) + "\\", "").replace("\\", "/"), "dims_check": v["dims_check"]["detail"],
                         "dims_pass": v["dims_check"]["pass"], "pure_black_white": v["pure_black_white"],
                         "auto_qc_passed": v["automated_qc_passed"], "margin_ok": v["margin_ok"], "stroke": pq.get("stroke_normalised", {}).get(k)} for k, v in pq["formats"].items()},
           "pinholes_filled": pq.get("pinholes_filled", 0),
           "caveat": "Interpolated enlargement of ~1100x1450 source; geometry verdicts are subjective visual judgment."}
    (root / "manifests" / f"{stem}.json").write_text(json.dumps(man, indent=2), encoding="utf-8")
    # collection metrics from the Letter print
    g = cv2.imread(str(root / "pages_final" / "US_LETTER" / f"{stem}.png"), 0)
    ink = g < 128
    dt = ndi.distance_transform_edt(ink)
    ridge = ink & (dt >= ndi.maximum_filter(dt, size=3)) & (dt > 0.7)
    ys, xs = np.where(ink)
    rows.append({"object": oid, "median_stroke_px": round(float(np.median(2 * dt[ridge])), 1), "ink_fraction": round(float(ink.mean()), 4),
                 "object_width_frac": round(float((xs.max() - xs.min()) / g.shape[1]), 3), "attempts": len(attempts)})
med = np.array([r["median_stroke_px"] for r in rows]); m = float(np.median(med))
for r in rows:
    r["stroke_vs_median"] = round(r["median_stroke_px"] / m, 2)
    r["stroke_outlier"] = bool(abs(r["stroke_vs_median"] - 1) > 0.35)
report = {"method": "automated", "median_of_medians_px": round(m, 1), "outlier_rule": "median stroke differs from collection median by >35%",
          "pages": rows, "outliers": [r["object"] for r in rows if r["stroke_outlier"]],
          "note": "Stroke is measured on Letter prints where each object is scaled to fit its own box, so stroke differs with object size; large differences mean visibly different line weight on the page."}
(root / "qc" / "CP-001_collection_qc.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
# combined PDFs
for fmt in ("US_LETTER", "A4"):
    out = pymupdf.open()
    for o in spec["objects"]:
        out.insert_pdf(pymupdf.open(root / "pages_final" / fmt / f"CP-001_{o['id']}.pdf"))
    out.save(root / "pages_final" / f"CP-001_{fmt}_20_pages.pdf")
    print(fmt, "pages", len(out))
print("outliers:", report["outliers"])
for r in rows:
    print(r["object"].ljust(16), r["median_stroke_px"], r["stroke_vs_median"], r["object_width_frac"], "attempts", r["attempts"], "OUTLIER" if r["stroke_outlier"] else "")
