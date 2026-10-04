#!/usr/bin/env python3
"""
Generator for Modules 11 to 14 of the Cyber Security Essentials & Linux Security Guide.
"""

import os

os.makedirs("cyber-security/modules", exist_ok=True)

module11_content = """# Module 11: Linux Mandatory Access Control: SELinux & AppArmor

## 11.1 The Limitation of DAC & The Need for Mandatory Access Control (MAC)

Standard Linux Discretionary Access Control (DAC) suffers from a catastrophic architectural flaw: **The Omnipotent Root Flaw**.
- In DAC, if an attacker compromises a daemon executing as `root` (or exploits a web server vulnerability where the process owner has write permissions to files), the attacker inherits the full permissions of the resource owner.
- The resource owner possesses the complete "discretion" to modify file permissions, grant public access, or execute destructive commands.
- Under DAC, a vulnerability in a single network service (e.g., Apache HTTP server or BIND DNS) executing as root gives the attacker full control over the entire operating system, enabling them to wipe disks, read `/etc/shadow`, install kernel rootkits, or disable firewall rules.

**Mandatory Access Control (MAC)** solves this vulnerability by enforcing a system-wide security policy defined strictly by the security administrator and hardcoded into the kernel:
- **Even the `root` superuser is bound by MAC policy!**
- If a root-owned web server process is compromised, MAC rules prevent it from reading user home directories, accessing `/etc/shadow`, or binding to unauthorized ports.

```mermaid
graph TD
    subgraph DAC_vs_MAC_Comparison["Security Boundary Comparison: DAC vs MAC"]
        direction LR
        
        subgraph DAC_Model["1. Discretionary Access Control (DAC)"]
            Root_App["Compromised Apache Daemon<br/>(Executing as UID 0: root)"]
            Root_App -->|"Allowed: Root has full access"| Shadow1["/etc/shadow"]
            Root_App -->|"Allowed: Root can write"| Bin1["/bin/bash"]
            Root_App -->|"Allowed: Unrestricted"| SSH_Keys1["/root/.ssh/id_rsa"]
        end
        
        subgraph MAC_Model["2. Mandatory Access Control (SELinux)"]
            Confined_App["Compromised Apache Daemon<br/>(Process Label: httpd_t)"]
            Confined_App -.->|"STRICTLY BLOCKED: AVC Denial"| Shadow2["/etc/shadow (shadow_t)"]
            Confined_App -.->|"STRICTLY BLOCKED: AVC Denial"| Bin2["/bin/bash (bin_t)"]
            Confined_App -->|"ALLOWED by Policy"| HTML["/var/www/html (httpd_sys_content_t)"]
        end
    end
    
    style DAC_Model fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
    style MAC_Model fill:#d4efdf,stroke:#27ae60,stroke-width:2px;
    style HTML fill:#a9dfbf,stroke:#2ecc71,stroke-width:2px;
```

---

## 11.2 The Linux Security Modules (LSM) Kernel Framework

Rather than hardcoding a single security paradigm, the Linux kernel incorporates the **Linux Security Modules (LSM)** framework.

```mermaid
graph TD
    subgraph LSM_Pipeline["Linux Security Modules (LSM) Hooking Architecture"]
        direction TB
        
        Syscall["User-Space Application emits System Call (e.g., open('/etc/shadow'))"]
        Kernel_Entry["Kernel Syscall Dispatcher (sys_open)"]
        DAC_Check{"Standard DAC Check Passed?<br/>(File Permissions rwxr-xr-x)"}
        LSM_Hook["LSM Kernel Hook: security_file_open()<br/>(Invoked immediately after DAC passes)"]
        MAC_Policy{"Active LSM Engine (SELinux / AppArmor)<br/>Does Policy Permit Subject to Access Object?"}
        Hardware_Access["VFS Layer Grants Access to Inode / Data"]
        EACCES["System Call Fails: EACCES (Permission Denied)"]
        
        Syscall --> Kernel_Entry --> DAC_Check
        DAC_Check -->|NO| EACCES
        DAC_Check -->|YES| LSM_Hook --> MAC_Policy
        MAC_Policy -->|PERMIT| Hardware_Access
        MAC_Policy -->|DENY| EACCES
    end
    
    style LSM_Pipeline fill:#f9f9f9,stroke:#34495e,stroke-width:2px;
    style DAC_Check fill:#fef9e7,stroke:#f39c12,stroke-width:2px;
    style MAC_Policy fill:#ebf5fb,stroke:#2980b9,stroke-width:2px;
    style Hardware_Access fill:#d4efdf,stroke:#27ae60,stroke-width:2px;
    style EACCES fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
```

### LSM Hook Mechanics
- LSM inserts security hooks at critical decision points across the Linux virtual filesystem (VFS), process lifecycle management, socket communications, and IPC.
- Whenever a user process invokes a system call, the kernel first executes standard DAC checks.
- If DAC passes, the kernel invokes the registered **LSM hook** (e.g., `security_file_open()`, `security_socket_create()`).
- The active MAC security engine (SELinux, AppArmor, or Smack) evaluates its internal security policy and returns either `0` (allow) or `-EACCES` (deny).

---

## 11.3 SELinux (Security-Enhanced Linux) Architecture & Policy

Originally designed by the United States National Security Agency (NSA) and Red Hat, **SELinux** is a comprehensive, Type Enforcement-based Mandatory Access Control implementation.

### 1. SELinux Security Context Syntax
In SELinux, every process (subject) and every file, directory, socket, or device node (object) is stamped with an immutable cryptographic label called a **Security Context**:
$$\\text{Security Context} = \\text{user} : \\text{role} : \\text{type} : \\text{level}$$

```
Example SELinux Contexts:
  Apache Web Server Process:   system_u:system_r:httpd_t:s0
  Web Content HTML File:       system_u:object_r:httpd_sys_content_t:s0
  User Shadow Password File:   system_u:object_r:shadow_t:s0
```

- **`user`**: The SELinux user identity (e.g., `system_u`, `unconfined_u`).
- **`role`**: The operational role (in Role-Based Access Control, e.g., `system_r`, `object_r`).
- **`type` (Domain / Type Enforcement)**: The primary mechanism of isolation. For processes, it is termed the **Domain** (e.g., `httpd_t`, `sshd_t`); for files, it is the **Type** (e.g., `httpd_sys_content_t`, `shadow_t`).
- **`level`**: Multi-Level Security / Multi-Category Security (MLS/MCS) sensitivity rating (e.g., `s0`, `s0:c0,c100`).

```mermaid
graph TD
    subgraph SELinux_AVC_Decision["SELinux Type Enforcement & Access Vector Cache (AVC) Engine"]
        direction TB
        
        Req["Process (Domain: httpd_t) attempts to open File (Type: shadow_t)"]
        AVC{"Is Decision Cached in<br/>Access Vector Cache (AVC)?"}
        PolicyDB{"Evaluate Policy Rules in Kernel DB:<br/>allow httpd_t shadow_t : file { read };"}
        
        Req --> AVC
        AVC -->|Cache Hit: Denied| LogDeny["Log AVC Denial to /var/log/audit/audit.log"]
        AVC -->|Cache Miss| PolicyDB
        
        PolicyDB -->|No Rule Exists: Implicit Deny| LogDeny
        PolicyDB -->|Rule Exists: Allow| AllowAccess["Update AVC & Grant Read Handle"]
        
        LogDeny --> EnforcingCheck{"Current Mode == Enforcing?"}
        EnforcingCheck -->|YES (Enforcing)| Block["Return -EACCES (Operation Aborted)"]
        EnforcingCheck -->|NO (Permissive)| AllowPermissive["Allow Operation (Audit Log Only)"]
    end
    
    style SELinux_AVC_Decision fill:#fdfefe,stroke:#2c3e50,stroke-width:2px;
    style AVC fill:#ebf5fb,stroke:#2980b9,stroke-width:2px;
    style Block fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
    style AllowAccess fill:#d4efdf,stroke:#27ae60,stroke-width:2px;
```

### 2. SELinux Operating Modes
- **Enforcing**: The default production mode. The security policy is actively enforced; unauthorized actions are blocked and logged.
- **Permissive**: The system operates without blocking unauthorized actions. Violations are allowed to proceed, but detailed audit denial messages are logged. (Essential for debugging and authoring new policies).
- **Disabled**: SELinux is completely unloaded from the kernel; zero labeling or protection is active.

### 3. Essential Administrative Commands

```bash
# Querying and switching active SELinux mode:
getenforce                  # Displays current status (Enforcing / Permissive)
setenforce 0                # Temporarily sets Permissive mode (runtime only)
setenforce 1                # Sets Enforcing mode

# Inspecting security labels:
ls -lZ /var/www/html/index.html   # Displays file security context
ps -eZ | grep nginx               # Displays process domain

# Relabeling and restoring context:
restorecon -vR /var/www/html      # Resets files to default policy labels
chcon -t httpd_sys_content_t file.txt # Temporarily modifies type label

# Managing SELinux Booleans (Policy toggles):
getsebool httpd_can_network_connect  # Checks if Apache can make outbound connections
setsebool -P httpd_can_network_connect on # Permanently enables boolean in policy

# Diagnosing and fixing AVC Denials:
ausearch -m avc -ts recent | audit2why   # Translates raw audit logs into human explanations
ausearch -m avc -ts recent | audit2allow -M my_custom_policy # Auto-generates policy module
```

---

## 11.4 AppArmor: Path-Based Mandatory Access Control

While SELinux relies on explicit inode labels stored in filesystem extended attributes (`xattr`), **AppArmor** (standard on Ubuntu, Debian, and openSUSE) implements a **path-based** Mandatory Access Control architecture.

### AppArmor Architecture & Profile Modes
- **Profiles**: Plaintext configuration files residing in `/etc/apparmor.d/` defining the file access paths, network sockets, and capabilities allowed for a specific binary executable (e.g., `/usr/sbin/tcpdump`).
- **Modes**:
  - **Enforce**: Violations are blocked and logged to `/var/log/syslog` or `audit.log`.
  - **Complain**: Violations are permitted, but logged as warnings.

```
Example AppArmor Profile Snippet (/etc/apparmor.d/usr.bin.ping):
  /usr/bin/ping {
    # Include base abstractions
    #include <abstractions/base>
    #include <abstractions/nameservice>

    # Granular capability grants
    capability net_raw,
    capability setuid,

    # File access rules
    /usr/bin/ping mr,
    /etc/modules.conf r,
    /dev/null rw,
  }
```

### Administrative Tools:
```bash
aa-status                   # Shows current status of loaded profiles
aa-enforce /etc/apparmor.d/* # Puts all profiles into Enforce mode
aa-complain /usr/sbin/nginx  # Puts Nginx into Complain mode
aa-logprof                  # Interactive CLI tool to update profiles from audit logs
```

---
"""

