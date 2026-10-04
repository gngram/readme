#!/usr/bin/env python3
"""
Verification script for the generated comprehensive guide.
"""

import re
import sys

filename = "arm-security/ARM_SECURITY_CCA_RME_COMPREHENSIVE_GUIDE.md"

with open(filename, "r") as f:
    content = f.read()

words = re.findall(r'\b\w+\b', content)
word_count = len(words)
line_count = len(content.splitlines())

print("=== Guide Statistics ===")
print(f"File: {filename}")
print(f"Word count: {word_count}")
print(f"Line count: {line_count}")
print(f"Approximate pages: {word_count / 425:.1f} pages")

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
for h in headings[:15]:
    print(" ", h)
if len(headings) > 15:
    print(f"  ... and {len(headings) - 15} more headings.")

print("\nVerification SUCCESS!")
