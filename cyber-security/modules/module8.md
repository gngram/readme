# Module 8: Advanced Malware Capabilities & Privilege Escalation

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
    Injector->>Kernel: WriteProcessMemory(hProcess, pRemoteBuf, "C:\malware.dll")
    Injector->>Kernel: GetProcAddress("kernel32.dll", "LoadLibraryW")
    Kernel-->>Injector: Returns address of LoadLibraryW (Same across processes!)
    Injector->>Kernel: CreateRemoteThread(hProcess, NULL, 0, LoadLibraryW, pRemoteBuf, 0, NULL)
    Note over Target: Remote Thread spawns inside explorer.exe executing LoadLibraryW("C:\malware.dll")!
    Target->>Target: Injected DLL DllMain() executes with explorer.exe privileges!
```

### Injection Variants
1. **Classic DLL Injection (`CreateRemoteThread`)**:
   - Outlined in the diagram above. Requires `PROCESS_ALL_ACCESS` permissions.
2. **AppInit_DLLs Registry Injection**:
   - The registry key `HKLM\Software\Microsoft\Windows NT\CurrentVersion\Windows\AppInit_DLLs` allows specifying custom DLLs that are automatically loaded into *every* user-mode GUI process that links with `user32.dll`.
3. **Reflective DLL Injection (Stephen Fewer Technique)**:
   - Traditional DLL injection leaves artifacts on the hard disk and registers the DLL in the target process's `InLoadOrderModuleList` (visible to PEB inspection).
   - *Reflective Injection* writes the raw PE binary of the DLL directly into remote process memory from a memory buffer. The DLL contains an exported bootstrapping function (`ReflectiveLoader`) that manually maps its own sections, resolves imports, executes base relocations, and invokes `DllMain` entirely in memory without ever calling `LoadLibrary` or touching disk.

---

## 8.3 Token Kidnapping & Windows Privilege Escalation

Windows services frequently execute under service accounts (such as `NT AUTHORITY\NETWORK SERVICE` or `LOCAL SERVICE`). While these accounts lack administrative powers, they frequently hold the sensitive **`SeImpersonatePrivilege`** or **`SeAssignPrimaryTokenPrivilege`**.

```mermaid
graph TD
    subgraph Token_Kidnapping_Flow["Token Kidnapping Privilege Escalation Workflow"]
        direction TB
        
        Compromised["Service Process Compromised (NETWORK SERVICE)<br/>Possesses SeImpersonatePrivilege"]
        NamedPipe["Attacker creates local Named Pipe (\\.\pipe\privesc)"]
        Coerce["Coerces SYSTEM Service (e.g., Print Spooler / RPC) to connect to Pipe"]
        Impersonate["Invokes ImpersonateNamedPipeClient()<br/>Temporarily adopts SYSTEM Token on thread!"]
        Duplicate["DuplicateTokenEx() creates Primary SYSTEM Token"]
        CreateProc["CreateProcessWithTokenW(hToken, 'cmd.exe')<br/>Spawns interactive shell as NT AUTHORITY\SYSTEM!"]
        
        Compromised --> NamedPipe --> Coerce --> Impersonate --> Duplicate --> CreateProc
    end
    
    style Token_Kidnapping_Flow fill:#fdfefe,stroke:#2c3e50,stroke-width:2px;
    style Compromised fill:#fef9e7,stroke:#f39c12,stroke-width:2px;
    style Impersonate fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
    style CreateProc fill:#d4efdf,stroke:#27ae60,stroke-width:2px;
```

### Exploitation Mechanics
- **Token Impersonation**: A thread executing in a service process can call `ImpersonateNamedPipeClient()` or `ImpersonateLoggedOnUser()` to adopt the security identity of an incoming client connection.
- Tools like **RottenPotato**, **JuicyPotato**, and **PrintSpoofer** coerce high-privilege system services (such as the DCOM activator or Print Spooler) into authenticating against a local named pipe or RPC endpoint controlled by the low-privileged process, instantly capturing a token for `NT AUTHORITY\SYSTEM`.

---
