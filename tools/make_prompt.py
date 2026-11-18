"""Print the generation prompt (template v2) for an object, or a retry prompt from diagnose fixes.
Usage: python tools/make_prompt.py <object_id>            -> first prompt
       python tools/make_prompt.py <object_id> --retry <stem> -> retry prompt built from diagnose.py output
"""
import sys, json, subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
spec = json.loads((root / "specs" / "CP-001.json").read_text(encoding="utf-8"))
t = spec["prompt_template_v2"]
obj = next(o for o in spec["objects"] if o["id"] == sys.argv[1])
if "--retry" in sys.argv:
    stem = sys.argv[sys.argv.index("--retry") + 1]
    out = subprocess.run([sys.executable, str(root / "tools" / "diagnose.py"), stem], capture_output=True, text=True).stdout
    if "AMENDMENT:" not in out:
        raise SystemExit(out)
    fixes = out.split("keeping everything else the same.", 1)[1].strip()
    print(t["retry_text"].format(fixes=fixes))
else:
    print(t["text"].format(name=obj["name"], view=obj.get("view", "front view"), structure="; ".join(obj["structure"])))
