import re

with open("cyber-security/CYBER_SECURITY_ESSENTIALS_AND_LINUX_SECURITY_GUIDE.md") as f:
    text = f.read()

lines = text.splitlines()
diagram_indices = []
for i, line in enumerate(lines):
    if line.strip().startswith("```mermaid"):
        context = []
        heading = ""
        for j in range(max(0, i-15), i):
            if lines[j].strip().startswith("#"):
                heading = lines[j].strip()
            elif lines[j].strip():
                context.append(lines[j].strip())
        diagram_indices.append((i+1, heading, context[-1] if context else ""))

print(f"Total diagrams: {len(diagram_indices)}")
for idx, (lineno, heading, ctx) in enumerate(diagram_indices, 1):
    print(f"Fig {idx:02d} | Line {lineno:4d} | {heading} | {ctx[:60]}")
