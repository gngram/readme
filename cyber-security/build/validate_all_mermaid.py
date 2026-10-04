import re
import subprocess
import os

with open("cyber-security/CYBER_SECURITY_ESSENTIALS_AND_LINUX_SECURITY_GUIDE.md") as f:
    text = f.read()

matches = list(re.finditer(r"```mermaid\n(.*?)\n```", text, re.DOTALL))
print(f"Testing {len(matches)} diagrams individually with mmdc...")

os.makedirs("/tmp/mmd_test", exist_ok=True)

failed = []
for i, m in enumerate(matches, 1):
    content = m.group(1)
    mmd_path = f"/tmp/mmd_test/diag_{i}.mmd"
    svg_path = f"/tmp/mmd_test/diag_{i}.svg"
    with open(mmd_path, "w") as mf:
        mf.write(content)
    
    cmd = [
        "mmdc",
        "-p", "cyber-security/build/puppeteer-config.json",
        "-i", mmd_path,
        "-o", svg_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        err_msg = res.stderr.splitlines()[-1] if res.stderr.splitlines() else res.stdout
        print(f"❌ Diagram {i} FAILED: {err_msg}")
        failed.append((i, content, res.stderr))
    else:
        print(f"✅ Diagram {i} OK")

print(f"\nSummary: {len(matches) - len(failed)} passed, {len(failed)} failed.")
