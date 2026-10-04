#!/usr/bin/env python3
"""
Master Builder for the Cyber Security Essentials & Linux Security Guide.
Assembles all modules, expands sections with deep technical reference details,
adds comprehensive glossary, acronym index, and compiles:
cyber-security/CYBER_SECURITY_ESSENTIALS_AND_LINUX_SECURITY_GUIDE.md
"""

import os
import re

MODULES_DIR = "cyber-security/modules"
OUTPUT_FILE = "cyber-security/CYBER_SECURITY_ESSENTIALS_AND_LINUX_SECURITY_GUIDE.md"

preface = """# CYBER SECURITY ESSENTIALS & LINUX SECURITY ARCHITECTURE
## Comprehensive Technical Reference Manual & Master Study Guide
**Document Classification:** Enterprise Cyber Security & Operating System Hardening Master Notes  
**Target Coverage:** Complete Core Cyber Security Domains & Deep Linux Security Subsystems  
**Primary Source Material:**
- *Cyber Security Essentials* (James Graham, Richard Howard, Ryan Olson – Auerbach Publications / CRC Press)
- *Linux Kernel Security Subsystem Architecture Specifications* (DAC, LSM, SELinux, AppArmor, Namespaces, Cgroups, Seccomp, Netfilter)
- *NIST Special Publications* (SP 800-53, SP 800-63B, SP 800-90A) & *OWASP Top 10 Enterprise Standards*

---

## Executive Summary & Guide Roadmap

Modern cybersecurity is an asymmetric discipline spanning computer architecture, network protocols, operating system internals, cryptographic mathematics, and human psychological factors. To defend complex systems or analyze sophisticated threat actors, security engineers and systems architects must understand security not as isolated silos, but as an interconnected stack.

This master guide establishes an exhaustive, publication-grade reference manual spanning **15 comprehensive modules** organized across four foundational domains:

1. **Foundations of Security & Windows OS Architecture (Modules 1–2)**:
   - Information Assurance pillars (Confidentiality, Integrity, Availability, Authentication, Authorization, Non-Repudiation).
   - Modern Cryptographic Primitives (Symmetric stream/block ciphers, Asymmetric key exchange and digital signatures, SHA-2/SHA-3 and HMACs).
   - Core Internet Protocols & Defenses (DNS, DNSSEC, Packet-filtering, Stateful, and Application Gateway Firewalls, Virtualization threat models).
   - Windows Operating System Security Architecture (Security Access Tokens, SIDs, DACLs, SACLs, Windows Messaging Subsystem, Shatter attacks, and the complete PE program execution lifecycle).
2. **Attacker Infrastructure, Social Engineering & Threat Operations (Modules 3–4)**:
   - Anonymization circuits, HTTP/SOCKS proxies, TOR onion routing, and proxy detection.
   - Covert Tunneling & Protocol Smuggling (HTTP encapsulation, DNS tunneling exfiltration, ICMP tunnels).
   - Botnet Command and Control (C2) topologies (Centralized IRC/HTTP vs. Decentralized P2P) and Fast-Flux / Double Fast-Flux DNS networks.
   - Social Engineering vectors (Mass Phishing, Spear-Phishing, BEC, Smishing, Vishing, AI Deepfakes), Rogue Antivirus scareware pipelines, and Pay-Per-Click Click Fraud networks.
3. **Exploitation, Malware Engineering & Defensive Forensics (Modules 5–9)**:
   - Low-level Software Vulnerabilities: x86/x86_64 call stack mechanics, stack-based buffer overflows, NOP sleds, shellcode construction, integer overflows, format string vulnerabilities, and TOCTOU race conditions.
   - Web Application Exploits & Network DoS: SQL Injection (In-band, Blind, Error-based) and Prepared Statement defenses, Cross-Site Scripting (Stored, Reflected, DOM), Malicious PDF document architecture, and Network Amplification attacks (SYN floods, DNS/NTP reflection).
   - Malware Taxonomy, Evasion & Persistence: Viruses, Worms, Trojans, Spyware, Ransomware; Packers, Crypters, Polymorphic and Metamorphic engines; Anti-Debugging, CPUID/Sandbox detection; and firmware/OS persistence mechanisms.
   - Advanced Capabilities & Memory Forensics: User-mode vs Kernel-mode Rootkits (IAT hooking, Inline Detours, SSDT hooking, DKOM), Token Kidnapping, DLL Injection (Classic, AppInit, Reflective), Volatile Memory Forensics with Volatility (VAD tree parsing, unlinked process detection), and Honeypot deception systems.
4. **Comprehensive Linux Security Fundamentals (Modules 10–14)**:
   - Linux Multi-User Philosophy & Discretionary Access Control (DAC): File triplets (`rwx`), numeric modes, directory permissions, SUID/SGID/Sticky bits, GTFOBins exploitation, `umask` calculations, and POSIX ACLs.
   - Mandatory Access Control (MAC) & Linux Security Modules (LSM): SELinux architecture (Type Enforcement, security contexts, AVC cache, Enforcing/Permissive modes, `semanage`, boolean toggles, `audit2allow`), and AppArmor path-based profile management.
   - Linux Authentication & Credentials: Shadow password file hashing algorithms (`$1$` MD5, `$5$` SHA-256, `$6$` SHA-512, `$y$` Yescrypt), Pluggable Authentication Modules (PAM) architecture (`auth`, `account`, `password`, `session`), control flags, and brute-force lockout (`pam_faillock`).
   - Process & Container Isolation Architecture: The Seven Linux Kernel Namespaces, Control Groups (cgroups v1 vs v2 resource limits), Linux Capabilities decomposing root authority, and Seccomp-BPF system call filtering.
   - Network Defense & Exploit Hardening: Netfilter packet processing hooks, `iptables` vs modern `nftables`, SSH server hardening (`sshd_config`), Linux Audit Framework (`auditd`), and kernel-level mitigations (KASLR, Stack Canaries, DEP/NX, KPTI, sysctl hardening).

```mermaid
graph TD
    subgraph Guide_Architecture["Guide Structural Roadmap (15 Modules)"]
        direction TB
        
        subgraph Domain1["Domain I: Security Foundations & Windows Architecture"]
            M1["Module 1: Information Assurance & Cryptography"]
            M2["Module 2: Windows Security & Process Execution"]
            M1 --> M2
        end
        
        subgraph Domain2["Domain II: Threat Infrastructure & Social Engineering"]
            M3["Module 3: Proxies, Covert Tunneling & Botnets"]
            M4["Module 4: Social Engineering & Fraud Campaigns"]
            M3 --> M4
        end
        
        subgraph Domain3["Domain III: Exploitation, Malware & Forensics"]
            M5["Module 5: Memory Corruption & Stack Overflows"]
            M6["Module 6: Web Exploits & Network DoS Attacks"]
            M7["Module 7: Malware Taxonomy, Evasion & Persistence"]
            M8["Module 8: Rootkits, DLL Injection & Token Theft"]
            M9["Module 9: Memory Forensics & Deception Systems"]
            M5 --> M6 --> M7 --> M8 --> M9
        end
        
        subgraph Domain4["Domain IV: Comprehensive Linux Security Fundamentals"]
            M10["Module 10: Linux Discretionary Access Control (DAC)"]
            M11["Module 11: Mandatory Access Control (SELinux & AppArmor)"]
            M12["Module 12: User Authentication, /etc/shadow & PAM"]
            M13["Module 13: Namespaces, Cgroups, Capabilities & Seccomp"]
            M14["Module 14: Netfilter, nftables, Auditing & Hardening"]
            M10 --> M11 --> M12 --> M13 --> M14
        end
        
        subgraph Domain5["Reference Reference & Master Index"]
            M15["Module 15: Master Technical Glossary & Acronym Index"]
        end
        
        Domain1 --> Domain2 --> Domain3 --> Domain4 --> Domain5
    end
    
    style Guide_Architecture fill:#fdfefe,stroke:#2c3e50,stroke-width:2px;
    style Domain1 fill:#ebf5fb,stroke:#2980b9,stroke-width:2px;
    style Domain2 fill:#fef9e7,stroke:#f39c12,stroke-width:2px;
    style Domain3 fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
    style Domain4 fill:#d4efdf,stroke:#27ae60,stroke-width:2px;
    style Domain5 fill:#f4ecf7,stroke:#8e44ad,stroke-width:2px;
```

---

## Detailed Table of Contents

- [Executive Summary & Guide Roadmap](#executive-summary--guide-roadmap)
- [Module 1: Information Assurance Fundamentals, Cryptography & Network Infrastructure](#module-1-information-assurance-fundamentals-cryptography--network-infrastructure)
  - [1.1 The Information Assurance Foundation: Beyond the CIA Triad](#11-the-information-assurance-foundation-beyond-the-cia-triad)
  - [1.2 Cryptographic Foundations: Symmetric, Asymmetric & Hashing](#12-cryptographic-foundations-symmetric-asymmetric--hashing)
  - [1.3 The Domain Name System (DNS) Architecture & Security Exploits](#13-the-domain-name-system-dns-architecture--security-exploits)
  - [1.4 Perimeter Defense: Firewall Architectures & Evolution](#14-perimeter-defense-firewall-architectures--evolution)
  - [1.5 Virtualization Security & Hypervisor Architectures](#15-virtualization-security--hypervisor-architectures)
- [Module 2: Windows Operating System Security Architecture & Process Execution](#module-2-windows-operating-system-security-architecture--process-execution)
  - [2.1 The Windows Security Model: SIDs, Tokens & Descriptors](#21-the-windows-security-model-sids-tokens--descriptors)
  - [2.2 Windows Messaging Subsystem & Shatter Attacks](#22-windows-messaging-subsystem--shatter-attacks)
  - [2.3 The Windows PE Program Execution Lifecycle](#23-the-windows-pe-program-execution-lifecycle)
- [Module 3: Attacker Infrastructure, Anonymization & Tunneling Techniques](#module-3-attacker-infrastructure-anonymization--tunneling-techniques)
  - [3.1 Proxies, Relays & Anonymization Networks](#31-proxies-relays--anonymization-networks)
  - [3.2 Covert Tunneling & Protocol Smuggling](#32-covert-tunneling--protocol-smuggling)
  - [3.3 Botnet Command & Control (C2) Architectures](#33-botnet-command--control-c2-architectures)
  - [3.4 Fast-Flux DNS & Resilient Hosting Networks](#34-fast-flux-dns--resilient-hosting-networks)
- [Module 4: Social Engineering, Fraud & Deception Campaigns](#module-4-social-engineering-fraud--deception-campaigns)
  - [4.1 Social Engineering Vectors: Phishing, Smishing & Vishing](#41-social-engineering-vectors-phishing-smishing--vishing)
  - [4.2 Rogue Antivirus & Scareware Monetization Pipelines](#42-rogue-antivirus--scareware-monetization-pipelines)
  - [4.3 Click Fraud Architecture & Pay-Per-Click Exploitation](#43-click-fraud-architecture--pay-per-click-exploitation)
- [Module 5: Software Vulnerabilities & Memory Corruption Exploitation](#module-5-software-vulnerabilities--memory-corruption-exploitation)
  - [5.1 The x86 / x86_64 Process Memory Architecture & Stack Mechanics](#51-the-x86--x86_64-process-memory-architecture--stack-mechanics)
  - [5.2 Stack-Based Buffer Overflows](#52-stack-based-buffer-overflows)
  - [5.3 Integer Overflows, Underflows & Signedness Flaws](#53-integer-overflows-underflows--signedness-flaws)
  - [5.4 Format String Vulnerabilities](#54-format-string-vulnerabilities)
  - [5.5 Race Conditions & Time-of-Check to Time-of-Use (TOCTOU)](#55-race-conditions--time-of-check-to-time-of-use-toctou)
- [Module 6: Web Application Attacks & Network Denial of Service](#module-6-web-application-attacks--network-denial-of-service)
  - [6.1 SQL Injection (SQLi) Mechanics & Defenses](#61-sql-injection-sqli-mechanics--defenses)
  - [6.2 Cross-Site Scripting (XSS)](#62-cross-site-scripting-xss)
  - [6.3 Malicious PDF Document Exploitation](#63-malicious-pdf-document-exploitation)
  - [6.4 Denial of Service (DoS) & Network Amplification Attacks](#64-denial-of-service-dos--network-amplification-attacks)
- [Module 7: Malware Taxonomy, Evasion & Persistence Techniques](#module-7-malware-taxonomy-evasion--persistence-techniques)
  - [7.1 Malware Taxonomy: Structural Classifications](#71-malware-taxonomy-structural-classifications)
  - [7.2 Evasion & Code Obfuscation: Packers, Crypters & Polymorphism](#72-evasion--code-obfuscation-packers-crypters--polymorphism)
  - [7.3 Anti-Analysis, Anti-Debugging & Virtual Machine Detection](#73-anti-analysis-anti-debugging--virtual-machine-detection)
  - [7.4 System Persistence Mechanisms](#74-system-persistence-mechanisms)
- [Module 8: Advanced Malware Capabilities & Privilege Escalation](#module-8-advanced-malware-capabilities--privilege-escalation)
  - [8.1 Rootkit Architectures: User-Mode vs. Kernel-Mode](#81-rootkit-architectures-user-mode-vs-kernel-mode)
  - [8.2 DLL Injection Techniques](#82-dll-injection-techniques)
  - [8.3 Token Kidnapping & Windows Privilege Escalation](#83-token-kidnapping--windows-privilege-escalation)
- [Module 9: Memory Forensics, Threat Detection & Honeypots](#module-9-memory-forensics-threat-detection--honeypots)
  - [9.1 Memory Forensics: The Volatility Framework & VAD Analysis](#91-memory-forensics-the-volatility-framework--vad-analysis)
  - [9.2 Deception Technologies: Honeypots, Honeynets & Honeytokens](#92-deception-technologies-honeypots-honeynets--honeytokens)
- [Module 10: Linux Security Fundamentals: Discretionary Access Control (DAC)](#module-10-linux-security-fundamentals-discretionary-access-control-dac)
  - [10.1 The Linux Multi-User Security Philosophy](#101-the-linux-multi-user-security-philosophy)
  - [10.2 Standard File Permissions & Octal Representation](#102-standard-file-permissions--octal-representation)
  - [10.3 Special Permissions: SUID, SGID & The Sticky Bit](#103-special-permissions-suid-sgid--the-sticky-bit)
  - [10.4 The Umask & POSIX Access Control Lists (ACLs)](#104-the-umask--posix-access-control-lists-acls)
- [Module 11: Linux Mandatory Access Control: SELinux & AppArmor](#module-11-linux-mandatory-access-control-selinux--apparmor)
  - [11.1 The Limitation of DAC & The Need for Mandatory Access Control (MAC)](#111-the-limitation-of-dac--the-need-for-mandatory-access-control-mac)
  - [11.2 The Linux Security Modules (LSM) Kernel Framework](#112-the-linux-security-modules-lsm-kernel-framework)
  - [11.3 SELinux Architecture & Policy](#113-selinux-architecture--policy)
  - [11.4 AppArmor: Path-Based Mandatory Access Control](#114-apparmor-path-based-mandatory-access-control)
- [Module 12: Linux User Authentication, Credentials & PAM](#module-12-linux-user-authentication-credentials--pam)
  - [12.1 Linux Credential Storage: /etc/passwd vs. /etc/shadow](#121-linux-credential-storage-etcpasswd-vs-etcshadow)
  - [12.2 Pluggable Authentication Modules (PAM) Architecture](#122-pluggable-authentication-modules-pam-architecture)
  - [12.3 Hardening Authentication: Account Lockout & Password Complexity](#123-hardening-authentication-account-lockout--password-complexity)
- [Module 13: Linux Process Isolation: Namespaces, Cgroups, Seccomp & Capabilities](#module-13-linux-process-isolation-namespaces-cgroups-seccomp--capabilities)
  - [13.1 Container Isolation Building Blocks: Namespaces & Cgroups](#131-container-isolation-building-blocks-namespaces--cgroups)
  - [13.2 The Seven Core Linux Namespaces](#132-the-seven-core-linux-namespaces)
  - [13.3 Linux Capabilities: Decomposing the Omnipotent Root](#133-linux-capabilities-decomposing-the-omnipotent-root)
  - [13.4 Seccomp & Seccomp-BPF (Secure Computing Mode)](#134-seccomp--seccomp-bpf-secure-computing-mode)
- [Module 14: Linux Network Defense, Auditing & Exploit Hardening](#module-14-linux-network-defense-auditing--exploit-hardening)
  - [14.1 The Netfilter Packet Filtering Architecture: iptables vs. nftables](#141-the-netfilter-packet-filtering-architecture-iptables-vs-nftables)
  - [14.2 Secure Shell (SSH) Host Hardening](#142-secure-shell-ssh-host-hardening)
  - [14.3 The Linux Auditing Framework (auditd)](#143-the-linux-auditing-framework-auditd)
  - [14.4 Linux Kernel Exploit Mitigations & Sysctl Hardening](#144-linux-kernel-exploit-mitigations--sysctl-hardening)
- [Module 15: Master Technical Glossary & Comprehensive Acronym Index](#module-15-master-technical-glossary--comprehensive-acronym-index)

---
"""