module12_content = """# Module 12: Linux User Authentication, Credentials & PAM

## 12.1 Linux Credential Storage: `/etc/passwd` vs. `/etc/shadow`

User account management and credential verification in Linux are decoupled between public user identification and private cryptographic credential storage.

```
/etc/passwd Entry Format (World-Readable: 0644):
  username:password_placeholder:UID:GID:GECOS:home_directory:login_shell
  root:x:0:0:root:/root:/bin/bash
  www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
```

Because `/etc/passwd` must be globally world-readable for system utilities to map numeric UIDs to usernames (e.g., `ls -l`), storing password hashes in `/etc/passwd` permitted unprivileged users to read hashes and conduct offline dictionary cracking.

To resolve this vulnerability, modern Linux systems deploy the **Shadow Password Suite** (`/etc/shadow`), which is restricted to read-only access by `root` (permissions `0640` or `0000`, owned by `root:shadow`).

```mermaid
graph TD
    subgraph Shadow_Entry_Anatomy["Anatomy of an /etc/shadow Record"]
        direction TB
        
        Raw["alice : $6$rounds=5000$saltsalt$hashedpassword... : 19720 : 0 : 90 : 7 : : :"]
        
        Field1["1. Username (alice)"]
        Field2["2. Hashed Password ($ID$Salt$Hash)"]
        Field3["3. Last Password Change (Days since Jan 1, 1970)"]
        Field4["4. Minimum Password Age (Days before user can change)"]
        Field5["5. Maximum Password Age (Days before password expires)"]
        Field6["6. Warning Period (Days warning user before expiry)"]
        Field7["7. Inactivity Period (Days after expiry before account disabled)"]
        Field8["8. Account Expiration Date (Days since epoch when account dies)"]
        
        Raw --- Field1 --- Field2 --- Field3 --- Field4 --- Field5 --- Field6 --- Field7 --- Field8
    end
    
    style Shadow_Entry_Anatomy fill:#f9f9f9,stroke:#34495e,stroke-width:2px;
    style Field2 fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
```

### Cryptographic Hash Identifier Prefixes (`$ID$`)
The second field of `/etc/shadow` encodes the hashing algorithm, the random cryptographic salt (preventing Rainbow table attacks), and the resulting one-way hash:

| Prefix ID | Hashing Algorithm | Security Assessment | Key Derivation Iterations |
| :---: | :--- | :--- | :--- |
| **`$1$`** | **MD5-crypt** | **BROKEN / INSECURE**. Vulnerable to collision attacks and ultra-fast GPU cracking. | 1,000 iterations (Fixed) |
| **`$2a$` / `$2b$`** | **Bcrypt** | **SECURE**. Memory-hard Blowfish-based key derivation. | Configurable cost factor |
| **`$5$`** | **SHA-256-crypt** | **SECURE**. Standard NIST algorithm. | 5,000 iterations (Configurable) |
| **`$6$`** | **SHA-512-crypt** | **HIGHLY SECURE**. Linux default standard for over a decade. | 5,000 iterations (Configurable) |
| **`$y$`** | **Yescrypt** | **MODERN STATE-OF-THE-ART**. Native memory-hard function resistant to FPGA/ASIC password cracking rigs. | Modern default in Debian 11+ and RHEL 9+ |

---

## 12.2 Pluggable Authentication Modules (PAM) Architecture

Historically, every program requiring user authentication (e.g., `login`, `su`, `sshd`, `ftp`) hardcoded its own authentication routines. Altering authentication schemes (such as integrating LDAP, smart cards, or biometric tokens) required re-compiling every application from source code.

**Pluggable Authentication Modules (PAM)** decouples user-facing applications from underlying authentication technologies via a modular, dynamic framework configured in `/etc/pam.d/`.

```mermaid
graph TD
    subgraph PAM_Architecture_Stack["Pluggable Authentication Modules (PAM) Processing Pipeline"]
        direction TB
        
        App["Application Requiring Authentication (e.g., /usr/sbin/sshd, /bin/su)"]
        API["PAM API: pam_authenticate(), pam_acct_mgmt()"]
        Config["Service Configuration: /etc/pam.d/sshd"]
        
        subgraph PAM_Stacks["The Four Independent PAM Management Groups"]
            Auth["1. auth Stack<br/>Verifies User Identity (Prompts for Password, MFA Token)"]
            Acct["2. account Stack<br/>Verifies Account Status (Expiry, Day/Time Restrictions, Locked)"]
            Pass["3. password Stack<br/>Handles Credential Updates (Complexity, Minimum Age, History)"]
            Sess["4. session Stack<br/>Configures Environment (Mounts Home Dir, Sets Ulimits, Auditing)"]
        end
        
        App --> API --> Config
        Config --> Auth
        Config --> Acct
        Config --> Pass
        Config --> Sess
    end
    
    style PAM_Architecture_Stack fill:#fdfefe,stroke:#2c3e50,stroke-width:2px;
    style Auth fill:#ebf5fb,stroke:#2980b9,stroke-width:2px;
    style Acct fill:#fef9e7,stroke:#f39c12,stroke-width:2px;
    style Pass fill:#f4ecf7,stroke:#8e44ad,stroke-width:2px;
    style Sess fill:#d4efdf,stroke:#27ae60,stroke-width:2px;
```

### The Four PAM Management Groups
1. **`auth`**: Authenticates the user and establishes credentials (e.g., querying password, validating hardware security key).
2. **`account`**: Determines whether the authenticated user is allowed to access the system right now (checks whether the account is disabled, expired, or prohibited by time-of-day policies).
3. **`password`**: Enforces password changing policies and password strength rules.
4. **`session`**: Tasks executed before and after user access is granted (e.g., mounting encrypted directories, setting resource limits in `/etc/security/limits.conf`, logging login records in `wtmp`).

### The Four Control Flags

| Control Flag | Behavior on Module Success | Behavior on Module Failure |
| :--- | :--- | :--- |
| **`required`** | Success recorded. Pipeline continues executing subsequent modules. | Failure recorded. Pipeline **must continue** executing subsequent modules (to prevent attackers from timing which specific check failed), but overall authentication will ultimately fail. |
| **`requisite`** | Success recorded. Pipeline continues executing subsequent modules. | Immediate failure! Pipeline **aborts immediately**, rejecting user without executing remaining modules. |
| **`sufficient`** | If no earlier `required` modules failed, pipeline **terminates immediately with SUCCESS**! | Failure recorded, but ignored; pipeline continues executing. |
| **`optional`** | Success recorded. Only determines outcome if it is the only module in the stack. | Ignored unless it is the only module in the stack. |

---

## 12.3 Hardening Authentication: Account Lockout & Password Complexity

Modern enterprise Linux configurations mandate strict brute-force mitigations and entropy enforcement via specialized PAM modules.

### 1. Brute-Force Defense via `pam_faillock`
Protects against offline and online credential stuffing by locking user accounts after a defined threshold of consecutive failed authentication attempts:
```
# /etc/pam.d/password-auth or system-auth configuration:
auth     required  pam_faillock.so preauth silent audit deny=5 unlock_time=900
auth     sufficient pam_unix.so try_first_pass
auth     [default=die] pam_faillock.so authfail audit deny=5 unlock_time=900
account  required  pam_faillock.so
```
- `deny=5`: Locks the account after 5 consecutive failures.
- `unlock_time=900`: Account remains locked for 15 minutes (900 seconds).

### 2. Password Quality Enforcement via `pam_pwquality`
Rejects weak or dictionary passwords during password changes:
```ini
# /etc/security/pwquality.conf
minlen = 14          # Minimum password length: 14 characters
dcredit = -1         # At least 1 digit required
ucredit = -1         # At least 1 uppercase letter required
lcredit = -1         # At least 1 lowercase letter required
ocredit = -1         # At least 1 special character required
difok = 5            # At least 5 characters must differ from old password
maxrepeat = 2        # No character repeated more than twice consecutively
```

---
"""

