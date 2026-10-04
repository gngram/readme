#!/usr/bin/env python3
"""
Generator for Modules 8 to 10 of the Cyber Security Essentials & Linux Security Guide.
"""

import os

os.makedirs("cyber-security/modules", exist_ok=True)

module8_content = """# Module 8: Advanced Malware Capabilities & Privilege Escalation

## 8.1 Rootkit Architectures: User-Mode vs. Kernel-Mode

A **Rootkit** is a specialized stealth cloaking technology designed to conceal the presence of unauthorized running processes, network sockets, files, and registry keys from the operating system, antivirus tools, and system administrators.

```mermaid
graph TD
    subgraph Rootkit_Taxonomy["User-Mode vs Kernel-Mode Rootkit Hooking Topologies"]
        direction TB
        
        subgraph User_Space["User Space (Ring 3)"]
            TaskMgr["Taskmgr.exe / Process Explorer"]
            subgraph User_Rootkit["User-Mode Rootkit Hooking"]
                IAT_Hook["1. IAT Hooking<br/>Modifies Import Address Table pointers in memory"]
                Inline_Hook["2. Inline API Hooking (Detours)<br/>Overwrites first 5 bytes of target function with JMP opcode"]
            end
            TaskMgr --> IAT_Hook
            TaskMgr --> Inline_Hook
            IAT_Hook --> NTDLL["ntdll.dll (NtQuerySystemInformation)"]
            Inline_Hook --> NTDLL
        end
        
        subgraph Kernel_Space["Kernel Space (Ring 0)"]
            NTDLL -->|"Syscall (sysenter / syscall)"| SSDT["System Service Descriptor Table (SSDT)"]
            
            subgraph Kernel_Rootkit["Kernel-Mode Rootkit Hooking"]
                SSDT_Hook["3. SSDT Hooking<br/>Replaces kernel system call function pointers in SSDT"]
                DKOM["4. Direct Kernel Object Manipulation (DKOM)<br/>Unlinks EPROCESS block from kernel doubly-linked active process list!"]
            end
            
            SSDT --> SSDT_Hook
            SSDT_Hook --> KernelProc["Real Kernel Process Handlers"]
            DKOM -.->|"Manipulates directly"| KernelProc
        end
    end
    
    style Rootkit_Taxonomy fill:#fdfefe,stroke:#2c3e50,stroke-width:2px;
    style User_Rootkit fill:#ebf5fb,stroke:#2980b9,stroke-width:2px;
    style Kernel_Rootkit fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
```

### Hooking & Cloaking Mechanisms
1. **User-Mode Rootkits (Ring 3)**:
   - Operate inside the virtual address space of user processes.
   - *Import Address Table (IAT) Hooking*: When an executable links to an external DLL, it resolves function pointers through the IAT. A user-mode rootkit replaces the function pointer of `NtQuerySystemInformation` in the IAT with a pointer to its malicious filter function. When Task Manager queries running processes, the rootkit intercepts the returned array, deletes its own process record, and returns the scrubbed list.
   - *Inline Hooking (Detours / Trampolines)*: Replaces the first 5 bytes (the function prologue, e.g., `mov edi, edi; push ebp; mov ebp, esp`) of the target API function in memory with an unconditional `JMP` instruction directing execution to the rootkit's hook.
2. **Kernel-Mode Rootkits (Ring 0)**:
   - Execute with supreme architectural privilege in the Windows or Linux kernel.
   - *SSDT Hooking (System Service Descriptor Table)*: The SSDT contains kernel dispatch function pointers. Hooking the SSDT allows the rootkit to filter all system calls system-wide before user mode ever receives data. (Mitigated in 64-bit Windows via Kernel Patch Protection / PatchGuard).
   - *Direct Kernel Object Manipulation (DKOM)*: Every active process in the Windows kernel is represented by an `EPROCESS` structure. All `EPROCESS` blocks are linked in a circular, doubly-linked list (`ActiveProcessLinks.Flink` and `Blink`). A DKOM rootkit modifies the pointers of the adjacent processes to point to each other, unlinking the rootkit's `EPROCESS` from the list. The process remains fully scheduled by the CPU dispatcher, but disappears completely from all enumeration APIs.

---

## 8.2 DLL Injection Techniques

**DLL Injection** is an exploitation technique that forces a running remote process to load an arbitrary Dynamic Link Library (DLL) into its own virtual address space, executing malicious code under the legitimate process's security context.

```mermaid
sequenceDiagram
    autonumber
    participant Injector as Attacker Injector Process
    participant Kernel as Windows Kernel
    participant Target as Target Legitimate Process (e.g., explorer.exe)

    Injector->>Kernel: OpenProcess(PROCESS_ALL_ACCESS, target_PID)
    Kernel-->>Injector: Returns Process Handle (hProcess)
    Injector->>Kernel: VirtualAllocEx(hProcess, MEM_COMMIT, PAGE_READWRITE)
    Kernel-->>Injector: Allocates remote memory buffer (pRemoteBuf)
    Injector->>Kernel: WriteProcessMemory(hProcess, pRemoteBuf, "C:\\malware.dll")
    Injector->>Kernel: GetProcAddress("kernel32.dll", "LoadLibraryW")
    Kernel-->>Injector: Returns address of LoadLibraryW (Same across processes!)
    Injector->>Kernel: CreateRemoteThread(hProcess, NULL, 0, LoadLibraryW, pRemoteBuf, 0, NULL)
    Note over Target: Remote Thread spawns inside explorer.exe executing LoadLibraryW("C:\\malware.dll")!
    Target->>Target: Injected DLL DllMain() executes with explorer.exe privileges!
```

### Injection Variants
1. **Classic DLL Injection (`CreateRemoteThread`)**:
   - Outlined in the diagram above. Requires `PROCESS_ALL_ACCESS` permissions.
2. **AppInit_DLLs Registry Injection**:
   - The registry key `HKLM\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Windows\\AppInit_DLLs` allows specifying custom DLLs that are automatically loaded into *every* user-mode GUI process that links with `user32.dll`.
3. **Reflective DLL Injection (Stephen Fewer Technique)**:
   - Traditional DLL injection leaves artifacts on the hard disk and registers the DLL in the target process's `InLoadOrderModuleList` (visible to PEB inspection).
   - *Reflective Injection* writes the raw PE binary of the DLL directly into remote process memory from a memory buffer. The DLL contains an exported bootstrapping function (`ReflectiveLoader`) that manually maps its own sections, resolves imports, executes base relocations, and invokes `DllMain` entirely in memory without ever calling `LoadLibrary` or touching disk.

---

## 8.3 Token Kidnapping & Windows Privilege Escalation

Windows services frequently execute under service accounts (such as `NT AUTHORITY\\NETWORK SERVICE` or `LOCAL SERVICE`). While these accounts lack administrative powers, they frequently hold the sensitive **`SeImpersonatePrivilege`** or **`SeAssignPrimaryTokenPrivilege`**.

```mermaid
graph TD
    subgraph Token_Kidnapping_Flow["Token Kidnapping Privilege Escalation Workflow"]
        direction TB
        
        Compromised["Service Process Compromised (NETWORK SERVICE)<br/>Possesses SeImpersonatePrivilege"]
        NamedPipe["Attacker creates local Named Pipe (\\\\.\\pipe\\privesc)"]
        Coerce["Coerces SYSTEM Service (e.g., Print Spooler / RPC) to connect to Pipe"]
        Impersonate["Invokes ImpersonateNamedPipeClient()<br/>Temporarily adopts SYSTEM Token on thread!"]
        Duplicate["DuplicateTokenEx() creates Primary SYSTEM Token"]
        CreateProc["CreateProcessWithTokenW(hToken, 'cmd.exe')<br/>Spawns interactive shell as NT AUTHORITY\\SYSTEM!"]
        
        Compromised --> NamedPipe --> Coerce --> Impersonate --> Duplicate --> CreateProc
    end
    
    style Token_Kidnapping_Flow fill:#fdfefe,stroke:#2c3e50,stroke-width:2px;
    style Compromised fill:#fef9e7,stroke:#f39c12,stroke-width:2px;
    style Impersonate fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
    style CreateProc fill:#d4efdf,stroke:#27ae60,stroke-width:2px;
```

### Exploitation Mechanics
- **Token Impersonation**: A thread executing in a service process can call `ImpersonateNamedPipeClient()` or `ImpersonateLoggedOnUser()` to adopt the security identity of an incoming client connection.
- Tools like **RottenPotato**, **JuicyPotato**, and **PrintSpoofer** coerce high-privilege system services (such as the DCOM activator or Print Spooler) into authenticating against a local named pipe or RPC endpoint controlled by the low-privileged process, instantly capturing a token for `NT AUTHORITY\\SYSTEM`.

---
"""

