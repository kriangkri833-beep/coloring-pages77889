"""Save the image currently on the Windows clipboard into raw_from_chatgpt/ unmodified (lossless PNG).
Usage: python tools/save_clipboard.py <file_name.png>
Never overwrites. Prints sha256, size. Original bytes are the clipboard PNG re-encoded losslessly.
"""
import sys, hashlib
from pathlib import Path
from PIL import ImageGrab

name = sys.argv[1]
dest = Path(__file__).resolve().parent.parent / "raw_from_chatgpt" / name
dest.parent.mkdir(exist_ok=True)
if dest.exists():
    raise SystemExit(f"REFUSED: {dest} already exists")
im = ImageGrab.grabclipboard()
if im is None or not hasattr(im, "save"):
    raise SystemExit("No image on clipboard")
im.save(dest, "PNG")
h = hashlib.sha256(dest.read_bytes()).hexdigest()
for other in dest.parent.glob("*.png"):
    if other != dest and hashlib.sha256(other.read_bytes()).hexdigest() == h:
        dest.unlink()
        raise SystemExit(f"REFUSED: clipboard image is identical to {other.name} (stale clipboard?). Nothing saved.")
print(dest, im.size, im.mode, hashlib.sha256(dest.read_bytes()).hexdigest()[:16])
