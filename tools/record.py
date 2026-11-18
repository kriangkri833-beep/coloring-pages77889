"""Record a visual review. Usage: python tools/record.py <stem> PASS|REVISE "note" ["id:fail|warn|pass:note" ...]
Method is always visual_judgment (subjective).
"""
import sys, json
from pathlib import Path

stem, verdict, note = sys.argv[1], sys.argv[2], sys.argv[3]
findings = [{"id": "overall", "severity": "pass" if verdict == "PASS" else "fail", "note": note}]
for extra in sys.argv[4:]:
    i, sev, n = extra.split(":", 2)
    findings.append({"id": i, "severity": sev, "note": n})
out = Path(__file__).resolve().parent.parent / "qc" / f"{stem}.visual_review.json"
out.write_text(json.dumps({"image": f"raw_from_chatgpt/{stem}.png", "method": "visual_judgment",
    "reviewer": "Claude (vision, subjective - not a programmatic check). Owner still approves.",
    "verdict": verdict, "findings": findings}, indent=2), encoding="utf-8")
print("recorded", out.name, verdict)
