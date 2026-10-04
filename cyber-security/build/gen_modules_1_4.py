#!/usr/bin/env python3
"""
Generator for Modules 1 to 4 of the Cyber Security Essentials & Linux Security Guide.
"""

import os

os.makedirs("cyber-security/modules", exist_ok=True)

module1_content = """# Module 1: Information Assurance Fundamentals, Cryptography & Network Infrastructure

## 1.1 The Information Assurance Foundation: Beyond the CIA Triad

Information security in modern enterprise, defense, and cloud systems is anchored in the principles of **Information Assurance (IA)**. While traditional computer security historically prioritized data confidentiality, comprehensive operational assurance requires a holistic multidimensional model encompassing six core pillars:

```mermaid
graph TD
    subgraph IA_Pillars["The Six Pillars of Information Assurance"]
        direction TB
        C["Confidentiality<br/>(Secrecy of Data at Rest, in Transit, and in Use)"]
        I["Integrity<br/>(Guarding Against Unauthorized Modification / Tampering)"]
        A["Availability<br/>(Timely, Reliable Access to Systems and Services)"]
        AuthN["Authentication<br/>(Verification of Identity Claims)"]
        AuthZ["Authorization<br/>(Granting Specific Permissions and Access Rights)"]
        NR["Non-Repudiation<br/>(Undeniable Proof of Origin and Delivery)"]
    end
    
    C --- I --- A
    AuthN --- AuthZ --- NR
    
    style IA_Pillars fill:#f8f9f9,stroke:#34495e,stroke-width:2px;
    style C fill:#eaf2f8,stroke:#2980b9,stroke-width:2px;
    style I fill:#e8f8f5,stroke:#27ae60,stroke-width:2px;
    style A fill:#fef9e7,stroke:#f39c12,stroke-width:2px;
    style AuthN fill:#f4ecf7,stroke:#8e44ad,stroke-width:2px;
    style AuthZ fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
    style NR fill:#d5f5e3,stroke:#1abc9c,stroke-width:2px;
```

### Detailed Pillar Breakdown
1. **Confidentiality**: Assures that sensitive information is shielded from interception, snooping, or unauthorized disclosure. Enforced via symmetric/asymmetric encryption, access control mechanisms, and physical isolation.
2. **Integrity**: Assures that data and software remain uncorrupted by unauthorized modification, deletion, injection, or hardware failure. Enforced via cryptographic hash digests (SHA-256, SHA-3), Message Authentication Codes (HMAC), and digital signatures.
3. **Availability**: Assures that computing resources, network fabrics, and data storage are readily accessible to authorized users whenever required. Threat models include Distributed Denial of Service (DDoS), ransomware locking, hardware faults, and power grid failures. Enforced through redundant clustering, load balancing, fault tolerance, and Disaster Recovery (DR) architectures.
4. **Authentication**: The mathematical or procedural verification of an asserted identity (user, host, service, or API). Mechanisms include single-factor (passwords), multi-factor authentication (MFA: possession, knowledge, inherence), cryptographic certificates (X.509), and hardware tokens (FIDO2/WebAuthn).
5. **Authorization**: The enforcement mechanism determining whether an authenticated subject possesses the legal entitlement to execute a requested action upon an object. Enforced via Discretionary Access Control (DAC), Mandatory Access Control (MAC), Role-Based Access Control (RBAC), and Attribute-Based Access Control (ABAC).
6. **Non-Repudiation**: The cryptographic guarantee that an entity cannot refute having initiated an action, transmitted a message, or approved a transaction. Enforced via asymmetric digital signatures and immutable audit trails anchored in trusted timestamping authorities.

---

## 1.2 Cryptographic Foundations: Symmetric, Asymmetric & Hashing

Cryptography constitutes the primary mathematical toolkit for enforcing confidentiality, integrity, and authentication.

```mermaid
graph LR
    subgraph Crypto_Taxonomy["Taxonomy of Modern Cryptographic Primitives"]
        direction TB
        
        subgraph Symmetric["Symmetric Cryptography (Shared Secret Key K)"]
            Stream["Stream Ciphers<br/>• RC4, ChaCha20<br/>• Encrypts bit-by-bit via XOR with Keystream"]
            Block["Block Ciphers<br/>• AES, DES, 3DES<br/>• Encrypts fixed-size blocks (128 bits)"]
        end
        
        subgraph Asymmetric["Asymmetric Cryptography (Public / Private Key Pair)"]
            PK_Enc["Encryption / Key Exchange<br/>• RSA, Diffie-Hellman (DH), ECDH"]
            PK_Sig["Digital Signatures<br/>• RSA-PSS, ECDSA, Ed25519"]
        end
        
        subgraph Hashing["Cryptographic Hash Functions (One-Way Compression)"]
            Digest["Cryptographic Digests<br/>• SHA-256, SHA-3, BLAKE2<br/>• Collision & Pre-image Resistant"]
            MAC["Keyed MACs<br/>• HMAC-SHA256, Poly1305"]
        end
    end
    
    style Crypto_Taxonomy fill:#fdfefe,stroke:#2c3e50,stroke-width:2px;
    style Symmetric fill:#ebf5fb,stroke:#2980b9,stroke-width:2px;
    style Asymmetric fill:#fef9e7,stroke:#f39c12,stroke-width:2px;
    style Hashing fill:#e8f8f5,stroke:#27ae60,stroke-width:2px;
```

### 1. Symmetric Cryptography
Symmetric ciphers rely on a single shared secret key ($K$) known to both the communicating parties. The key space must be sufficiently large to preclude brute-force exploration (minimum 128 bits; modern enterprise standard is AES-256).

- **Stream Ciphers**:
  - Encrypt plaintext byte-by-byte or bit-by-bit by performing an exclusive OR (XOR, $\\oplus$) operation between plaintext bits ($P_i$) and a pseudorandom keystream ($K_i$) generated by a cryptographic seed:
    $$C_i = P_i \\oplus K_i, \\quad P_i = C_i \\oplus K_i$$
  - *Vulnerability of Keystream Reuse (Two-Time Pad)*: If the same keystream $K$ is ever used to encrypt two different plaintexts $P_1$ and $P_2$:
    $$C_1 \\oplus C_2 = (P_1 \\oplus K) \\oplus (P_2 \\oplus K) = P_1 \\oplus P_2$$
    An attacker cancels out the key entirely, enabling trivial linguistic plaintext recovery.
- **Block Ciphers & Modes of Operation**:
  - Transform fixed-size blocks of plaintext (e.g., 128 bits for AES) into identical-sized ciphertext blocks.
  - *Electronic Codebook (ECB)*: Encrypts each 128-bit block independently with the same key. **Insecure**: Identical plaintext blocks produce identical ciphertext blocks, preserving structural data patterns (the famous "ECB Penguin" leak).
  - *Cipher Block Chaining (CBC)*: Each plaintext block is XORed with the preceding ciphertext block before encryption, initialized with an unpredictable Initialization Vector (IV).
  - *Galois/Counter Mode (GCM)*: An Authenticated Encryption with Associated Data (AEAD) mode providing line-speed confidentiality and integrity verification via universal hashing.

### 2. Asymmetric Cryptography (Public-Key Cryptography)
Asymmetric systems utilize mathematically related key pairs: a **Public Key** ($K_{\\text{pub}}$) openly distributed to the world, and a **Private Key** ($K_{\\text{priv}}$) strictly guarded by the owner.
- **Diffie-Hellman Key Exchange (DH / ECDH)**: Enables two mutually untrusted parties to establish a shared symmetric secret across an insecure, sniffed communications channel without transmitting the key itself.
- **RSA**: Rooted in the integer factorization problem of large composite numbers $n = p \\cdot q$.
- **Elliptic Curve Cryptography (ECC)**: Rooted in the discrete logarithm problem over elliptic curves (e.g., Curve25519, NIST P-384). Achieves equivalent cryptographic security to RSA with drastically smaller key sizes (e.g., 256-bit ECC $\\approx$ 3072-bit RSA), saving CPU cycles and network bandwidth.

---

## 1.3 The Domain Name System (DNS) Architecture & Security Exploits

The **Domain Name System (DNS)** serves as the fundamental directory service of the Internet, translating human-readable Fully Qualified Domain Names (FQDNs like `api.corporate.internal`) into machine-routable IPv4/IPv6 addresses.

```mermaid
sequenceDiagram
    autonumber
    participant Client as Client Stub Resolver
    participant Recurse as Recursive DNS Resolver (ISP/Cloud)
    participant Auth as Authoritative DNS Server
    participant Attacker as Rogue Nameserver / Attacker

    Client->>Recurse: Query A Record: target.com
    Recurse->>Auth: Iterative Query (Port 53, Transaction ID: 0x4A1F)
    Attacker-->>Recurse: Floods Spoofed DNS Responses (Guessed TXID + Malicious IP)
    Note over Recurse: Cache Poisoned if Attacker's Response Arrives First!
    Auth-->>Recurse: Genuine Response (Arrives Late - Discarded)
    Recurse-->>Client: Returns Attacker's Malicious IP (Redirected to Phishing)
```

### Major DNS Attack Vectors
1. **DNS Cache Poisoning (Kaminsky Attack)**:
   - Attackers flood recursive resolvers with forged DNS responses containing spoofed Authoritative Name Server records.
   - If the attacker successfully guesses the 16-bit **DNS Transaction ID (TXID)** and UDP source port before the legitimate authoritative server responds, the recursive cache stores the malicious IP mapping for the duration of the Time-To-Live (TTL).
2. **DNS Amplification & Reflection DDoS**:
   - Attackers emit spoofed UDP queries targeting open recursive resolvers with the `ANY` record request, forging the victim's source IP address.
   - The resolvers respond to the victim with enormous multi-kilobyte responses, achieving amplification factors of $50\\times$ to $100\\times$.
3. **DNS Tunneling**:
   - Encapsulates non-DNS protocols (SSH, HTTP, command-and-control beacons, exfiltrated files) within standard DNS query labels (`base64data.c2.attacker.com`). Bypasses perimeter firewalls because port 53 UDP traffic is almost universally permitted egress.
4. **Defensive Standard: DNSSEC**:
   - Cryptographically signs DNS resource records using asymmetric signatures (`RRSIG`, `DNSKEY`, `DS` records).
   - Establishes a hierarchical chain of trust from the ICANN DNS Root zone down to domain records, eliminating spoofing and cache poisoning.

---

## 1.4 Perimeter Defense: Firewall Architectures & Evolution

Firewalls enforce boundary security policies by inspecting, filtering, and governing traffic traversing network segments.

```mermaid
graph TD
    subgraph Firewall_Generations["Firewall Architectural Evolution"]
        direction TB
        
        subgraph Gen1["Generation 1: Stateless Packet-Filtering"]
            PF["Inspects Headers in Isolation<br/>• Source IP, Dest IP<br/>• Source Port, Dest Port, Protocol (TCP/UDP/ICMP)<br/>• Zero awareness of connection state"]
        end
        
        subgraph Gen2["Generation 2: Stateful Inspection Firewalls"]
            SI["Maintains State Table (Connection Tracking)<br/>• Tracks TCP 3-Way Handshake (SYN, SYN-ACK, ACK)<br/>• Validates Sequence / Acknowledgment Numbers<br/>• Permits Return Traffic Automatically"]
        end
        
        subgraph Gen3["Generation 3: Application Gateway / Next-Gen Firewalls"]
            NGFW["Full Application Layer Inspection (Layer 7)<br/>• Decrypts TLS / SSL Traffic<br/>• Deep Packet Inspection (DPI) for Malicious Payloads<br/>• Reassembles Application Streams (HTTP, DNS, SMB)"]
        end
        
        Gen1 --> Gen2 --> Gen3
    end
    
    style Firewall_Generations fill:#fdfefe,stroke:#34495e,stroke-width:2px;
    style Gen1 fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
    style Gen2 fill:#fcf3cf,stroke:#f39c12,stroke-width:2px;
    style Gen3 fill:#d4efdf,stroke:#27ae60,stroke-width:2px;
```

### Comparative Firewall Engine Mechanics

| Feature / Capability | Stateless Packet Filter | Stateful Inspection Firewall | Application Layer Gateway (Proxy / NGFW) |
| :--- | :--- | :--- | :--- |
| **OSI Layer** | Layer 3 & Layer 4 | Layer 3 & Layer 4 (State-aware) | Layer 7 (Application Layer) |
| **Performance / Throughput** | Maximum (Line rate, ASIC accelerated) | High (State table lookup) | Moderate to Low (CPU intensive stream reassembly) |
| **Connection State Awareness** | None. Treats every packet as an isolated event. | Yes. Tracks TCP states (`NEW`, `ESTABLISHED`, `RELATED`). | Full protocol state machine modeling. |
| **Egress Inspection** | Must open static high ports ($>1023$) for replies. | Automatically allows valid response packets. | Proxies connection; client never talks directly to server. |
| **Payload / Exploit Inspection** | Zero payload inspection. | Zero payload inspection. | Inspects application payloads, detects SQLi, XSS, malware. |
| **Vulnerability to Spoofing** | Highly vulnerable to forged TCP flag combinations. | Resilient: Drops packets with invalid state transitions. | Immune to transport spoofing. |

---

## 1.5 Virtualization Security & Hypervisor Architectures

Modern cloud platforms run entirely on virtualized abstractions. Virtualization separates physical hardware from running operating systems via the **Hypervisor** (or Virtual Machine Monitor - VMM).

```mermaid
graph TD
    subgraph Hypervisor_Types["Type 1 vs Type 2 Hypervisor Architectures"]
        direction LR
        
        subgraph Type1["Type 1: Bare-Metal Hypervisor"]
            HW1["Bare-Metal Physical Hardware"]
            HYP1["Type 1 Hypervisor (VMware ESXi, Xen, KVM)"]
            VM1_1["Guest VM 1"]
            VM1_2["Guest VM 2"]
            HW1 --> HYP1 --> VM1_1
            HYP1 --> VM1_2
        end
        
        subgraph Type2["Type 2: Hosted Hypervisor"]
            HW2["Physical Hardware"]
            HOST_OS["Host Operating System (Windows / macOS)"]
            HYP2["Type 2 Hypervisor (VirtualBox, VMware Workstation)"]
            VM2_1["Guest VM 1"]
            VM2_2["Guest VM 2"]
            HW2 --> HOST_OS --> HYP2 --> VM2_1
            HYP2 --> VM2_2
        end
    end
    
    style Hypervisor_Types fill:#fdfefe,stroke:#2c3e50,stroke-width:2px;
    style Type1 fill:#d4efdf,stroke:#27ae60,stroke-width:2px;
    style Type2 fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
```

### Virtualization Attack Vectors
1. **VM Escape**: An exploit where code executing within a guest virtual machine breaks through isolation boundaries to execute arbitrary code within the host hypervisor context (e.g., VENOM vulnerability in virtual floppy disk controllers).
2. **Cross-VM Side-Channel Attacks**: Exploiting shared physical hardware resources (shared CPU L3 caches, memory controllers, branch prediction units) to infer cryptographic keys or keystroke timings from a co-located tenant VM (e.g., Flush+Reload, Prime+Probe).
3. **Hyperjacking**: The covert installation of a malicious hypervisor beneath a running host operating system, granting the attacker stealth persistence beneath all OS-level antivirus and monitoring tooling.

---
"""