module9_content = """# Module 9: Memory Forensics, Threat Detection & Honeypots

## 9.1 Memory Forensics: The Volatility Framework & VAD Analysis

When investigating advanced persistent threats (APTs) deploying fileless malware, reflective DLL injection, or unlinked DKOM processes, disk forensics reveals zero evidence. The ground truth of system state resides in **volatile physical memory (RAM)**.

```mermaid
graph TD
    subgraph Memory_Forensics_Workflow["Volatile Memory Forensics & Rootkit Detection Pipeline"]
        direction TB
        
        Dump["Physical Memory Acquisition<br/>(Raw RAM Dump: WinPmem, LiME, VMware .vmem)"]
        
        subgraph Volatility_Engine["Volatility Analysis Engine"]
            Detect_OS["imageinfo / windows.info (Identifies OS Profile & Kernel DTB)"]
            
            subgraph Process_Triage["Cross-Checking Process Enumeration"]
                PsList["pslist: Walks ActiveProcessLinks<br/>(Standard doubly-linked list)"]
                PsScan["psscan: Scans raw RAM for EPROCESS pool tags<br/>(Finds unlinked / hidden processes!)"]
                PsXView["psxview: Cross-references 7 process sources<br/>(Flags DKOM anomalies: False in pslist, True in psscan)"]
            end
            
            subgraph Deep_Analysis["Deep Memory Inspection"]
                Malfind["malfind: Scans VAD trees for PAGE_EXECUTE_READWRITE memory containing MZ headers or shellcode"]
                VadDump["vaddump: Extracts injected code segments directly from RAM"]
            end
        end
        
        Dump --> Detect_OS --> Process_Triage --> Deep_Analysis
    end
    
    style Memory_Forensics_Workflow fill:#f9f9f9,stroke:#34495e,stroke-width:2px;
    style Process_Triage fill:#ebf5fb,stroke:#2980b9,stroke-width:2px;
    style Deep_Analysis fill:#fef9e7,stroke:#f39c12,stroke-width:2px;
```

### Core Volatility Analysis Modules
1. **Process Discovery Cross-Validation (`psxview`)**:
   - DKOM rootkits unlink processes from `ActiveProcessLinks` (making them invisible to `pslist` and Task Manager).
   - `psscan` ignores the linked list, conducting heuristic signature scanning across raw memory bytes searching for `_EPROCESS` pool tag headers (`Proc`).
   - If `psxview` reveals a process marked `False` in `pslist` but `True` in `psscan`, a DKOM rootkit is actively hiding a malicious process.
2. **Virtual Address Descriptor (VAD) Tree Analysis (`malfind`)**:
   - Every Windows process maintains a self-balancing binary search tree (the **VAD Tree**) tracking allocated virtual memory ranges.
   - Legitimate Windows binaries map executable code (`.text`) with `PAGE_EXECUTE_READ` attributes backed by a file on disk.
   - Attackers injecting shellcode allocate private memory marked `PAGE_EXECUTE_READWRITE` (RWX) without backing disk files. The `malfind` plugin traverses the VAD tree searching for RWX allocations containing executable opcodes or PE headers (`MZ`).

---

## 9.2 Deception Technologies: Honeypots, Honeynets & Honeytokens

**Deception technology** shifts the asymmetrical advantage of cyber warfare from the attacker to the defender. While defenders traditionally had to secure every vulnerability, deception creates an environment where an attacker touching a single false asset trips an alarm.

```mermaid
graph TD
    subgraph Deception_Taxonomy["Taxonomy of Deception Systems"]
        direction TB
        
        subgraph Low_Interaction["1. Low-Interaction Honeypots (e.g., Honeyd, Dionaea)"]
            LI_Desc["Simulates listening network services (FTP, SMB, SSH)<br/>• Captures automated exploit payloads & port scans<br/>• Zero real operating system execution; zero risk of compromise"]
        end
        
        subgraph High_Interaction["2. High-Interaction Honeypots (e.g., Real VM Sandboxes)"]
            HI_Desc["Deploys full, real operating systems and applications<br/>• Monitored via out-of-band hypervisor / network taps<br/>• Captures novel zero-day exploits, manual hacker behavior<br/>• High operational maintenance; risk of use as launchpad"]
        end
        
        subgraph Honeytokens["3. Honeytokens / Canaries"]
            HT_Desc["Fictitious data assets planted across production systems:<br/>• Fake AWS API keys in code repos (Canary Tokens)<br/>• Fake database administrator credentials<br/>• Phony sensitive documents with phone-home beacons"]
        end
    end
    
    style Deception_Taxonomy fill:#fdfefe,stroke:#2c3e50,stroke-width:2px;
    style Low_Interaction fill:#ebf5fb,stroke:#2980b9,stroke-width:2px;
    style High_Interaction fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
    style Honeytokens fill:#d4efdf,stroke:#27ae60,stroke-width:2px;
```

---
"""

