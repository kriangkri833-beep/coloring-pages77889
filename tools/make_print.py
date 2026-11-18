"""Make print-ready pages from an approved raw image: US Letter + A4 at 300 DPI, plus a 2-format PDF each.
Steps: crop to ink bounding box -> fit inside page minus margin -> cubic upscale -> light blur -> threshold
(pure black/white, so no grey) -> centre on white canvas of EXACT pixel size -> verify.
The upscale is interpolation, NOT new detail: raw ChatGPT output is ~1086x1448, so line art is enlarged ~2.3x.
Usage: python tools/make_print.py <raw.png> <out_stem>   e.g. CP-001_rotary_telephone
Never touches the raw file.
"""
import sys, json
from pathlib import Path
import numpy as np, cv2
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qc_lineart as q

FORMATS = {"US_LETTER": (2550, 3300, (8.5 * inch, 11 * inch)), "A4": (2480, 3508, (595.2756, 841.8898))}
STROKE_TARGET_PX = 34.0  # median line width at 300 DPI = the owner-approved master (rotary telephone)
MARGIN_PX = 150  # 0.5 inch at 300 DPI, minimum clear border on every side

raw, stem = Path(sys.argv[1]), sys.argv[2]
root = Path(__file__).resolve().parent.parent
g = cv2.imread(str(raw), cv2.IMREAD_GRAYSCALE)
ys, xs = np.where(g < 128)
crop = g[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
# Repair: fill 1-4 px enclosed pinholes (ink gaps from near-touching lines), logged in the report.
_n, _lab, _st, _ = cv2.connectedComponentsWithStats((crop >= 128).astype(np.uint8), connectivity=4)
_edge = set(np.unique(np.concatenate([_lab[0], _lab[-1], _lab[:, 0], _lab[:, -1]])))
pinholes = [i for i in range(1, _n) if i not in _edge and _st[i, cv2.CC_STAT_AREA] < 5]
for i in pinholes:
    crop[_lab == i] = 0
report = {"pinholes_filled": len(pinholes), "source": str(raw), "upscale_note": "interpolated enlargement of ~1086x1448 source", "formats": {}}
for name, (W, H, pts) in FORMATS.items():
    box_w, box_h = W - 2 * MARGIN_PX, H - 2 * MARGIN_PX
    s = min(box_w / crop.shape[1], box_h / crop.shape[0])
    up = cv2.resize(crop, (round(crop.shape[1] * s), round(crop.shape[0] * s)), interpolation=cv2.INTER_CUBIC)
    up = cv2.GaussianBlur(up, (0, 0), 1.2)
    _, bw = cv2.threshold(up, 128, 255, cv2.THRESH_BINARY)
    # Normalise line weight to the master so the whole collection looks consistent (erode thicker / dilate thinner).
    from scipy import ndimage as _ndi
    def _stroke(img):
        _ink = img < 128
        _dt = _ndi.distance_transform_edt(_ink)
        _r = _ink & (_dt >= _ndi.maximum_filter(_dt, size=3)) & (_dt > 0.7)
        return float(np.median(2 * _dt[_r]))
    def _topo(img):
        _n1, _l1, _s1, _ = cv2.connectedComponentsWithStats((img >= 128).astype(np.uint8), connectivity=4)
        _e = set(np.unique(np.concatenate([_l1[0], _l1[-1], _l1[:, 0], _l1[:, -1]])))
        regions = sum(1 for i in range(1, _n1) if i not in _e and _s1[i, cv2.CC_STAT_AREA] >= 50)
        inkc = cv2.connectedComponents((img < 128).astype(np.uint8), connectivity=8)[0] - 1
        return regions, inkc
    cur = _stroke(bw)
    ref_topo = _topo(bw)
    delta = (STROKE_TARGET_PX - cur) / 2
    note = "unchanged"
    if abs(delta) >= 0.75:
        r_full = int(round(abs(delta)))
        note = "NOT normalised: every adjustment changed the number of parts"
        for r_ in range(r_full, 0, -1):
            k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r_ + 1, 2 * r_ + 1))
            ink_ = (bw < 128).astype(np.uint8)
            ink_ = cv2.dilate(ink_, k) if delta > 0 else cv2.erode(ink_, k)
            cand = np.where(ink_ > 0, 0, 255).astype(np.uint8)
            if _topo(cand) == ref_topo:
                bw = cand
                note = "normalised" if r_ == r_full else f"partly normalised (radius {r_} of {r_full}) to keep every part"
                break
    report.setdefault("stroke_normalised", {})[name] = {"from_px": round(cur, 1), "to_px": round(_stroke(bw), 1), "note": note, "regions_parts": ref_topo[0], "ink_components": ref_topo[1], "topology_preserved": _topo(bw) == ref_topo}
    canvas_ = np.full((H, W), 255, np.uint8)
    y0, x0 = (H - bw.shape[0]) // 2, (W - bw.shape[1]) // 2
    canvas_[y0:y0 + bw.shape[0], x0:x0 + bw.shape[1]] = bw
    out_dir = root / "pages_final" / name
    out_dir.mkdir(parents=True, exist_ok=True)
    png = out_dir / f"{stem}.png"
    cv2.imwrite(str(png), canvas_, [cv2.IMWRITE_PNG_COMPRESSION, 9])
    pdf = out_dir / f"{stem}.pdf"
    c = canvas.Canvas(str(pdf), pagesize=pts)
    c.drawImage(str(png), 0, 0, width=pts[0], height=pts[1])
    c.save()
    dims = q.print_dims(png, name)
    auto = q.analyse(png)
    pure = bool(np.isin(np.unique(canvas_), [0, 255]).all())
    report["formats"][name] = {"png": str(png), "pdf": str(pdf), "dims_check": dims,
                               "pure_black_white": pure, "automated_qc_passed": auto["passed_all_automated"],
                               "failed": auto["failed"], "margins_px": auto["metrics"]["margins_px"],
                               "min_margin_required_px": MARGIN_PX}
    report["formats"][name]["margin_ok"] = min(auto["metrics"]["margins_px"]) >= MARGIN_PX - 2
    print(name, dims["detail"], "dims", "PASS" if dims["pass"] else "FAIL", "| margins", auto["metrics"]["margins_px"],
          "| pure B/W", pure, "| auto QC", "PASS" if auto["passed_all_automated"] else auto["failed"])
(root / "qc" / f"{stem}.print_qc.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
