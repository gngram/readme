import re

with open("cyber-security/CYBER_SECURITY_ESSENTIALS_AND_LINUX_SECURITY_GUIDE.md") as f:
    text = f.read()

# find all mermaid blocks
matches = list(re.finditer(r"```mermaid\n(.*?)\n```", text, re.DOTALL))
print(f"Total mermaid blocks found: {len(matches)}")

errors = []
for i, m in enumerate(matches, 1):
    content = m.group(1)
    chart_type = content.strip().split("\n")[0].strip()
    # Check for invalid syntax in graph TD / LR
    if "graph" in chart_type:
        lines = content.splitlines()
        for l_num, line in enumerate(lines, 1):
            if "-->>" in line:
                errors.append((i, l_num, line.strip(), "Found '-->>' in graph (invalid in flowcharts, use '-->' or '-.->')"))
            if "<<--" in line:
                errors.append((i, l_num, line.strip(), "Found '<<--' in graph"))

print(f"Discovered {len(errors)} potential syntax issues:")
for err in errors:
    print(f"Diagram {err[0]}, Line {err[1]}: {err[2]} -> {err[3]}")
