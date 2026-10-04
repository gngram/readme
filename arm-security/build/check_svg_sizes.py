import glob
import re

for f in sorted(glob.glob("arm-security/diagrams/*.svg")):
    with open(f) as fp:
        s = fp.read()
    vb = re.search(r'viewBox="([^"]+)"', s)
    if vb:
        parts = [float(x) for x in vb.group(1).split()]
        w, h = parts[2], parts[3]
        ratio = h / w if w > 0 else 0
        if ratio > 1.2 or h > 800:
            print(f"{f}: width={w:.1f}, height={h:.1f}, aspect_ratio={ratio:.2f} (CHECK)")