module2_content = """# Module 2: Windows Operating System Security Architecture & Process Execution

## 2.1 The Windows Security Model: SIDs, Tokens & Descriptors

The Microsoft Windows NT operating system architecture enforces access control via the **Security Reference Monitor (SRM)**, an executive component residing within the Windows kernel (`ntoskrnl.exe`).

Whenever a thread attempts to access an object (such as a file, registry key, process, or semaphore), the SRM evaluates the thread's **Access Token** against the target object's **Security Descriptor**.

```mermaid
graph TD
    subgraph Windows_Security_Architecture["Windows Object Access Control Evaluation Pipeline"]
        direction TB
        
        Subject["Subject Thread<br/>(Possesses Access Token)"]
        
        subgraph Access_Token["Access Token Anatomy"]
            User_SID["User SID: S-1-5-21-..."]
            Group_SIDs["Group SIDs: Administrators, Users"]
            Privileges["Privileges: SeDebugPrivilege, SeBackupPrivilege"]
            Impersonation["Impersonation Level: Anonymous, Identify, Impersonate"]
        end
        
        Subject --> Access_Token
        
        SRM["Security Reference Monitor (SRM)<br/>Evaluates Desired Access against DACL ACEs"]
        
        subgraph Security_Descriptor["Target Object Security Descriptor"]
            Owner_SID["Owner SID"]
            Primary_Group["Primary Group SID"]
            DACL["Discretionary Access Control List (DACL)<br/>• ACE 1: Access Denied (Attacker_SID)<br/>• ACE 2: Access Allowed (Domain_Admins, Full Control)"]
            SACL["System Access Control List (SACL)<br/>(Governs Security Auditing & Event Logging)"]
        end
        
        Access_Token --> SRM
        Security_Descriptor --> SRM
        
        SRM -->|DACL Match: Permit| Granted["Access Granted: Handle Created"]
        SRM -->|DACL Denied: Abort| Denied["Access Denied: STATUS_ACCESS_DENIED"]
    end
    
    style Windows_Security_Architecture fill:#f9f9f9,stroke:#34495e,stroke-width:2px;
    style Access_Token fill:#ebf5fb,stroke:#2980b9,stroke-width:2px;
    style Security_Descriptor fill:#fef9e7,stroke:#f39c12,stroke-width:2px;
    style Granted fill:#d4efdf,stroke:#27ae60,stroke-width:2px;
    style Denied fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
```

### Components of the Access Evaluation Engine
1. **Security Identifier (SID)**:
   - A variable-length binary string uniquely identifying a security principal (user, security group, or computer).
   - Formatted as `S-R-I-S-S...` (e.g., `S-1-5-32-544` represents the well-known local Administrators group; `S-1-5-18` represents `NT AUTHORITY\\SYSTEM`).
2. **Access Token**:
   - Represents the security context of a process or thread. Created by the Local Security Authority Subsystem Service (`LSASS.exe`) upon successful logon.
   - Contains: User SID, Group SIDs, Restricted SIDs, Authentication ID, Privileges, and Token Type (Primary vs. Impersonation).
3. **Security Descriptor (SD)**:
   - Accompanies every securable Windows kernel object.
   - Contains:
     - **DACL (Discretionary Access Control List)**: Contains Access Control Entries (ACEs) specifying who can perform what operations (`GENERIC_READ`, `GENERIC_WRITE`, `DELETE`).
     - **SACL (System Access Control List)**: Contains ACEs dictating which access attempts generate audit event records in the Windows Security Event Log.
4. **DACL Evaluation Rules**:
   - Evaluated sequentially from top to bottom.
   - **Explicit Access Denied ACEs take precedence over Access Allowed ACEs**.
   - If a requested permission is not explicitly permitted by the time the end of the DACL is reached, access is **implicitly denied**.
   - A NULL DACL grants full access to everyone; an empty DACL (zero ACEs) denies access to all subjects.

---

## 2.2 Windows Messaging Subsystem & Shatter Attacks

Windows GUI applications are event-driven, operating via the **Windows Messaging Subsystem** implemented in `win32k.sys` (kernel space) and `user32.dll` (user space).

Processes communicate with windows and UI elements using the `SendMessage` and `PostMessage` Win32 APIs, targeting specific **Window Handles (`HWND`)**.

```mermaid
sequenceDiagram
    autonumber
    participant Attacker as Unprivileged Local Process (Low Integrity)
    participant Win32k as win32k.sys (Window Message Router)
    participant PrivService as Elevated Service GUI (SYSTEM Integrity)

    Attacker->>Win32k: Scans desktop for elevated HWNDs
    Win32k-->>Attacker: Returns HWND of elevated SYSTEM utility
    Attacker->>Win32k: Injects Malicious Message: WM_TIMER with Shellcode Callback Pointer
    Win32k->>PrivService: Dispatches Window Message to Message Queue
    Note over PrivService: Elevated Process executes Shellcode in SYSTEM Context!
    PrivService->>Attacker: Spawns Interactive Command Prompt with SYSTEM Privileges
```

### The Shatter Attack Mechanism
In legacy Windows architectures (Windows 2000, XP, Server 2003):
1. Services running as `NT AUTHORITY\\SYSTEM` could be configured with the "Interact with Desktop" flag, allowing them to render status dialogs on the interactive user desktop (`WinSta0`).
2. Because all processes within the same desktop shared a unified window message space, a low-privileged local user could discover the `HWND` of the elevated window.
3. By issuing `SendMessage` with message IDs such as `WM_TIMER` or `EM_SETWORDBREAKPROC`, the unprivileged process passed a function pointer pointing to injected shellcode.
4. The elevated process dispatched the message and executed the attacker's shellcode with full `SYSTEM` privileges.
5. **Modern Mitigations**: Microsoft introduced **User Interface Privilege Isolation (UIPI)** and mandatory integrity levels in Windows Vista, completely blocking lower-integrity processes from sending window messages to higher-integrity windows.

---

## 2.3 The Windows PE Program Execution Lifecycle

When an executable binary (Portable Executable - PE format) is launched, the Windows kernel and user-mode subsystems execute an elaborate, multi-stage initialization workflow:

```mermaid
graph TD
    subgraph PE_Execution_Pipeline["Windows Process Creation & Execution Lifecycle"]
        direction TB
        
        Step1["1. API Invocation (CreateProcessW / NtCreateUserProcess)"]
        Step2["2. PE Header Validation (e_magic 'MZ', Signature 'PE\\0\\0', Architecture)"]
        Step3["3. Process Kernel Object Allocation (EPROCESS, KPROCESS, Initial Page Directory)"]
        Step4["4. Virtual Address Space Setup & Section Mapping (NT Header, .text, .data, .rsrc)"]
        Step5["5. Subsystem Notification (CsrClientCallServer -> CSRSS / Subsystem Setup)"]
        Step6["6. Initial Thread Instantiation (ETHREAD, KTHREAD, TEB, Initial Stack)"]
        Step7["7. User-Mode Loader Execution (ntdll.dll!LdrInitializeThunk)<br/>• Imports Resolution (IAT Binding)<br/>• Base Relocations (ASLR Fixups)<br/>• TLS Callbacks Executed"]
        Step8["8. Execution Handoff: Jump to PE Entry Point (main / WinMain)"]
        
        Step1 --> Step2 --> Step3 --> Step4 --> Step5 --> Step6 --> Step7 --> Step8
    end
    
    style PE_Execution_Pipeline fill:#fcfcfc,stroke:#34495e,stroke-width:2px;
    style Step3 fill:#ebf5fb,stroke:#2980b9,stroke-width:2px;
    style Step4 fill:#fef9e7,stroke:#f39c12,stroke-width:2px;
    style Step7 fill:#e8f8f5,stroke:#27ae60,stroke-width:2px;
    style Step8 fill:#d4efdf,stroke:#2ecc71,stroke-width:2px;
```

### Detailed Execution Stages
1. **Validation & Image Conversion**:
   - The kernel validates DOS header `IMAGE_DOS_HEADER.e_magic` (`0x5A4D` / `MZ`).
   - Validates `IMAGE_NT_HEADERS.Signature` (`0x00004550` / `PE\\0\\0`).
   - Checks PE architecture (x86 32-bit vs. x64 64-bit) and subsystem (`IMAGE_SUBSYSTEM_WINDOWS_GUI` vs. `CUI`).
2. **Process Object Creation**:
   - The kernel allocates the executive process block (`EPROCESS`) in non-paged kernel pool memory.
   - Allocates the root page table directory (CR3 register context) establishing a private virtual address space.
3. **Section Mapping**:
   - Maps the executable image sections into the address space:
     - `.text` (Executable code, marked `PAGE_EXECUTE_READ`).
     - `.rdata` (Read-only data, strings, import descriptors).
     - `.data` (Global initialized variables, marked `PAGE_READWRITE`).
     - `.reloc` (Relocation tables for Address Space Layout Randomization).
4. **User-Mode Loader Initialization (`LdrInitializeThunk`)**:
   - The thread begins execution in user mode at `ntdll!LdrInitializeThunk`.
   - Resolves all dependent Dynamic Link Libraries (DLLs) specified in the Import Directory Table.
   - Populates the **Import Address Table (IAT)** with runtime memory addresses of imported Win32 APIs.
   - Executes **Thread Local Storage (TLS) Callbacks** (frequently abused by malware to execute malicious code *before* the application entry point is reached).
5. **Entry Point Dispatch**:
   - Control is handed over to the entry point address recorded in `IMAGE_OPTIONAL_HEADER.AddressOfEntryPoint`.

---
"""

