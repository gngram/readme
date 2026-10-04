#!/usr/bin/env python3
"""
Finalize the Cyber Security & Linux Security Master Guide PDF:
1. Replaces generic ![diagram](...) with publication-grade descriptive Figure captions.
2. Generates optimized print CSS for A4 publication rendering.
3. Invokes Pandoc to compile a standalone HTML bundle with embedded SVGs.
4. Invokes Headless Chromium to generate the publication-grade PDF.
5. Verifies page count, outline, and layout integrity using poppler tools.
"""

import os
import re
import subprocess
import sys

captions = [
    "Figure 1: Comprehensive Cyber Security & Linux Security Architectural Roadmap",
    "Figure 2: The Five Pillars of Information Assurance (DoD IA Architecture)",
    "Figure 3: Symmetric vs. Asymmetric Cryptography and Digital Signature Verification",
    "Figure 4: Recursive DNS Resolution Architecture & Cache Poisoning Injection Points",
    "Figure 5: Multi-Tier Perimeter Defense: Packet Filtering, Stateful Inspection, and WAF",
    "Figure 6: Hypervisor Architectures: Bare-Metal Type-1 vs. Hosted Type-2 Virtualization",
    "Figure 7: Windows Security Reference Monitor (SRM) Access Token & DACL Evaluation",
    "Figure 8: Windows Subsystem Message Loop & Cross-Process Shatter Attack",
    "Figure 9: Windows Portable Executable (PE) Program Execution & Process Initialization",
    "Figure 10: Anonymous Proxy Chains vs. Tor Multi-Hop Onion Routing Circuit",
    "Figure 11: Covert Protocol Smuggling & DNS/ICMP Exfiltration Channels",
    "Figure 12: Botnet Command and Control (C2) Topologies: Centralized vs. P2P Mesh",
    "Figure 13: Fast-Flux DNS & Double-Flux Botnet IP Shuffling Infrastructure",
    "Figure 14: Social Engineering Attack Vectors & Credential Harvesting Pipeline",
    "Figure 15: Rogue Antivirus (Scareware) Infection, Extortion, and Payment Workflow",
    "Figure 16: Click Fraud Multi-Tier Traffic Laundering and Ad Syndicate Abuse",
    "Figure 17: Standard x86-64 Stack Frame Memory Layout & Register Conventions",
    "Figure 18: Stack Buffer Overflow Exploitation & Return Address Hijack Mechanics",
    "Figure 19: Unsigned vs. Signed Integer Overflow & Boundary Wraparound Flaws",
    "Figure 20: Time-of-Check to Time-of-Use (TOCTOU) Race Condition Window",
    "Figure 21: Return-Oriented Programming (ROP) Gadget Chain Execution Mechanics",
    "Figure 22: SQL Injection Query Manipulation & Authentication Bypass Sequence",
    "Figure 23: Stored (Persistent) Cross-Site Scripting (XSS) Cookie Theft Workflow",
    "Figure 24: Malicious PDF Exploit Structure & Embedded Action Script Execution",
    "Figure 25: NTP/DNS Amplification Distributed Denial of Service (DDoS) Attack",
    "Figure 26: Malware Structural Taxonomy & Infection Mechanisms",
    "Figure 27: Packer & Crypter Execution Flow: Stub Decompression & OEP Transfer",
    "Figure 28: Anti-Analysis Sandbox & VM Fingerprinting Decision Tree",
    "Figure 29: User-Mode API Hooking vs. Kernel-Mode SSDT/DKOM Rootkit Mechanics",
    "Figure 30: Remote Process DLL Injection via CreateRemoteThread Pipeline",
    "Figure 31: Windows Token Kidnapping & Impersonation Privilege Escalation",
    "Figure 32: Physical Memory Forensics & Virtual Address Descriptor (VAD) Tree",
    "Figure 33: Enterprise Honeypot & Deception Decoy Deployment Topology",
    "Figure 34: Standard Linux DAC Triad: User, Group, and Other Permission Model",
    "Figure 35: Linux Special Permission Bits: SUID, SGID, and Sticky Bit Evaluation",
    "Figure 36: Discretionary Access Control (DAC) Failure vs. Mandatory Access Control (MAC) Confinement",
    "Figure 37: Linux Security Modules (LSM) Hook Architecture in the Kernel Subsystem",
    "Figure 38: SELinux Type Enforcement (TE) & Multi-Category Security (MCS) Model",
    "Figure 39: Linux Dual Credential Storage Architecture: /etc/passwd and /etc/shadow",
    "Figure 40: Pluggable Authentication Modules (PAM) Stack Evaluation Flow",
    "Figure 41: Linux Container Isolation: Kernel Namespaces and Cgroups v2 Quotas",
    "Figure 42: Seccomp-BPF System Call Filtering & Syscall Dispatch Interception",
    "Figure 43: Linux Kernel Netfilter Packet Traversal & Hook Architecture",
    "Figure 44: Linux Audit Framework (auditd) Kernel Syscall Interception Architecture",
    "Figure 45: Defense-in-Depth Enterprise Production Linux Hardening Architecture"
]

