"""Programmatic QC for coloring-page line art. AUTOMATED checks only.
Subjective/structural judgments (overlaps, recognisable parts) are NOT decided here;
they are recorded separately as method="visual_judgment" in the QC report.

Usage: python tools/qc_lineart.py <image.png> [--spec specs/CP-001.json --object rotary_telephone]
Writes <image>.qc.json next to qc/ output and prints a summary. Exit code 0 = all automated checks pass.
"""
import sys, json, argparse
from pathlib import Path
import numpy as np, cv2
from scipy import ndimage as ndi

T = dict(  # thresholds (tunable, versioned with the report)
    ink_thresh=128,
    min_margin_frac=0.04,      # ink must stay this far from every edge
    edge_touch_px=2,           # ink within this of an edge = cropped
    max_stray_grey_frac=0.0005,  # grey pixels away from any ink edge, fraction of image
    bg_white_min=0.97,         # fraction of non-ink area that is near white
    min_region_frac=0.0004,    # an enclosed region smaller than this is a speck / too small to colour
    thin_line_ratio=0.5,       # stroke narrower than ratio*median counts as thin
    max_thin_frac=0.20,
    min_median_stroke_frac=0.0025,
)


def analyse(path, expect=None):
    g = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    h, w = g.shape
    res = {"image": str(path), "pixels": [w, h], "checks": {}, "metrics": {}}
    ink = g < T["ink_thresh"]
    ink_frac = float(ink.mean())
    res["metrics"]["ink_fraction"] = round(ink_frac, 4)

    def chk(name, ok, detail):
        res["checks"][name] = {"pass": bool(ok), "method": "automated", "detail": detail}

    # 1 background / grey shading
    near_ink = cv2.dilate(ink.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
    mid = (g >= 60) & (g <= 200)
    stray = mid & ~near_ink
    stray_frac = float(stray.mean())
    chk("no_stray_grey", stray_frac <= T["max_stray_grey_frac"], f"stray grey fraction {stray_frac:.5f}")
    nonink = ~ink
    white_frac = float((g[nonink] > 235).mean()) if nonink.any() else 0
    chk("white_background", white_frac >= T["bg_white_min"], f"near-white share of non-ink {white_frac:.4f}")

    # 2 cropping / margins
    ys, xs = np.where(ink)
    if len(xs) == 0:
        chk("margins", False, "no ink found"); return res
    l, r, t, b = xs.min(), w - 1 - xs.max(), ys.min(), h - 1 - ys.max()
    res["metrics"]["margins_px"] = [int(l), int(t), int(r), int(b)]
    chk("not_cropped", min(l, t, r, b) > T["edge_touch_px"], f"nearest ink to edge {min(l,t,r,b)}px")
    need = T["min_margin_frac"] * w
    chk("safe_margin", min(l, r) >= need and min(t, b) >= T["min_margin_frac"] * h,
        f"margins L{l} T{t} R{r} B{b} px, need >= {need:.0f}/{T['min_margin_frac']*h:.0f}")

    # 3 enclosed regions (colouring spaces)
    white = (~ink).astype(np.uint8)
    n, lab, st, cen = cv2.connectedComponentsWithStats(white, connectivity=4)
    border_labels = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
    regions = []
    for i in range(1, n):
        if i in border_labels:
            continue
        a = int(st[i, cv2.CC_STAT_AREA])
        m = (lab == i).astype(np.uint8)
        cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        per = cv2.arcLength(max(cs, key=cv2.contourArea), True) if cs else 1
        circ = 4 * np.pi * a / (per * per) if per else 0
        regions.append({"area": a, "circ": round(float(circ), 3), "cx": float(cen[i][0]), "cy": float(cen[i][1])})
    min_area = T["min_region_frac"] * w * h
    tiny = [r_ for r_ in regions if r_["area"] < min_area]
    res["metrics"]["enclosed_regions"] = len(regions)
    res["metrics"]["tiny_regions"] = len(tiny)
    chk("no_tiny_regions", len(tiny) == 0, f"{len(tiny)} enclosed regions under {min_area:.0f}px (too small to colour / specks)")
    chk("has_colourable_regions", len(regions) >= 3, f"{len(regions)} enclosed regions")

    # 4 stroke width consistency
    dt = ndi.distance_transform_edt(ink)
    ridge = ink & (dt >= ndi.maximum_filter(dt, size=3)) & (dt > 0.7)
    sw = 2 * dt[ridge]
    med = float(np.median(sw)); p10, p90 = float(np.percentile(sw, 10)), float(np.percentile(sw, 90))
    thin = float((sw < T["thin_line_ratio"] * med).mean())
    res["metrics"]["stroke_px"] = {"median": round(med, 2), "p10": round(p10, 2), "p90": round(p90, 2), "thin_frac": round(thin, 3)}
    chk("stroke_thick_enough", med >= T["min_median_stroke_frac"] * w, f"median stroke {med:.1f}px (>= {T['min_median_stroke_frac']*w:.1f})")
    chk("stroke_consistent", thin <= T["max_thin_frac"], f"{thin:.1%} of line is under {T['thin_line_ratio']:.0%} of median width")

    # 5 spec-driven structural PROXIES (counts only; not proof of correct geometry)
    if expect:
        body = [r_ for r_ in regions if r_["area"] >= min_area]
        for rule in expect:
            if rule["type"] == "similar_round_regions":
                cand = [r_ for r_ in body if r_["circ"] >= rule.get("min_circularity", 0.75)
                        and rule["area_frac"][0] * w * h <= r_["area"] <= rule["area_frac"][1] * w * h]
                if cand:
                    ma = np.median([c["area"] for c in cand])
                    cand = [c for c in cand if abs(c["area"] - ma) <= 0.45 * ma]
                chk(rule["name"], len(cand) == rule["count"], f"found {len(cand)} similar round regions, expected {rule['count']} (proxy, counts only)")
            elif rule["type"] == "min_regions":
                chk(rule["name"], len(body) >= rule["count"], f"{len(body)} regions >= {rule['count']} expected")
    res["passed_all_automated"] = all(c["pass"] for c in res["checks"].values())
    res["failed"] = [k for k, c in res["checks"].items() if not c["pass"]]
    res["thresholds"] = T
    return res


def print_dims(path, size_name):
    """Final-package check: exact pixel size for the paper format at 300 DPI."""
    target = {"US_LETTER": (2550, 3300), "A4": (2480, 3508)}[size_name]
    im = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    return {"pass": im.shape[1] == target[0] and im.shape[0] == target[1], "method": "automated",
            "detail": f"{im.shape[1]}x{im.shape[0]} vs {target[0]}x{target[1]}"}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("image"); ap.add_argument("--spec"); ap.add_argument("--object")
    a = ap.parse_args()
    expect = None
    if a.spec and a.object:
        spec = json.loads(Path(a.spec).read_text(encoding="utf-8"))
        expect = next(o for o in spec["objects"] if o["id"] == a.object).get("auto_checks")
    r = analyse(a.image, expect)
    outdir = Path(__file__).resolve().parent.parent / "qc"
    outdir.mkdir(exist_ok=True)
    out = outdir / (Path(a.image).stem + ".auto_qc.json")
    out.write_text(json.dumps(r, indent=2), encoding="utf-8")
    for k, c in r["checks"].items():
        print(("PASS " if c["pass"] else "FAIL ") + k.ljust(24) + c["detail"])
    print("ALL AUTOMATED PASS" if r.get("passed_all_automated") else "FAILED: " + ", ".join(r.get("failed", [])))
    print("report:", out)
    sys.exit(0 if r.get("passed_all_automated") else 1)