module3_content = """# Module 3: Attacker Infrastructure, Anonymization & Tunneling Techniques

## 3.1 Proxies, Relays & Anonymization Networks

Sophisticated cyber adversaries decouple their physical identity and location from target victim networks by routing attacks through complex layers of intermediate proxies and anonymization circuits.

```mermaid
graph LR
    subgraph Proxy_Topologies["Anonymization & Proxy Relaying Pipeline"]
        direction LR
        Attacker["Attacker<br/>(Adversary Terminal)"] --> P1["HTTP / SOCKS5 Proxy 1<br/>(Compromised IoT Node)"]
        P1 --> P2["Open Relay Proxy 2<br/>(Bulletproof Hoster)"]
        P2 --> P3["Exit Node / SOCKS Proxy 3<br/>(Compromised Web Server)"]
        P3 --> Target["Victim Enterprise Network<br/>(Logs show only Proxy 3 IP)"]
    end
    
    style Proxy_Topologies fill:#fdfefe,stroke:#2c3e50,stroke-width:2px;
    style Attacker fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
    style Target fill:#d4efdf,stroke:#27ae60,stroke-width:2px;
```

### Proxy Protocols & Characteristics
1. **HTTP / HTTPS Proxies**:
   - Designed for application-level forwarding of web traffic.
   - *HTTP CONNECT Method*: Enables transparent tunneling of encrypted TLS connections through the proxy without terminating the SSL session.
   - *Header Leakage*: Misconfigured proxies often insert headers exposing the real source IP address:
     - `X-Forwarded-For: <Client_IP>`
     - `Via: <Proxy_Identifier>`
     - `Client-IP: <Original_IP>`
2. **SOCKS Proxies (SOCKS4 / SOCKS5)**:
   - Operates at the transport layer (Layer 5), protocol-agnostic.
   - *SOCKS4*: Supports only IPv4 TCP connections; cannot resolve hostnames on the proxy side (leading to DNS leakage at the client).
   - *SOCKS5*: Supports IPv4, IPv6, UDP relaying, authentication schemes, and proxy-side DNS resolution (preventing client DNS leaks).
3. **The Onion Router (TOR)**:
   - Routes traffic through volunteer-operated distributed overlay networks.
   - Employs **multi-layered onion routing**:
     - Client negotiates a 3-hop circuit: Guard Node $\\rightarrow$ Middle Relay $\\rightarrow$ Exit Node.
     - Payload is encrypted with 3 layers of AES keys. Each node peels off exactly one layer of encryption, learning only the immediate preceding and succeeding nodes.
     - The Exit Node connects to the target destination. Destination logs record only the IP address of the TOR Exit Node.

---

## 3.2 Covert Tunneling & Protocol Smuggling

Security perimeters frequently enforce strict egress filtering, permitting outbound traffic only over standard ports (such as HTTP port 80, HTTPS port 443, and DNS port 53). Adversaries bypass egress controls by **tunneling** unauthorized protocols (e.g., interactive command shells, file transfers, malware C2) inside legitimate carrier protocols.

```mermaid
graph TD
    subgraph DNS_Tunneling_Architecture["Covert DNS Tunneling & Data Exfiltration Mechanism"]
        direction TB
        
        Victim["Compromised Internal Host<br/>(Firewall blocks direct outbound TCP/UDP)"]
        Resolver["Enterprise Internal Recursive DNS<br/>(Permitted Outbound Port 53 UDP)"]
        Authoritative["Attacker Authoritative Name Server<br/>(Controlled by Threat Actor)"]
        C2_App["Attacker C2 Controller<br/>(Reassembles Decoded Shell/Files)"]
        
        Victim -->|"1. Query: b64enc_chunk1.malicious.net"| Resolver
        Resolver -->|"2. Recursive Lookup via Root/TLD"| Authoritative
        Authoritative -->|"3. Reassembles Exfiltrated Base64 Data"| C2_App
        Authoritative -->>|"4. Returns TXT Record with Staged Command"| Resolver
        Resolver -->>|"5. Delivers Command Payload"| Victim
    end
    
    style DNS_Tunneling_Architecture fill:#f9f9f9,stroke:#34495e,stroke-width:2px;
    style Victim fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
    style Resolver fill:#fef9e7,stroke:#f39c12,stroke-width:2px;
    style Authoritative fill:#ebf5fb,stroke:#2980b9,stroke-width:2px;
    style C2_App fill:#d4efdf,stroke:#27ae60,stroke-width:2px;
```

### Tunneling Modalities
1. **HTTP/HTTPS Tunneling**:
   - Encapsulates raw TCP connections inside standard HTTP `POST` requests or WebSocket channels. Data payloads are base64-encoded or XOR-scrambled inside innocent-looking HTTP request bodies (e.g., mimicking JSON analytics beacons or JPEG image uploads).
2. **DNS Tunneling**:
   - Encapsulates bidirectional communication inside DNS query and response records.
   - *Exfiltration (Outbound)*: Data is segmented, encoded into subdomain labels, and prepended to the attacker's domain (e.g., `cmVnaXN0cnlfZHVtcA==.c2.attacker.com`).
   - *Infiltration (Inbound C2)*: The attacker's authoritative nameserver responds with base64-encoded commands packed into `TXT`, `CNAME`, or `NULL` records.
   - *Detection Indicators*: Unusually high query volume to single apex domains, abnormally long domain labels ($>50$ characters), high Shannon entropy in subdomains, and an abnormal ratio of `TXT` record queries.
3. **ICMP Tunneling**:
   - Exploits the optional data payload field of ICMP Echo Request (`ping` type 8) and Echo Reply (type 0) packets.
   - Utilities like `ptunnel` insert arbitrary TCP streams into the ICMP data payload, evading firewalls that permit ICMP echo without inspecting payload bytes.

---

## 3.3 Botnet Command & Control (C2) Architectures

A **botnet** is a distributed network of compromised computing nodes (bots/zombies) controlled remotely by a threat actor (botmaster) to conduct distributed denial-of-service (DDoS) campaigns, click fraud, credential stuffing, and mass spam distribution.

```mermaid
graph TD
    subgraph Botnet_Architectures["Comparison of Botnet Topologies"]
        direction LR
        
        subgraph Centralized["1. Centralized C2 (IRC / HTTP)"]
            BM1["Botmaster"] --> C2_Server["Central C2 Server"]
            C2_Server --> B1["Bot 1"]
            C2_Server --> B2["Bot 2"]
            C2_Server --> B3["Bot 3"]
        end
        
        subgraph P2P["2. Peer-to-Peer (P2P) Distributed C2"]
            BM2["Botmaster"] -.-> PB1["Peer Bot A"]
            PB1 <--> PB2["Peer Bot B"]
            PB2 <--> PB3["Peer Bot C"]
            PB1 <--> PB4["Peer Bot D"]
        end
    end
    
    style Centralized fill:#ebf5fb,stroke:#2980b9,stroke-width:2px;
    style P2P fill:#e8f8f5,stroke:#27ae60,stroke-width:2px;
    style C2_Server fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
```

### Architectural Evolutions
1. **Centralized C2 (IRC / HTTP / HTTPS)**:
   - Early botnets utilized Internet Relay Chat (IRC) channels. Bots connected to a hidden chatroom, executing commands issued by the botmaster.
   - Modern centralized botnets utilize HTTPS web servers, periodic polling beacons, and Domain Generation Algorithms (DGA).
   - *Vulnerability*: Single point of failure. Law enforcement and security teams can seize the C2 server IP or sinkhole the domain name, instantly severing the entire botnet.
2. **Peer-to-Peer (P2P) Botnets (e.g., Storm, Zeus Gameover)**:
   - Bots communicate with each other using distributed hash tables (DHT) and custom overlay protocols.
   - No single central server exists. Commands are cryptographically signed with the botmaster's asymmetric private key and gossiped through the peer network.
   - Defeats simple IP-blocking and domain takedown actions; dismantling requires poisoning peer routing tables or sybil attacks.

---

## 3.4 Fast-Flux DNS & Resilient Hosting Networks

To prevent defenders from taking down command-and-control servers via IP blocking, botmasters deploy **Fast-Flux DNS** networks.

```mermaid
graph TD
    subgraph Fast_Flux_Mechanics["Single-Flux vs Double-Flux Architecture"]
        direction TB
        
        subgraph SingleFlux["Single-Flux DNS"]
            Domain1["c2.botnet.com<br/>(TTL = 60 to 300 seconds)"]
            Domain1 --> IP1["Compromised Host IP 1 (Reverse Proxy)"]
            Domain1 --> IP2["Compromised Host IP 2 (Reverse Proxy)"]
            Domain1 --> IP3["Compromised Host IP 3 (Reverse Proxy)"]
            
            IP1 -.-> RealC2_1["Mothership C2 Server (Hidden)"]
            IP2 -.-> RealC2_1
            IP3 -.-> RealC2_1
        end
        
        subgraph DoubleFlux["Double-Flux DNS (Maximum Resilience)"]
            Domain2["c2.botnet.com"]
            NS_Rec["NS Records (ns1.botnet.com)<br/>(Also Rapidly Fluctuating IPs!)"]
            Domain2 --> NS_Rec
            NS_Rec --> FluxNS1["Flux Nameserver IP A"]
            NS_Rec --> FluxNS2["Flux Nameserver IP B"]
            Domain2 --> FluxIPs["Rapidly Fluctuating Proxy IPs..."]
        end
    end
    
    style Fast_Flux_Mechanics fill:#f9f9f9,stroke:#34495e,stroke-width:2px;
    style SingleFlux fill:#ebf5fb,stroke:#2980b9,stroke-width:2px;
    style DoubleFlux fill:#fef9e7,stroke:#f39c12,stroke-width:2px;
    style RealC2_1 fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
```

### Fast-Flux Implementations
1. **Single-Flux DNS**:
   - The FQDN's `A` records are constantly rotated, returning a different pool of IP addresses on every query.
   - DNS TTL values are set to extremely short durations (e.g., 60 to 300 seconds).
   - The IP addresses returned belong to a swarm of compromised volunteer or consumer hosts executing lightweight reverse-proxy software (e.g., Nginx or custom redirector daemons) that transparently forward traffic back to a hidden backend "mothership" C2 server.
2. **Double-Flux DNS**:
   - Both the **A records** of the domain AND the **NS records** (the authoritative nameservers for the domain) rapidly fluctuate across hundreds of compromised IP addresses.
   - Eliminates the vulnerability of relying on static nameservers. Takedown requires direct intervention at the parent Top-Level Domain (TLD) registrar registry level to revoke the domain delegation.

---
"""