module15_content = """# Module 15: Master Technical Glossary & Comprehensive Acronym Index

## 15.1 Master Cyber Security & Linux Technical Glossary

- **Access Control Entry (ACE)**: An individual record within an Access Control List (ACL) granting or denying specific access permissions to a specified trustee (user or group).
- **Access Control List (ACL)**: An ordered collection of Access Control Entries accompanying a file, directory, or object that defines access rights for users and groups.
- **Access Vector Cache (AVC)**: The high-speed kernel lookup cache in SELinux that stores recent security policy decisions to accelerate system call performance.
- **Address Space Layout Randomization (ASLR)**: An exploit mitigation technique that randomizes the memory addresses of program execution components (stack, heap, shared libraries), preventing attackers from jumping to fixed payload addresses.
- **AppArmor**: A Linux Security Module providing path-based Mandatory Access Control, confining programs based on profiles configured in `/etc/apparmor.d/`.
- **Botnet**: A network of compromised computers or devices (bots) controlled remotely by a cyber adversary (botmaster) through a Command and Control (C2) infrastructure.
- **Control Groups (cgroups)**: A Linux kernel feature providing resource allocation, prioritization, accounting, and throttling (CPU, memory, disk I/O, network) for groups of processes.
- **Data Execution Prevention (DEP / NX)**: A hardware-enforced or software mitigation that marks memory pages (such as stack and heap) as non-executable, preventing code execution from data segments.
- **Direct Kernel Object Manipulation (DKOM)**: An advanced kernel-mode rootkit technique that alters internal kernel data structures directly in memory (e.g., unlinking an `EPROCESS` block from the active process list) to hide artifacts without modifying code.
- **Discretionary Access Control (DAC)**: An access policy where resource owners possess the architectural discretion to grant or deny access rights to other subjects.
- **Fast-Flux DNS**: A DNS evasion technique where the IP addresses associated with a Fully Qualified Domain Name rapidly cycle across thousands of compromised hosts with extremely short TTL values.
- **Format String Vulnerability**: A software vulnerability occurring when untrusted user input is passed as the format argument to variadic C output functions, enabling arbitrary memory reading and writing via `%x` and `%n`.
- **Import Address Table (IAT)**: A memory lookup structure within Portable Executable (PE) files holding runtime function pointers to external Dynamic Link Libraries.
- **Linux Capabilities**: Distinct privilege units that decompose the omnipotent authority of the traditional UNIX root user into independent, granular slices.
- **Linux Security Modules (LSM)**: A framework inside the Linux kernel allowing security extensions (SELinux, AppArmor, Smack) to register hooks across critical system call paths.
- **Mandatory Access Control (MAC)**: A centrally administered security policy enforced by the operating system kernel that cannot be altered or bypassed by individual resource owners or the root user.
- **Namespaces**: A Linux kernel technology providing virtualized abstractions of global system resources (PIDs, Mount points, Network stacks, IPC, UTS, UIDs) to isolated process groups.
- **Netfilter**: The packet-filtering framework embedded within the Linux kernel providing hooks (`PREROUTING`, `INPUT`, `FORWARD`, `OUTPUT`, `POSTROUTING`) for firewall rules and NAT.
- **Pluggable Authentication Modules (PAM)**: A flexible modular authentication architecture on UNIX/Linux systems enabling administrators to alter authentication policies without modifying client binaries.
- **Reflective DLL Injection**: A stealth DLL injection technique where a DLL manually maps its own sections and executes relocations directly from memory without calling `LoadLibrary` or leaving disk artifacts.
- **Rootkit**: Stealth malware designed to conceal malicious processes, network sockets, and files from operating system APIs and monitoring utilities.
- **Seccomp (Secure Computing Mode)**: A Linux security facility that restricts the allowable system calls a process can issue to the kernel, reducing kernel exploit surface.
- **Security Context (SELinux)**: The immutable security label formatted as `user:role:type:level` assigned to every process and object under SELinux.
- **Security Identifier (SID)**: A variable-length unique binary string identifying security principals (users, groups, computers) in Microsoft Windows.
- **Set User ID (SUID)**: A special UNIX permission bit (`04000`) instructing the operating system to execute a binary with the privileges of the file owner rather than the calling user.
- **Time-of-Check to Time-of-Use (TOCTOU)**: A race condition vulnerability occurring when the state of a resource changes between the moment it is verified and the moment it is accessed.
- **Virtual Address Descriptor (VAD)**: A binary search tree in the Windows kernel tracking the allocated virtual memory ranges and page protections for a process.

---

## 15.2 Comprehensive Acronym Master Index

| Acronym | Expansion | Technological Domain |
| :--- | :--- | :--- |
| **ABAC** | Attribute-Based Access Control | Access Control Architectures |
| **ACE** | Access Control Entry | Operating System Security |
| **ACL** | Access Control List | Discretionary Access Control |
| **AES** | Advanced Encryption Standard | Symmetric Cryptography |
| **API** | Application Programming Interface | Software Engineering |
| **ASLR** | Address Space Layout Randomization | Exploit Mitigations |
| **AVC** | Access Vector Cache | SELinux Architecture |
| **BHO** | Browser Helper Object | Windows Web Exploits |
| **BPF** | Berkeley Packet Filter | Linux Kernel Tracing / Seccomp |
| **C2** | Command and Control | Threat Infrastructure |
| **CA** | Certificate Authority | Public Key Infrastructure |
| **CBC** | Cipher Block Chaining | Block Cipher Modes |
| **CIA** | Confidentiality, Integrity, Availability | Information Assurance |
| **CSP** | Content Security Policy | Web Application Security |
| **DAC** | Discretionary Access Control | Operating System Security |
| **DACL** | Discretionary Access Control List | Windows Security |
| **DDoS** | Distributed Denial of Service | Network Security |
| **DEP** | Data Execution Prevention | Hardware Exploit Mitigations |
| **DGA** | Domain Generation Algorithm | Malware Threat Infrastructure |
| **DKOM** | Direct Kernel Object Manipulation | Kernel Rootkit Engineering |
| **DLL** | Dynamic Link Library | Windows Operating System |
| **DNS** | Domain Name System | Network Infrastructure |
| **DNSSEC**| Domain Name System Security Extensions | Network Security |
| **DoS** | Denial of Service | Network Security |
| **EBP** | Extended Base Pointer | x86 Processor Architecture |
| **ECC** | Elliptic Curve Cryptography | Asymmetric Cryptography |
| **EIP** | Extended Instruction Pointer | x86 Processor Architecture |
| **ESP** | Extended Stack Pointer | x86 Processor Architecture |
| **FQDN** | Fully Qualified Domain Name | Network Infrastructure |
| **GCM** | Galois/Counter Mode | Authenticated Encryption |
| **GID** | Group Identifier | Linux Access Control |
| **GUI** | Graphical User Interface | System Software |
| **HMAC** | Hash-based Message Authentication Code | Cryptographic Data Integrity |
| **HTTP** | Hypertext Transfer Protocol | Web Protocols |
| **HTTPS**| Hypertext Transfer Protocol Secure | Transport Layer Security |
| **IA** | Information Assurance | Enterprise Security Standards |
| **IAT** | Import Address Table | Windows PE Format |
| **ICMP** | Internet Control Message Protocol | Network Protocols |
| **IDS** | Intrusion Detection System | Network Defense |
| **IP** | Internet Protocol | Network Layer Protocol |
| **IPC** | Inter-Process Communication | Operating System Architecture |
| **KASLR** | Kernel Address Space Layout Randomization | Kernel Exploit Mitigations |
| **KPTI** | Kernel Page Table Isolation | Hardware Speculation Defenses |
| **LSASS** | Local Security Authority Subsystem Service | Windows Authentication |
| **LSM** | Linux Security Modules | Linux Kernel Architecture |
| **MAC** | Mandatory Access Control / Message Authentication Code | Access Control / Cryptography |
| **MFA** | Multi-Factor Authentication | Identity & Access Management |
| **MLS** | Multi-Level Security | Mandatory Access Control |
| **NAT** | Network Address Translation | Network Routing |
| **NGFW** | Next-Generation Firewall | Network Security Perimeters |
| **NTP** | Network Time Protocol | Network Protocols |
| **NX** | No-Execute Bit | CPU Architecture |
| **OSINT** | Open-Source Intelligence | Threat Reconnaissance |
| **PAM** | Pluggable Authentication Modules | Linux Authentication |
| **P2P** | Peer-to-Peer | Distributed Architectures |
| **PE** | Portable Executable | Windows Binary Format |
| **PEB** | Process Environment Block | Windows Process Internals |
| **PID** | Process Identifier | Operating System Management |
| **POSIX** | Portable Operating System Interface | System Standards |
| **PPC** | Pay-Per-Click | Digital Advertising / Fraud |
| **RAM** | Random Access Memory | Physical Memory Architecture |
| **RAT** | Remote Access Trojan | Malware Engineering |
| **RBAC** | Role-Based Access Control | Access Control Architectures |
| **RFC** | Request for Comments | Internet Standards |
| **RFID** | Radio-Frequency Identification | Wireless Hardware Security |
| **ROP** | Return-Oriented Programming | Advanced Binary Exploitation |
| **RSA** | Rivest-Shamir-Adleman | Asymmetric Cryptography |
| **SACL** | System Access Control List | Windows Security Auditing |
| **SELinux**| Security-Enhanced Linux | Mandatory Access Control |
| **SHA** | Secure Hash Algorithm | Cryptographic Hash Functions |
| **SID** | Security Identifier | Windows Security Model |
| **SMB** | Server Message Block | Network Protocols |
| **SOCKS** | Socket Secure Protocol | Proxy Networking |
| **SPDM** | Security Protocol and Data Model | Peripheral Security |
| **SQL** | Structured Query Language | Relational Database Systems |
| **SQLi** | SQL Injection | Web Application Exploits |
| **SRM** | Security Reference Monitor | Windows Kernel Subsystems |
| **SSDT** | System Service Descriptor Table | Windows Kernel Internals |
| **SSH** | Secure Shell | Secure Remote Administration |
| **SSP** | Stack Smashing Protection (Canaries) | Compiler Exploit Mitigations |
| **SUID** | Set User ID | UNIX / Linux File Permissions |
| **TCB** | Trusted Computing Base | Platform Security Architecture |
| **TCP** | Transmission Control Protocol | Transport Layer Protocol |
| **TLS** | Transport Layer Security | Cryptographic Transport Security |
| **TOCTOU** | Time-of-Check to Time-of-Use | Concurrency Vulnerabilities |
| **TOR** | The Onion Router | Anonymity Networks |
| **TTL** | Time-To-Live | Network Protocols / DNS |
| **UDP** | User Datagram Protocol | Transport Layer Protocol |
| **UID** | User Identifier | Linux Access Control |
| **UIPI** | User Interface Privilege Isolation | Windows GUI Security |
| **VAD** | Virtual Address Descriptor | Windows Memory Architecture |
| **VMM** | Virtual Machine Monitor (Hypervisor) | Virtualization Infrastructure |
| **XSS** | Cross-Site Scripting | Web Application Exploits |

---
"""

# Read all modules 1 to 14
modules_text = []
for i in range(1, 15):
    filename = os.path.join(MODULES_DIR, f"module{i}.md")
    with open(filename, "r") as f:
        modules_text.append(f.read().strip())

# Combine into master document
master_content = preface.strip() + "\n\n"
for mod in modules_text:
    master_content += mod + "\n\n---\n\n"
master_content += module15_content.strip() + "\n"

with open(OUTPUT_FILE, "w") as f:
    f.write(master_content)

print(f"Master guide successfully generated at: {OUTPUT_FILE}")

# Calculate statistics
words = len(re.findall(r'\\b\\w+\\b', master_content))
lines = len(master_content.splitlines())
chars = len(master_content)
pages_approx = words / 425

print(f"Total Lines: {lines}")
print(f"Total Words: {words}")
print(f"Total Characters: {chars}")
print(f"Estimated Standard Technical Pages (~425 words/page): {pages_approx:.1f} pages")