module13_content = """# Module 13: Linux Process Isolation: Namespaces, Cgroups, Seccomp & Capabilities

## 13.1 Container Isolation Building Blocks: Namespaces & Cgroups

In modern cloud-native architectures (Docker, Kubernetes, Podman), **containers are not virtual machines**. Containers are simply standard Linux user-space processes isolated at the kernel level using two foundational technologies:
1. **Linux Kernel Namespaces**: Governs **what a process can SEE** (Virtualization of system resources).
2. **Control Groups (cgroups)**: Governs **how much a process can USE** (Resource metering and throttling).

```mermaid
graph TD
    subgraph Container_Isolation_Architecture["Linux Container Isolation Architecture"]
        direction TB
        
        subgraph Namespaces["Linux Kernel Namespaces (Resource Views)"]
            PID_NS["PID Namespace (Process Isolation: PID 1 inside container)"]
            NET_NS["Network Namespace (Virtual Interfaces, Routing Tables, Sockets)"]
            MNT_NS["Mount Namespace (Isolated Filesystem Root / Pivot Root)"]
            IPC_NS["IPC Namespace (Isolated Shared Memory & Message Queues)"]
            UTS_NS["UTS Namespace (Isolated Hostname & Domain Name)"]
            USER_NS["User Namespace (Maps Container Root UID 0 to Host UID 100000!)"]
        end
        
        subgraph Cgroups["Control Groups - cgroups v2 (Resource Throttling)"]
            CPU_Limit["CPU: Max 2 Cores / Quota Throttling"]
            MEM_Limit["Memory: Max 2GB / OOM Killer Enforcement"]
            IO_Limit["I/O: Max 50 MB/s BlkIO Throughput"]
            PID_Limit["pids.max: Max 100 PIDs (Mitigates Fork Bombs!)"]
        end
        
        subgraph Sandboxed_Process["Confined Container Workload"]
            App["Microservice Application Process"]
        end
        
        Namespaces --- App
        Cgroups --- App
    end
    
    style Container_Isolation_Architecture fill:#fdfefe,stroke:#2c3e50,stroke-width:2px;
    style Namespaces fill:#ebf5fb,stroke:#2980b9,stroke-width:2px;
    style Cgroups fill:#fef9e7,stroke:#f39c12,stroke-width:2px;
    style App fill:#d4efdf,stroke:#27ae60,stroke-width:2px;
```

---

## 13.2 The Seven Core Linux Namespaces

| Namespace Flag | Virtualized Resource | Security Impact & Isolation Boundary |
| :---: | :--- | :--- |
| **`CLONE_NEWPID`** | Process IDs | Processes inside the container only see themselves. The containerized entry point executes as PID 1, unable to inspect or send signals (`kill`) to host processes. |
| **`CLONE_NEWNET`** | Network Stacks | Provides a private loopback interface, virtual Ethernet pair (`veth`), independent routing tables, and private port namespaces. |
| **`CLONE_NEWNS`** | Mount Points | Provides a private filesystem hierarchy. Changes to mount tables inside do not reflect on the host. |
| **`CLONE_NEWIPC`** | Inter-Process Comm | Isolates System V IPC and POSIX message queues, preventing cross-container shared memory tapping. |
| **`CLONE_NEWUTS`** | Hostname / Domain | Allows container to define its own hostname without modifying host system identity. |
| **`CLONE_NEWUSER`** | User & Group IDs | **Crucial for rootless containers**. Maps container UID 0 (root inside) to an unprivileged UID (e.g., UID 100000) on the host. Even if container escapes, it holds zero host root privileges! |
| **`CLONE_NEWCGROUP`**| Cgroup Hierarchy | Masks the root cgroup directory structure, preventing container introspection of host system resource allocations. |

---

## 13.3 Linux Capabilities: Decomposing the Omnipotent Root

Traditionally, Linux enforced a binary permission model: a process was either an unprivileged standard user (`UID != 0`) or the omnipotent superuser (`UID == 0`). If an application needed to bind to privileged port 80 (e.g., web server) or set system time, it had to run with full root privileges.

**Linux Capabilities** (introduced in kernel 2.2) decompose the monolithic powers of `root` into distinct, granular privileges:

```
Common Critical Linux Capabilities:
  CAP_NET_BIND_SERVICE:  Bind a socket to Internet domain privileged ports (< 1024).
  CAP_NET_RAW:           Permits using RAW and PACKET sockets (ping, tcpdump).
  CAP_SYS_ADMIN:         Overpowered "catch-all" capability (mount filesystems, load BPF).
  CAP_SYS_PTRACE:        Trace arbitrary processes using ptrace (can read memory of other apps).
  CAP_DAC_OVERRIDE:      Bypass all file read, write, and execute permission checks.
  CAP_CHOWN:             Make arbitrary changes to file UIDs and GIDs.
```

### Restricting Capabilities on Binaries
Rather than setting the dangerous `SUID root` bit on a binary, administrators grant only the specific capability required:
```bash
# Removing SUID from ping and granting only CAP_NET_RAW:
chmod u-s /usr/bin/ping
setcap cap_net_raw+ep /usr/bin/ping

# Inspecting capabilities:
getcap /usr/bin/ping
# Output: /usr/bin/ping = cap_net_raw+ep
```

---

## 13.4 Seccomp & Seccomp-BPF (Secure Computing Mode)

The Linux kernel exposes over 400 distinct **system calls** (syscalls). The vast majority of user applications require only a tiny fraction (e.g., 30 to 40 syscalls like `read`, `write`, `epoll_wait`). Unused system calls (such as `ptrace`, `bpf`, `mount`, `kexec_load`) represent latent attack surface for kernel exploitation.

**Seccomp-BPF** allows a user process to define a stateful Berkeley Packet Filter (BPF) program that inspects system call numbers and arguments *before* the kernel dispatches them.

```mermaid
graph TD
    subgraph Seccomp_BPF_Pipeline["Seccomp-BPF System Call Filtering Pipeline"]
        direction TB
        
        AppSyscall["Process issues System Call: sys_ptrace()"]
        BPF_Filter["Seccomp-BPF Filter Engine in Linux Kernel"]
        
        AppSyscall --> BPF_Filter
        
        Decision{"Matches Allowed Syscall Whitelist?"}
        BPF_Filter --> Decision
        
        Decision -->|ALLOWED (e.g., read, write)| ExecSyscall["Kernel Executes System Call"]
        Decision -->|DENIED / PROHIBITED| Action{"Configured Seccomp Action"}
        
        Action -->|SECCOMP_RET_KILL_PROCESS| Kill["Kernel Instantly Terminates Process (SIGSYS)"]
        Action -->|SECCOMP_RET_ERRNO| ReturnErr["Returns -EPERM to Process without executing"]
    end
    
    style Seccomp_BPF_Pipeline fill:#fdfefe,stroke:#2c3e50,stroke-width:2px;
    style BPF_Filter fill:#ebf5fb,stroke:#2980b9,stroke-width:2px;
    style ExecSyscall fill:#d4efdf,stroke:#27ae60,stroke-width:2px;
    style Kill fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
```

---
"""

