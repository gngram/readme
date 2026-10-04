#!/usr/bin/env python3
"""
Enrichment Part 2 for Cyber Security & Linux Security modules.
Adds hands-on C2 packet formats, Tor cell headers, PEB anti-debug structures,
complete Volatility commands, Linux custom container from scratch, and PAM MFA.
"""

import os

mod3_enrichment = """

---

## 3.5 Network Protocol Dissection: SOCKS5 Handshake & Tor Cells

### 1. SOCKS5 Protocol Specification (RFC 1928)
Unlike HTTP proxies that operate at Layer 7, SOCKS5 operates at Layer 5, facilitating arbitrary TCP/UDP streaming without protocol inspection.

```
1. Client Version Identification & Method Selection Request:
+----+----------+----------+
|VER | NMETHODS | METHODS  |
+----+----------+----------+
| 1  |    1     | 1 to 255 |
+----+----------+----------+
• VER: 0x05 (SOCKS5)
• NMETHODS: Number of authentication methods supported
• METHODS: 0x00 (No Authentication), 0x02 (Username/Password)

2. Server Method Selection Response:
+----+--------+
|VER | METHOD |
+----+--------+
| 1  |   1    |
+----+--------+
• Returns selected method (e.g., 0x00 or 0xFF if no acceptable methods)

3. Client Connection Request (e.g., CONNECT to target C2):
+----+-----+-------+------+----------+----------+
|VER | CMD |  RSV  | ATYP | DST.ADDR | DST.PORT |
+----+-----+-------+------+----------+----------+
| 1  |  1  | X'00' |  1   | Variable |    2     |
+----+-----+-------+------+----------+----------+
• CMD: 0x01 (CONNECT), 0x02 (BIND), 0x03 (UDP ASSOCIATE)
• ATYP: 0x01 (IPv4 - 4 bytes), 0x03 (Domain name), 0x04 (IPv6 - 16 bytes)
• DST.ADDR & DST.PORT: Final target address and port
```

### 2. Tor Fixed-Size 512-Byte Cell Structure
Tor mitigates packet-size statistical traffic analysis by packing all network commands into uniform 512-byte **Cells**:
```
+---------------------------------------------------------------------------------+
| Circuit ID (CircID: 2 or 4 Bytes) | Command (1 Byte) | Payload (509 or 507 Bytes)|
+---------------------------------------------------------------------------------+
```
- **Control Cells**: Handled directly by the receiving node (`CREATE`, `CREATED`, `DESTROY`, `PADDING`).
- **Relay Cells**: Encapsulated end-to-end data streams (`RELAY_BEGIN`, `RELAY_DATA`, `RELAY_END`, `RELAY_EXTEND`).
"""

mod7_enrichment = """

---

## 7.5 Deep Low-Level Anti-Debugging: PEB & Kernel Flags

### 1. The Process Environment Block (PEB) Inspection
Adversaries query the PEB without invoking Win32 APIs (which might be hooked by EDR solutions):
```assembly
; Reading PEB BeingDebugged on 32-bit Windows
mov eax, fs:[0x30]        ; FS register points to TEB; offset 0x30 is pointer to PEB
movzx eax, byte [eax + 2] ; Offset 0x02 is BeingDebugged byte
test eax, eax
jnz debugger_detected

; Reading PEB BeingDebugged on 64-bit Windows
mov rax, gs:[0x60]        ; GS register points to TEB; offset 0x60 is pointer to PEB
movzx eax, byte [rax + 2]
test eax, eax
jnz debugger_detected
```

### 2. The `NtGlobalFlag` Signature
When a process is launched under a debugger, the Windows heap manager sets specific flags in the `NtGlobalFlag` field (`PEB + 0x68` in 32-bit, `PEB + 0xBC` in 64-bit):
- `FLG_HEAP_ENABLE_TAIL_CHECK` (`0x10`): Appends canary patterns to heap allocations.
- `FLG_HEAP_ENABLE_FREE_CHECK` (`0x20`): Verifies memory blocks upon deallocation.
- `FLG_HEAP_VALIDATE_PARAMETERS` (`0x40`): Validates parameters passed to heap functions.
- If `NtGlobalFlag == (0x10 | 0x20 | 0x40) == 0x70`, an attached debugger is flagged.
"""

