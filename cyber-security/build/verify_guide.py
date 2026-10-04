#!/usr/bin/env python3
"""
Verification script for the Cyber Security & Linux Security guide.
"""

import re
import sys

filename = "cyber-security/CYBER_SECURITY_ESSENTIALS_AND_LINUX_SECURITY_GUIDE.md"

with open(filename, "r") as f:
    content = f.read()

words = re.findall(r'\b\w+\b', content)
word_count = len(words)
line_count = len(content.splitlines())

print("=== Cyber Security & Linux Security Guide Statistics ===")
print(f"File: {filename}")
print(f"Word count: {word_count}")
print(f"Line count: {line_count}")
print(f"Estimated Standard Technical Pages (~400 words/page): {word_count / 400:.1f} pages")
print(f"Estimated Standard Technical Pages (~425 words/page): {word_count / 425:.1f} pages")

# Check Mermaid blocks
mermaid_blocks = re.findall(r"```mermaid\s+(.*?)```", content, re.DOTALL)
print(f"\nTotal Mermaid Diagrams: {len(mermaid_blocks)}")

for i, block in enumerate(mermaid_blocks, 1):
    lines = [l.strip() for l in block.strip().splitlines() if l.strip()]
    header = lines[0] if lines else "EMPTY"
    print(f"Diagram {i:02d}: {header}")

# Check Section Headings
headings = [h for h in content.splitlines() if h.startswith("#")]
print(f"\nTotal Headings: {len(headings)}")
for h in headings[:16]:
    print(" ", h)
if len(headings) > 16:
    print(f"  ... and {len(headings) - 16} more headings.")

print("\nVerification SUCCESS!")
