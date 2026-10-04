#!/usr/bin/env python3
"""
Finalize the PDF with descriptive figure captions and enhanced publication styling.
"""

import os
import re
import subprocess

captions = [
    "Figure 1: Arm CCA Architectural Guide Structure & Module Roadmap",
    "Figure 2: Traditional Hierarchical Privilege Model & Hypervisor Paradox",
    "Figure 3: Arm TrustZone Dual-World Architecture",
    "Figure 4: Arm CCA Orthogonal Decoupling Model",
    "Figure 5: Arm CCA Ecosystem Roles & Provisioning Sequence",
    "Figure 6: Armv9-A Four Security States & Exception Level Hierarchy",
    "Figure 7: Virtual to Physical Address Translation & PAS Assignment Pipeline",
    "Figure 8: Architectural Access Matrix & Legal PAS Boundaries",
    "Figure 9: PE Translation and Granule Protection Check (GPC) Pipeline",
    "Figure 10: Two-Level Granule Protection Table (GPT) Architecture",
    "Figure 11: Dynamic Granule Transition & Memory Scrubbing Protocol",
    "Figure 12: Memory Protection Engine (MPE) Inline DRAM Encryption",
    "Figure 13: Memory Encryption Contexts (MEC) & MECID Key Allocation",
    "Figure 14: Multi-Socket Coherent Interconnect Link Protection",
    "Figure 15: System MMU (SMMUv3) RME Architecture with Internal GPC",
    "Figure 16: Peripheral ATS Security Dilemma & Device Protection Table (DPT)",
    "Figure 17: RME Device Assignment (RME-DA) Security Hierarchy",
    "Figure 18: Arm CCA Software Topology & Execution Domains",
    "Figure 19: Realm Lifecycle State Machine (NEW, ACTIVE, SYSTEM_OFF)",
    "Figure 20: Realm Execution Context (REC) Entry & Exit Sequence",
    "Figure 21: Realm Translation Table (RTT) Hierarchy & RIPAS States",
    "Figure 22: GICv3/v4 Interrupt Routing & Virtual Interrupt Injection",
    "Figure 23: Realm Management Interface (RMI) Dispatch Flow",
    "Figure 24: Realm Services Interface (RSI) Command Operations",
    "Figure 25: Secondary vCPU Boot via PSCI CPU_ON Mediation",
    "Figure 26: Encapsulated CCA Dual-Token Attestation Architecture",
    "Figure 27: Hardware Root of Trust Key Derivation Hierarchy",
    "Figure 28: Complete Remote Attestation Protocol & Verification Flow",
    "Figure 29: Arm CCA Platform Security Lifecycle State Machine",
    "Figure 30: RME Hardware Debug, Trace (SPE), and Profiling Isolation",
    "Figure 31: RAS ECC Uncorrectable Error Scrubbing Sequence"
]

input_md = "arm-security/build/guide_processed.md"
output_md = "arm-security/build/guide_final.md"

with open(input_md, "r") as f:
    text = f.read()

# Replace ![diagram] with descriptive captions sequentially
idx = 0
def repl(match):
    global idx
    cap = captions[idx] if idx < len(captions) else f"Figure {idx+1}: Architecture Schematic"
    target = match.group(1)
    idx += 1
    return f"![{cap}]({target})"

final_text = re.sub(r"!\[diagram\]\(([^)]+)\)", repl, text)

with open(output_md, "w") as f:
    f.write(final_text)

print(f"Replaced {idx} diagrams with descriptive figure captions.")

# Enhanced CSS
css_content = """@page {
  size: A4;
  margin: 18mm 14mm 18mm 14mm;
  @bottom-right {
    content: counter(page);
    font-size: 9pt;
    color: #586069;
  }
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  font-size: 10pt;
  line-height: 1.55;
  color: #24292e;
  background-color: #ffffff;
}

h1 {
  font-size: 18pt;
  color: #0b2545;
  border-bottom: 2px solid #0091bd;
  padding-bottom: 6px;
  margin-top: 26px;
  margin-bottom: 14px;
  page-break-before: always;
}

h1:first-of-type {
  page-break-before: avoid;
  margin-top: 0;
}

h2 {
  font-size: 13pt;
  color: #134074;
  border-bottom: 1px solid #e1e4e8;
  padding-bottom: 4px;
  margin-top: 20px;
  margin-bottom: 10px;
  page-break-after: avoid;
}

h3 {
  font-size: 11.5pt;
  color: #1d3557;
  margin-top: 16px;
  margin-bottom: 6px;
  page-break-after: avoid;
}

h4 {
  font-size: 10.5pt;
  color: #457b9d;
  margin-top: 12px;
  margin-bottom: 4px;
  page-break-after: avoid;
}

p {
  margin-top: 0;
  margin-bottom: 8px;
  text-align: justify;
}

code {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
  font-size: 8.5pt;
  background-color: #f6f8fa;
  padding: 2px 4px;
  border-radius: 3px;
  color: #d73a49;
  border: 1px solid #e1e4e8;
}

pre {
  background-color: #f6f8fa;
  border: 1px solid #e1e4e8;
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 8pt;
  line-height: 1.4;
  overflow-x: auto;
  page-break-inside: avoid;
}

pre code {
  background-color: transparent;
  padding: 0;
  border: none;
  color: #24292e;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
  margin-bottom: 14px;
  font-size: 8.5pt;
  page-break-inside: avoid;
}

th, td {
  border: 1px solid #d1d5da;
  padding: 6px 9px;
  text-align: left;
}

th {
  background-color: #f1f8ff;
  color: #032f62;
  font-weight: 600;
}

tr:nth-child(even) {
  background-color: #fafbfc;
}

blockquote {
  margin: 10px 0;
  padding: 6px 14px;
  color: #444d56;
  border-left: 4px solid #0091bd;
  background-color: #f1f8ff;
  border-radius: 0 4px 4px 0;
  page-break-inside: avoid;
}

figure {
  margin: 14px auto;
  text-align: center;
  page-break-inside: avoid;
}

img {
  max-width: 98%;
  max-height: 200mm;
  width: auto;
  height: auto;
  object-fit: contain;
  display: block;
  margin: 0 auto;
}

figcaption {
  font-size: 8.5pt;
  color: #444d56;
  font-weight: 600;
  margin-top: 6px;
  margin-bottom: 10px;
  text-align: center;
}

hr {
  height: 1px;
  background-color: #e1e4e8;
  border: none;
  margin: 20px 0;
}

ul, ol {
  margin-top: 0;
  margin-bottom: 10px;
  padding-left: 20px;
}

li {
  margin-bottom: 3px;
}
"""

with open("arm-security/build/pdf-style.css", "w") as f:
    f.write(css_content)

print("Updated PDF stylesheet.")