mod9_enrichment = """

---

## 9.3 Practical Memory Forensics Command Reference (Volatility 3)

The following master table provides the essential forensic triage commands for volatile RAM analysis:

| Forensic Objective | Volatility 3 Command | Analytical Target & Anomaly Detection |
| :--- | :--- | :--- |
| **Kernel & OS Identification** | `vol -f mem.raw windows.info` | Discovers architecture, build number, and Kernel Directory Table Base (CR3). |
| **Process Tree Enumeration** | `vol -f mem.raw windows.pstree` | Displays parent-child process relationships (detects abnormal parent processes). |
| **DKOM Rootkit Detection** | `vol -f mem.raw windows.psscan` | Scans raw memory pool tags to find unlinked / hidden processes. |
| **Cross-Validation** | `vol -f mem.raw windows.psxview` | Flags discrepancies across 7 internal kernel process structures. |
| **Injected Code Detection** | `vol -f mem.raw windows.malfind` | Scans VAD trees for unbacked `PAGE_EXECUTE_READWRITE` memory containing code. |
| **Network Sockets** | `vol -f mem.raw windows.netscan` | Enumerates active and terminated TCP/UDP endpoints, foreign IPs, and PIDs. |
| **Command Line Arguments** | `vol -f mem.raw windows.cmdline` | Extracts process launch arguments (detects obfuscated PowerShell commands). |
| **Dump Injected PE Executable**| `vol -f mem.raw windows.vaddump --pid <PID>` | Dumps injected memory segments to disk for reverse engineering. |
"""

mod12_enrichment = """

---

## 12.4 Enterprise MFA Integration: PAM Google Authenticator Hardening

To enforce Multi-Factor Authentication (MFA) across SSH and local logins, Linux integrates Time-Based One-Time Password (TOTP, RFC 6238) engines:

```bash
# 1. Install Google Authenticator PAM engine
apt-get install libpam-google-authenticator -y

# 2. User initialization (generates QR code and emergency scratch codes)
google-authenticator -t -d -f -r 3 -R 30 -W

# 3. Configure /etc/pam.d/sshd:
# Prepend TOTP module to authentication stack:
auth required pam_google_authenticator.so nullok

# 4. Configure /etc/ssh/sshd_config:
KbdInteractiveAuthentication yes
AuthenticationMethods publickey,keyboard-interactive
```
When authenticating, the user must present BOTH a valid cryptographic SSH private key AND a 6-digit TOTP code generated on their hardware token or smartphone app.
"""

mod13_enrichment = """

---

## 13.5 Building a Container from Scratch using Linux Primitives

To demystify containerization, one can instantiate a fully isolated container using core Linux kernel system commands without Docker:

```bash
#!/usr/bin/env bash
# Building a minimal isolated Linux container from scratch

ROOTFS="/tmp/my_container_rootfs"
CGROUP_DIR="/sys/fs/cgroup/demo_container"

# 1. Create Control Group (cgroups v2) and enforce limits
mkdir -p "$CGROUP_DIR"
echo "50000 100000" > "$CGROUP_DIR/cpu.max"       # Limit to 0.5 CPU core
echo "104857600"      > "$CGROUP_DIR/memory.max"    # Limit to 100 MB RAM
echo "20"             > "$CGROUP_DIR/pids.max"      # Max 20 processes

# 2. Execute workload in private PID, Network, Mount, UTS, and IPC Namespaces
# unshare isolates namespaces, pivot_root isolates filesystem
unshare --mount --uts --ipc --net --pid --fork bash -c "
    # Assign process to cgroup
    echo \$\$ > $CGROUP_DIR/cgroup.procs

    # Set private hostname
    hostname containerized-secure-host

    # Mount private /proc inside container mount namespace
    mount -t proc proc /proc

    # Execute isolated container shell
    exec /bin/sh
"
```
"""

def append_to_file(path, content):
    with open(path, "a") as f:
        f.write(content.strip() + "\n")

append_to_file("cyber-security/modules/module3.md", mod3_enrichment)
append_to_file("cyber-security/modules/module7.md", mod7_enrichment)
append_to_file("cyber-security/modules/module9.md", mod9_enrichment)
append_to_file("cyber-security/modules/module12.md", mod12_enrichment)
append_to_file("cyber-security/modules/module13.md", mod13_enrichment)

print("Appended Part 2 enrichments successfully.")