module14_content = """# Module 14: Linux Network Defense, Auditing & Exploit Hardening

## 14.1 The Netfilter Packet Filtering Architecture: iptables vs. nftables

At the heart of Linux network defense resides **Netfilter**, a framework inside the Linux kernel providing callback hooks across the network stack for packet filtering, Network Address Translation (NAT), and connection tracking.

```mermaid
graph TD
    subgraph Netfilter_Packet_Flow["Netfilter Architecture & Packet Traversing Hooks"]
        direction TB
        
        NIC_In["Network Interface (Packet Ingress)"] --> Pre["1. PREROUTING Hook<br/>(DNAT, Raw, Mangle)"]
        
        Routing1{"Routing Decision:<br/>Is Packet for Local Host?"}
        Pre --> Routing1
        
        Routing1 -->|YES: Local Destination| Input["2. INPUT Hook<br/>(Filter: Inbound Firewall Rules)"]
        Routing1 -->|NO: Forward to Other Host| Forward["3. FORWARD Hook<br/>(Filter: Routed / Gateway Traffic)"]
        
        Input --> LocalProc["Local Socket / Application Process"]
        LocalProc --> Output["4. OUTPUT Hook<br/>(Filter: Outbound Host Traffic)"]
        
        Output --> Routing2["Routing Decision"]
        Routing2 --> Post["5. POSTROUTING Hook<br/>(SNAT / Masquerade)"]
        Forward --> Post
        
        Post --> NIC_Out["Network Interface (Packet Egress)"]
    end
    
    style Netfilter_Packet_Flow fill:#f9f9f9,stroke:#34495e,stroke-width:2px;
    style Pre fill:#ebf5fb,stroke:#2980b9,stroke-width:2px;
    style Input fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
    style Output fill:#fef9e7,stroke:#f39c12,stroke-width:2px;
    style Post fill:#d4efdf,stroke:#27ae60,stroke-width:2px;
```

### 1. iptables Architecture
- **Tables**:
  - `filter`: Default table for packet filtering (Chains: `INPUT`, `OUTPUT`, `FORWARD`).
  - `nat`: Network address translation (Chains: `PREROUTING`, `POSTROUTING`, `OUTPUT`).
  - `mangle`: Packet header alteration (TTL, TOS).
  - `raw`: Bypasses connection tracking (`conntrack`).
- **Connection Tracking (`conntrack`)**:
  - Enables stateful inspection. Packets are tagged as:
    - `NEW`: Initiating a connection.
    - `ESTABLISHED`: Part of an existing verified connection.
    - `RELATED`: Auxiliary connection (e.g., FTP data channel).
    - `INVALID`: Packets with illegal flag combinations.

### 2. nftables: The Modern Linux Standard
Replaces legacy `iptables`, `ip6tables`, `arptables`, and `ebtables` with a single unified packet filtering engine executing an in-kernel bytecode virtual machine:
- Eliminates duplicated rules across IPv4 and IPv6 via the unified `inet` address family.
- Atomic rule replacement: Multiple rules commit simultaneously without connection interruption.

```bash
# Example Modern nftables Production Firewall Configuration:
table inet firewall {
    chain inbound {
        type filter hook input priority filter; policy drop;

        # Allow established and related traffic
        ct state { established, related } accept

        # Drop invalid packets immediately
        ct state invalid drop

        # Allow local loopback traffic
        iif "lo" accept

        # Allow incoming ICMP (ping) rate-limited
        ip protocol icmp limit rate 5/second accept

        # Allow SSH (Port 22)
        tcp dport 22 accept
    }
}
```

---

## 14.2 Secure Shell (SSH) Host Hardening

SSH is the primary remote administrative interface for Linux infrastructure, making it an unceasing target for brute-force dictionary attacks and credential spraying.

```ini
# Production Hardened /etc/ssh/sshd_config Configuration:
Port 22
Protocol 2

# Authentication Hardening
PermitRootLogin no                   # Prohibit direct root login (force su/sudo)
MaxAuthTries 3                       # Disconnect client after 3 failed attempts
PubkeyAuthentication yes             # Enforce Public Key Authentication
PasswordAuthentication no            # DISABLE all password authentication!
PermitEmptyPasswords no              # Reject empty passwords
AuthenticationMethods publickey      # Require asymmetric key

# Cryptographic Suite Hardening (Prohibit broken legacy ciphers)
KexAlgorithms curve25519-sha256,diffie-hellman-group16-sha512
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com
MACs hmac-sha2-512-etm@openssh.com

# Channel & Forwarding Restrictions
X11Forwarding no                     # Disable X11 GUI forwarding
AllowTcpForwarding no                # Prevent SSH from acting as a network proxy
ClientAliveInterval 300              # Terminate idle sessions after 15 minutes
ClientAliveCountMax 2
```

---

## 14.3 The Linux Auditing Framework (`auditd`)

While log files in `/var/log/` record application-level messages, attackers with local privileges can modify or truncate logs. The **Linux Audit Framework (`auditd`)** is deeply integrated into kernel system call entrypoints, recording tamper-resistant audit records directly to disk.

```mermaid
graph LR
    subgraph Audit_Architecture["Linux Audit Subsystem Pipeline"]
        direction LR
        Kernel["Kernel Syscall / Event Engine<br/>(kauditd)"] --> Netlink["Netlink Socket<br/>(NETLINK_AUDIT)"]
        Netlink --> Daemon["auditd Daemon<br/>(User-Space Collector)"]
        Daemon --> LogFile["/var/log/audit/audit.log<br/>(Immutable Log Storage)"]
        LogFile --> Tools["Analysis Tools:<br/>• ausearch (Event query)<br/>• aureport (Summary stats)"]
    end
    
    style Audit_Architecture fill:#fdfefe,stroke:#2c3e50,stroke-width:2px;
    style Kernel fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
    style Daemon fill:#ebf5fb,stroke:#2980b9,stroke-width:2px;
    style Tools fill:#d4efdf,stroke:#27ae60,stroke-width:2px;
```

### Essential Audit Rules (`/etc/audit/rules.d/audit.rules`)
```bash
# Monitor changes to critical user/group identity files:
-w /etc/passwd -p wa -k identity_changes
-w /etc/shadow -p wa -k identity_changes
-w /etc/sudoers -p wa -k privilege_changes

# Monitor execution of the execve system call by non-root users (UID >= 1000):
-a always,exit -F arch=b64 -S execve -F auid>=1000 -F auid!=4294967295 -k user_commands

# Make audit rules immutable until next system reboot:
-e 2
```

---

## 14.4 Linux Kernel Exploit Mitigations & Sysctl Hardening

Modern Linux kernels incorporate defense-in-depth compile-time and runtime exploit mitigations that eliminate whole classes of memory corruption vulnerabilities:

```
Linux Kernel Memory Exploit Mitigations:
+---------------------------------------------------------------------------------+
| Mitigation Mechanism | Architectural Purpose & Implementation                   |
+----------------------+----------------------------------------------------------+
| KASLR                | Kernel Address Space Layout Randomization                |
|                      | Randomizes base physical/virtual location of kernel text |
| Stack Canaries (SSP) | Inserts random guard value before Saved EBP/RIP.         |
|                      | Compiler emits __stack_chk_fail on mismatch.            |
| DEP / NX             | Data Execution Prevention / No-Execute bit in page tables|
|                      | Marks Stack and Heap as Non-Executable (PAGE_NOEXEC)    |
| KPTI                 | Kernel Page Table Isolation                              |
|                      | Unmaps kernel address space while running in user mode   |
|                      | (Mitigates Meltdown speculative execution side-channels) |
| Yama ptrace_scope    | Restricts ptrace system call to parent processes only    |
+---------------------------------------------------------------------------------+
```

### Essential Production Sysctl Hardening (`/etc/sysctl.d/99-security.conf`)
```ini
# Restrict dmesg kernel log buffer access to root only (prevents KASLR address leaks)
kernel.dmesg_restrict = 1

# Restrict ptrace memory inspection to parent processes only
kernel.yama.ptrace_scope = 2

# Hide exposed kernel pointers in /proc/kallsyms
kernel.kptr_restrict = 2

# Enable TCP SYN Cookies (DoS Defense)
net.ipv4.tcp_syncookies = 1

# Disable ICMP Echo redirects (Mitigates MITM routing attacks)
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0

# Enable Reverse Path Filtering (Mitigates IP address spoofing)
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1
```

---
"""

with open("cyber-security/modules/module11.md", "w") as f:
    f.write(module11_content.strip() + "\n")

with open("cyber-security/modules/module12.md", "w") as f:
    f.write(module12_content.strip() + "\n")

with open("cyber-security/modules/module13.md", "w") as f:
    f.write(module13_content.strip() + "\n")

with open("cyber-security/modules/module14.md", "w") as f:
    f.write(module14_content.strip() + "\n")

print("Generated Modules 11 to 14 successfully.")