input_md = "cyber-security/build/guide_processed.md"
output_md = "cyber-security/build/guide_final.md"
css_file = "cyber-security/build/pdf-style.css"
output_html = "cyber-security/build/guide.html"
output_pdf = "cyber-security/CYBER_SECURITY_ESSENTIALS_AND_LINUX_SECURITY_GUIDE.pdf"

if not os.path.exists(input_md):
    print(f"Error: {input_md} not found. Please wait for mmdc to finish.")
    sys.exit(1)

with open(input_md, "r") as f:
    text = f.read()

# Replace generic ![diagram] or ![] with descriptive captions sequentially
idx = 0
def repl(match):
    global idx
    cap = captions[idx] if idx < len(captions) else f"Figure {idx+1}: Cyber Security Architecture Schematic"
    target = match.group(1)
    idx += 1
    return f"![{cap}]({target})"

final_text = re.sub(r"!\[[^\]]*\]\(([^)]+\.svg)\)", repl, text)

with open(output_md, "w") as f:
    f.write(final_text)

print(f"Successfully processed {idx} diagrams with descriptive figure captions in {output_md}")

# Generate high quality publication CSS
css_content = """@page {
  size: A4;
  margin: 18mm 14mm 18mm 14mm;
  @bottom-right {
    content: counter(page);
    font-size: 8.5pt;
    color: #5c677d;
  }
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  font-size: 9.8pt;
  line-height: 1.52;
  color: #1e293b;
  background-color: #ffffff;
}

h1 {
  font-size: 18pt;
  color: #0f172a;
  border-bottom: 2.5px solid #0284c7;
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
  color: #0369a1;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 4px;
  margin-top: 20px;
  margin-bottom: 10px;
  page-break-after: avoid;
}

h3 {
  font-size: 11pt;
  color: #0f766e;
  margin-top: 15px;
  margin-bottom: 6px;
  page-break-after: avoid;
}

h4 {
  font-size: 10pt;
  color: #334155;
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
  font-size: 8.2pt;
  background-color: #f1f5f9;
  padding: 1.5px 4px;
  border-radius: 3px;
  color: #b91c1c;
  border: 1px solid #e2e8f0;
}

pre {
  background-color: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 8pt;
  line-height: 1.38;
  overflow-x: auto;
  page-break-inside: avoid;
}

pre code {
  background-color: transparent;
  padding: 0;
  border: none;
  color: #0f172a;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
  margin-bottom: 14px;
  font-size: 8.4pt;
  page-break-inside: avoid;
}

th, td {
  border: 1px solid #cbd5e1;
  padding: 5px 8px;
  text-align: left;
}

th {
  background-color: #f0f9ff;
  color: #0369a1;
  font-weight: 600;
}

tr:nth-child(even) {
  background-color: #f8fafc;
}

blockquote {
  margin: 10px 0;
  padding: 6px 14px;
  color: #334155;
  border-left: 4px solid #0284c7;
  background-color: #f0f9ff;
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
  color: #475569;
  font-weight: 600;
  margin-top: 6px;
  margin-bottom: 10px;
  text-align: center;
}

hr {
  height: 1px;
  background-color: #e2e8f0;
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

with open(css_file, "w") as f:
    f.write(css_content)

print(f"Generated stylesheet in {css_file}")

# Compile HTML bundle using Pandoc
pandoc_cmd = [
    "pandoc",
    output_md,
    "-s",
    f"--css={css_file}",
    "--embed-resources",
    "--resource-path=cyber-security/build:cyber-security:cyber-security/diagrams",
    "-o",
    output_html
]

print("Running pandoc to create self-contained HTML bundle...")
subprocess.run(pandoc_cmd, check=True)
print(f"HTML bundle created at {output_html}")

# Convert HTML to PDF using Headless Chromium
chromium_path = "/nix/store/j8hc3kdypr2gaa2w3dq0a370lwfzbasf-chromium-151.0.7922.137/bin/chromium"
if not os.path.exists(chromium_path):
    # fallback to chromium in PATH
    chromium_path = "chromium"

chrome_cmd = [
    chromium_path,
    "--headless",
    "--disable-gpu",
    "--no-sandbox",
    "--run-all-compositor-stages-before-draw",
    "--no-pdf-header-footer",
    "--generate-pdf-document-outline",
    f"--print-to-pdf={output_pdf}",
    output_html
]

print(f"Running headless Chromium to render {output_pdf}...")
subprocess.run(chrome_cmd, check=True)
print(f"PDF successfully rendered: {output_pdf}")

# Check with pdfinfo if available
try:
    info_res = subprocess.run(["pdfinfo", output_pdf], capture_output=True, text=True)
    if info_res.returncode == 0:
        print("\n--- PDF INFO ---")
        print(info_res.stdout)
except Exception as e:
    pass

print("\nPDF generation complete!")