module10_content = """# Module 10: Linux Security Fundamentals: Discretionary Access Control (DAC)

## 10.1 The Linux Multi-User Security Philosophy & Philosophy of "Everything is a File"

The Linux operating system derives its architectural security lineage from UNIX. Linux enforces isolation through two fundamental axioms:
1. **Multi-User Isolation**: Every process executing on the system is owned by a specific **User ID (UID)** and **Group ID (GID)**. Resource permissions are strictly partitioned between different user accounts.
2. **"Everything is a File"**: Hardware devices (disks, terminals, graphics cards), network sockets, inter-process communication pipes, and kernel state structures (`/proc`, `/sys`) are represented as nodes within a unified hierarchical filesystem tree. Access to system hardware is governed by standard filesystem permissions.

```
Linux User ID Hierarchy:
  UID 0:        root (Superuser / Omnipotent Administrative Authority)
  UID 1 - 999:  System Accounts (daemon, bin, www-data, sshd, nobody)
  UID 1000+:    Standard Interactive User Accounts (alice, bob, developer)
```

---

## 10.2 Standard File Permissions & Octal Representation

Linux **Discretionary Access Control (DAC)** associates a 9-bit permission triplet with every file and directory, dividing subjects into three distinct classes:
- **User / Owner (`u`)**: The specific user account that owns the file.
- **Group (`g`)**: The group identity assigned to the file.
- **Others / World (`o`)**: All other user accounts on the operating system.

```mermaid
graph LR
    subgraph Permission_Bitmask["Anatomy of Linux 12-Bit Permission Mask"]
        direction TB
        Special["Special Bits [11:9]<br/>SUID (4) | SGID (2) | Sticky (1)"]
        User["User Permissions [8:6]<br/>Read (4) | Write (2) | Execute (1)"]
        Group["Group Permissions [5:3]<br/>Read (4) | Write (2) | Execute (1)"]
        Other["Other Permissions [2:0]<br/>Read (4) | Write (2) | Execute (1)"]
        
        Special --- User --- Group --- Other
    end
    
    style Permission_Bitmask fill:#f8f9f9,stroke:#34495e,stroke-width:2px;
    style Special fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
    style User fill:#ebf5fb,stroke:#2980b9,stroke-width:2px;
    style Group fill:#fef9e7,stroke:#f39c12,stroke-width:2px;
    style Other fill:#e8f8f5,stroke:#27ae60,stroke-width:2px;
```

### Semantic Meaning: Files vs. Directories
The operational behavior of the standard permission bits differs fundamentally between regular files and directories:

| Permission Bit | Regular File Semantic | Directory Semantic |
| :---: | :--- | :--- |
| **`r` (Read, Value: 4)** | Permits reading file contents (e.g., `cat`, `less`). | Permits listing files contained in the directory (e.g., `ls`). |
| **`w` (Write, Value: 2)**| Permits modifying or overwriting file contents. | Permits **creating, deleting, or renaming files** within the directory (even files owned by other users!). |
| **`x` (Execute, Value: 1)**| Permits running the file as a program or script. | Permits **entering / traversing** the directory (e.g., `cd`) and accessing metadata of files inside. |

---

## 10.3 Special Permissions: SUID, SGID & The Sticky Bit

In addition to standard read, write, and execute bits, Linux incorporates three high-order **Special Permission Bits**:

```mermaid
graph TD
    subgraph Special_Permissions_Mechanics["Operational Mechanics of Special Permissions"]
        direction TB
        
        subgraph SUID_Box["1. Set User ID (SUID - Value: 4000, 's')"]
            SUID_Desc["When an executable with SUID is run, the process executes with the privileges of the FILE OWNER (usually root), NOT the executing user!<br/>Example: /usr/bin/passwd (Allows normal users to edit /etc/shadow)"]
        end
        
        subgraph SGID_Box["2. Set Group ID (SGID - Value: 2000, 's')"]
            SGID_Desc["• On Executables: Process adopts privileges of the FILE GROUP.<br/>• On Directories: New files created inside automatically inherit the DIRECTORY'S GROUP ownership (Crucial for shared team folders)."]
        end
        
        subgraph Sticky_Box["3. Sticky Bit (Value: 1000, 't')"]
            Sticky_Desc["Applied to world-writable directories (e.g., /tmp).<br/>Restricts file deletion: Users can ONLY delete or rename files that they personally own, preventing users from deleting each other's files!"]
        end
    end
    
    style Special_Permissions_Mechanics fill:#fdfefe,stroke:#2c3e50,stroke-width:2px;
    style SUID_Box fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
    style SGID_Box fill:#fef9e7,stroke:#f39c12,stroke-width:2px;
    style Sticky_Box fill:#d4efdf,stroke:#27ae60,stroke-width:2px;
```

### Security Hazards of SUID Binaries & Privilege Escalation
SUID binaries owned by `root` are primary targets for local privilege escalation:
- If a SUID binary contains a buffer overflow, format string vulnerability, or command injection flaw, an unprivileged local attacker can exploit it to spawn a root shell.
- **GTFOBins Exploitation**: If administrative utilities (e.g., `nmap`, `vim`, `find`, `bash`, `python`) are inadvertently granted SUID root permissions:
  ```bash
  # Exploiting SUID on find to gain immediate root:
  find . -exec /bin/sh -p \\; -quit
  ```
- **Auditing Command**: Defenders audit the system for rogue SUID binaries using:
  ```bash
  find / -perm -4000 -type f -exec ls -la {} \\; 2>/dev/null
  ```

---

## 10.4 The Umask & POSIX Access Control Lists (ACLs)

### 1. Default Creation Permissions & `umask`
When a process creates a new file or directory, the initial permission is determined by masking the default base mode (`0666` for files, `0777` for directories) with the process's **`umask`** (user file-creation mode mask):
$$\\text{Created File Mode} = 0666 \\land (\\neg \\text{umask})$$
$$\\text{Created Directory Mode} = 0777 \\land (\\neg \\text{umask})$$
- A standard secure server `umask` of `0027` results in:
  - Files: `0666 - 0027 = 0640` (`-rw-r-----` : Owner read/write, Group read, Others zero permissions).
  - Directories: `0777 - 0027 = 0750` (`drwxr-x---`).

### 2. POSIX Access Control Lists (ACLs)
Standard DAC permits specifying permissions for only one owner and one group. In enterprise environments, files often require granular access rules for multiple disparate users and groups. **POSIX ACLs** extend DAC without requiring kernel modifications.

```bash
# Inspecting ACLs on a sensitive file:
getfacl /var/log/audit/audit.log

# Granting user 'developer' read and write access without altering file group:
setfacl -m u:developer:rw /var/log/audit/audit.log

# Setting default ACLs on a directory (automatically inherited by future children):
setfacl -d -m g:finance:r-x /shared/finance_reports
```

---
"""

with open("cyber-security/modules/module8.md", "w") as f:
    f.write(module8_content.strip() + "\n")

with open("cyber-security/modules/module9.md", "w") as f:
    f.write(module9_content.strip() + "\n")

with open("cyber-security/modules/module10.md", "w") as f:
    f.write(module10_content.strip() + "\n")

print("Generated Modules 8 to 10 successfully.")