module4_content = """# Module 4: Social Engineering, Fraud & Deception Campaigns

## 4.1 Social Engineering Vectors: Phishing, Smishing & Vishing

While technical exploits target vulnerabilities in software and hardware architectures, **social engineering** exploits psychological vulnerabilities in human cognition (authority, urgency, fear, greed, curiosity, and reciprocity).

```mermaid
graph TD
    subgraph Social_Engineering_Matrix["Taxonomy of Social Engineering Attack Vectors"]
        direction TB
        
        MassPhish["Mass Phishing<br/>(Untargeted, high-volume generic email lures)"]
        SpearPhish["Spear-Phishing<br/>(Targeted lures using bespoke intelligence)"]
        Whaling["Whaling<br/>(Targeting C-suite Executives & Board Members)"]
        Smishing["Smishing (SMS Phishing)<br/>(Urgent text messages impersonating delivery/banks)"]
        Vishing["Vishing (Voice Phishing)<br/>(Voice phone calls impersonating IT Helpdesk / Telecom)"]
        Deepfake["AI-Generated Deepfakes<br/>(Synthetic audio/video impersonating leadership)"]
        
        MassPhish --> SpearPhish --> Whaling
        Smishing --> Vishing --> Deepfake
    end
    
    style Social_Engineering_Matrix fill:#fdfefe,stroke:#2c3e50,stroke-width:2px;
    style MassPhish fill:#ebf5fb,stroke:#2980b9,stroke-width:2px;
    style SpearPhish fill:#fef9e7,stroke:#f39c12,stroke-width:2px;
    style Whaling fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
    style Deepfake fill:#f4ecf7,stroke:#8e44ad,stroke-width:2px;
```

### Exploitation Mechanics
1. **Spear-Phishing & Business Email Compromise (BEC)**:
   - Adversaries conduct extensive Open-Source Intelligence (OSINT) gathering across LinkedIn, corporate press releases, and vendor associations.
   - Construct contextual lures mimicking internal workflows (e.g., urgent invoice approval, shared OneDrive documentation, travel reimbursement).
   - Exploits email spoofing vulnerabilities (lack of strict SPF, DKIM, and DMARC enforcement).
2. **Smishing & Vishing**:
   - Bypasses enterprise email security gateways entirely by targeting mobile devices directly.
   - Exploits caller-ID spoofing to impersonate internal corporate IT support desks, tricking users into revealing MFA session codes or authenticating push notifications (MFA Fatigue / Prompt Bombing).

---

## 4.2 Rogue Antivirus & Scareware Monetization Pipelines

**Rogue Antivirus** (commonly referred to as **Scareware**) represents a highly lucrative cybercriminal monetization ecosystem that combines social engineering, web drive-by manipulation, and deceptive software engineering.

```mermaid
sequenceDiagram
    autonumber
    participant Victim as Victim Browser
    participant Malvertising as Malicious Ad Network
    participant Scareware as Rogue AV Landing Page
    participant Payment as Illicit Merchant Processor
    participant Cybercrime as Threat Syndicate

    Victim->>Malvertising: Visits legitimate news site hosting compromised ad
    Malvertising->>Victim: Injects deceptive JavaScript redirect
    Victim->>Scareware: Renders fake Windows Blue Screen / Virus Alert dialogs
    Note over Scareware: Simulates rapid scan of C:\ showing 487 'Infections'
    Scareware->>Victim: Prompts user to download 'AntivirusScanner2026.exe'
    Victim->>Victim: Installs executable (Disables legitimate Defender, generates popups)
    Victim->>Payment: Submits credit card to buy 'Full License Activation'
    Payment->>Cybercrime: Funds laundered through offshore shell companies
```

### Architectural Characteristics of Rogue Antivirus
1. **Drive-By Social Engineering**:
   - Uses browser locking techniques (infinite JavaScript loops, full-screen canvas rendering mimicking OS error dialogs) to induce panic.
2. **System Subversion**:
   - Once executed, the binary adds itself to registry startup keys (`HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run`).
   - Terminates genuine antivirus processes (`taskkill /f /im msmpeng.exe`), modifies the Windows `hosts` file to block access to security vendors, and continuously displays fake alert notifications.
3. **Monetization Pipeline**:
   - The software insists that removal of the "critical trojans" requires purchasing a lifetime software license for $49.99 to $99.99.
   - Credit card transactions are funneled through shadowy merchant accounts, resulting in direct financial fraud and credit card data harvesting.

---

## 4.3 Click Fraud Architecture & Pay-Per-Click Exploitation

Digital advertising is dominated by the **Pay-Per-Click (PPC)** model, where advertisers pay ad networks (such as Google AdSense, Bing Ads) every time an Internet user clicks an advertisement.

**Click Fraud** occurs when an automated software program, script, or human click-farm intentionally generates fraudulent clicks on online advertisements without genuine user interest, siphoning billions of dollars from advertisers.

```mermaid
graph TD
    subgraph Click_Fraud_Topology["Mechanics of Botnet Click Fraud"]
        direction TB
        
        Advertiser["Legitimate Advertiser<br/>(Allocates $100k Ad Budget)"]
        AdNetwork["Ad Exchange / Ad Network<br/>(Charges per click, pays publisher fee)"]
        FraudSite["Adversary-Controlled Publisher Website<br/>(Hosts embedded PPC ad banners)"]
        Botnet["Distributed Zombie Botnet<br/>(Thousands of compromised endpoints)"]
        
        Advertiser -->|Pays Ad Budget| AdNetwork
        AdNetwork -->|Serves Ads to Publisher| FraudSite
        
        Botnet -->|"Automated Headless Browser Clicks<br/>(Simulates mouse moves, scrolls, clicks)"| FraudSite
        FraudSite -->|Registers Valid Ad Click Events| AdNetwork
        AdNetwork -->|Payouts 60-70% Revenue Share| Adversary["Cybercriminal Publisher Account"]
    end
    
    style Click_Fraud_Topology fill:#fdfefe,stroke:#2c3e50,stroke-width:2px;
    style Advertiser fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
    style AdNetwork fill:#fef9e7,stroke:#f39c12,stroke-width:2px;
    style FraudSite fill:#ebf5fb,stroke:#2980b9,stroke-width:2px;
    style Botnet fill:#f4ecf7,stroke:#8e44ad,stroke-width:2px;
    style Adversary fill:#d4efdf,stroke:#27ae60,stroke-width:2px;
```

### Click Fraud Tactics
1. **Hidden Iframes & Ad Stacking**:
   - The fraudulent website loads ad banners inside invisible $1\\times 1$ pixel iframes or stacks dozens of ad banners directly on top of each other. A single user click registers dozens of simultaneous ad impressions and clicks.
2. **Automated Headless Browsers**:
   - Botnets embed headless browser engines (e.g., Puppeteer, Playwright, or modified WebKit runtimes) within infected zombie machines.
   - To defeat heuristic fraud detection, bots simulate realistic human behaviors: randomized mouse movements, natural page scrolling, random dwell times, and visiting secondary landing pages before exiting.

---
"""

with open("cyber-security/modules/module1.md", "w") as f:
    f.write(module1_content.strip() + "\n")

with open("cyber-security/modules/module2.md", "w") as f:
    f.write(module2_content.strip() + "\n")

with open("cyber-security/modules/module3.md", "w") as f:
    f.write(module3_content.strip() + "\n")

with open("cyber-security/modules/module4.md", "w") as f:
    f.write(module4_content.strip() + "\n")

print("Generated Modules 1 to 4 successfully.")
