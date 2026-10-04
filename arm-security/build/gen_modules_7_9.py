#!/usr/bin/env python3
"""
Generator for Modules 7 to 9 of the ARM Security Architecture Reference Guide.
"""

import os

os.makedirs("arm-security/modules", exist_ok=True)

module7_content = """# Module 7: Realm Lifecycle, Execution Contexts (REC) & Stage-2 Translation (RTT)

## 7.1 Realm Lifecycle State Machine

A Realm undergoes a deterministic, cryptographically tracked lifecycle enforced by the Realm Management Monitor (RMM). The RMM maintains a state variable within the Realm Descriptor (`RD`), governing permissible operations at each stage of execution.

```mermaid
stateDiagram-v2
    [*] --> NEW: RMI_REALM_CREATE
    
    state NEW {
        [*] --> Populating_Memory
        Populating_Memory --> RTT_Tree_Built: RMI_RTT_CREATE
        RTT_Tree_Built --> Granules_Added: RMI_DATA_CREATE
        Granules_Added --> Initial_Measurements_Hashed: Measures into RIM
        Initial_Measurements_Hashed --> RECs_Created: RMI_REC_CREATE
    }
    
    NEW --> ACTIVE: RMI_REALM_ACTIVATE<br/>(Locks RIM, Enables Execution)
    
    state ACTIVE {
        [*] --> Running_In_Realm
        Running_In_Realm --> Exited_To_Host: RMI_REC_EXIT (Interrupt / Trap)
        Exited_To_Host --> Running_In_Realm: RMI_REC_ENTER
        Running_In_Realm --> Dynamic_Memory_Transitions: RSI_IPA_STATE_SET
    }
    
    ACTIVE --> SYSTEM_OFF: PSCI_SYSTEM_OFF / Fatal Fault
    SYSTEM_OFF --> DESTROYING: RMI_REALM_DESTROY
    ACTIVE --> DESTROYING: RMI_REALM_DESTROY
    
    state DESTROYING {
        [*] --> Reclaiming_Granules: RMI_DATA_DESTROY (Zeroed)
        Reclaiming_Granules --> Tearing_Down_RTT: RMI_RTT_DESTROY
        Tearing_Down_RTT --> Reclaiming_RECs: RMI_REC_DESTROY
    }
    
    DESTROYING --> [*]: RD Deallocated (Memory returned to NS-PAS)
```

### Architectural States
1. **`NEW` State**:
   - The Realm is instantiated via `RMI_REALM_CREATE`.
   - The Host Hypervisor builds the initial Realm Translation Table (RTT) hierarchy and populates the Realm's initial firmware and boot parameters via `RMI_DATA_CREATE`.
   - Every byte of code and data loaded during the `NEW` state is measured by the RMM using a cryptographic hash function (SHA-256 or SHA-512) and accumulated into the **Realm Initial Measurement (RIM)** register.
   - Virtual CPUs are instantiated by creating **Realm Execution Contexts (RECs)** via `RMI_REC_CREATE`.
2. **`ACTIVE` State**:
   - The host issues `RMI_REALM_ACTIVATE`.
   - **The RIM register is permanently locked**. No further code or data can be added to the Realm without altering runtime measurements.
   - The Realm enters the execution phase. RECs can now be scheduled and entered using `RMI_REC_ENTER`.
3. **`SYSTEM_OFF` / `DESTROYING` State**:
   - Triggered when the Realm executes a power-off call (`PSCI_SYSTEM_OFF`) or when the host terminates the Realm.
   - The host tears down the Realm by destroying RECs, dismantling the RTT tree, and returning memory granules to Non-Secure PAS via `RMI_DATA_DESTROY`.
   - **Hardware Invariant**: The RMM refuses to deallocate the Realm Descriptor (`RD`) until every single memory granule, RTT node, and REC assigned to the Realm has been zeroed, scrubbed, and transitioned back to Non-Secure PAS.

---

## 7.2 Realm Execution Context (REC) & Scheduling

A **Realm Execution Context (REC)** represents the architectural state of a virtual CPU allocated to a Realm. 

Because the Host Hypervisor is outside the TCB, it cannot directly inspect or modify the virtual CPU registers. Instead, CPU state is bifurcated across two structures:
1. **Host-Visible REC Buffer**: Contains only operational scheduling metadata (exit reason, interrupt injection flags, timer values).
2. **Private REC Context (Inside Realm PAS)**: Contains general-purpose registers (`X0`–`X30`), stack pointers (`SP_EL0`, `SP_EL1`), program counter (`PC`), Process State (`PSTATE`), Floating-Point/Neon/SVE vector registers, and Realm-private system registers.

```mermaid
sequenceDiagram
    autonumber
    participant Host as Host KVM (NS-EL2)
    participant EL3 as Root Monitor (TF-A)
    participant RMM as Realm Mgmt Monitor (R-EL2)
    participant Core as Physical CPU Core (R-EL1)

    Note over Host,Core: Context Entry Flow
    Host->>EL3: SMC RMI_REC_ENTER(REC_Address, Run_Buffer)
    EL3->>RMM: Dispatches to RMM at R-EL2
    RMM->>RMM: Validates REC parameters & checks Active state
    RMM->>RMM: Configures Stage-2 Translation Base (VTCR_EL2, VTTBR_EL2)
    RMM->>Core: Restores X0-X30, PC, PSTATE & executes ERET
    
    Note over Core: Realm Executes Securely at R-EL1/R-EL0
    Core->>Core: Executes Guest OS & Applications
    
    Note over Host,Core: Context Exit Flow (e.g., Guest accesses emulated VirtIO MMIO)
    Core->>RMM: Synchronous Trap to R-EL2 (Stage-2 Data Abort)
    RMM->>RMM: Saves Realm Register State into Private REC Context
    RMM->>RMM: Scrubs Core Registers (zeros out X0-X30 to prevent leakage)
    RMM->>RMM: Populates Run_Buffer with minimal Exit Reason & Fault IPA
    RMM->>EL3: SMC return to EL3
    EL3->>Host: Returns to KVM at NS-EL2 with sanitized Exit Info
```

### Context Entry & Exit Lifecycle
- **Context Entry (`RMI_REC_ENTER`)**:
  - The host issues an `RMI_REC_ENTER` SMC call, passing the physical address of the REC and a shared communication page (`rec_run`).
  - The RMM configures hardware virtualization controls: the Virtualization Translation Control Register (`VTCR_EL2`) and Virtualization Translation Table Base Register (`VTTBR_EL2`) are loaded with the Realm's Stage-2 page table base.
  - The RMM restores the guest's registers and issues an `ERET` instruction into Realm EL1.
- **Context Exit (`RMI_REC_EXIT`)**:
  - Exits occur on:
    - **Physical Interrupts**: A physical host timer or network interrupt asserts while executing in Realm mode.
    - **Hypercalls / Traps**: The guest issues an `HVC` instruction or performs an access to an unmapped IPA (e.g., MMIO space of an emulated device).
    - **PSCI Calls**: The guest requests a vCPU power transition.
  - The core traps to R-EL2. The RMM securely preserves the guest state, thoroughly zeroes all scratch and general-purpose registers on the physical core, and populates the `rec_run` buffer with sanitized exit metadata before relinquishing control back to `NS-EL2`.

---

## 7.3 Realm Translation Tables (RTT) & RIPAS States

Memory mapping inside a Realm is governed by a dedicated Stage-2 translation tree managed exclusively by the RMM: the **Realm Translation Table (RTT)**.

```mermaid
graph TD
    subgraph RTT_Hierarchy["Realm Translation Table (RTT) & RIPAS Architecture"]
        direction TB
        VTTBR["VTTBR_EL2 (Points to Level 0 RTT in Realm PAS)"]
        
        subgraph RTT_Tree["Stage-2 Translation Hierarchy"]
            L0["RTT Level 0 (Covering 512GB Blocks)"]
            L1["RTT Level 1 (Covering 1GB Blocks)"]
            L2["RTT Level 2 (Covering 2MB Blocks)"]
            L3["RTT Level 3 (Covering 4KB Pages)"]
            
            VTTBR --> L0
            L0 --> L1 --> L2 --> L3
        end
        
        subgraph RIPAS_States["Realm Intermediate Physical Address States (RIPAS)"]
            RIPAS_EMPTY["RIPAS_EMPTY<br/>• Unallocated IPA space<br/>• Access triggers Stage-2 Translation Fault"]
            RIPAS_RAM["RIPAS_RAM<br/>• Active private Realm memory<br/>• Backed by physical granule in Realm PAS"]
            RIPAS_DESTROYED["RIPAS_DESTROYED<br/>• Reclaimed memory granule<br/>• Access triggers fault until re-initialized"]
        end
        
        L3 --> RIPAS_States
    end
    
    style RTT_Hierarchy fill:#f9f9f9,stroke:#34495e,stroke-width:2px;
    style RTT_Tree fill:#eaf2f8,stroke:#2980b9,stroke-width:2px;
    style RIPAS_States fill:#e8f8f5,stroke:#27ae60,stroke-width:2px;
```

### Realm Intermediate Physical Address State (RIPAS)
Every Intermediate Physical Address (IPA) within a Realm's virtual address space is tagged with a **RIPAS** value:
1. **`RIPAS_EMPTY`**:
   - The address space has been defined by the hypervisor, but no physical memory granule has been assigned yet.
   - If the Realm attempts to access an address marked `RIPAS_EMPTY`, a Stage-2 translation fault is trapped to the RMM.
2. **`RIPAS_RAM`**:
   - The IPA is backed by a valid physical memory granule residing in **Realm PAS**.
   - The Realm has full read/write permissions. The Host Hypervisor cannot read or write this memory.
3. **`RIPAS_DESTROYED`**:
   - The backing physical granule has been reclaimed or torn down by the host. Any subsequent read/write by the guest will fault until the page is explicitly re-provisioned and zeroed.

### Dynamic RIPAS Transition Workflow
When an enlightened guest OS boots, it may dynamically request additional private memory or donate memory to a shared pool:
1. Guest issues an SMC call: `RSI_IPA_STATE_SET(Start_IPA, Size, Desired_RIPAS)`.
2. The RMM intercepts the call, marks the translation range as pending transition, and returns a status code signaling the host hypervisor.
3. The host hypervisor invokes `RMI_DATA_CREATE` to allocate physical memory and bind it to the IPA.
4. The RMM verifies that the backing physical granule is scrubbed and updates the RTT entry to `RIPAS_RAM`.

---

## 7.4 Interrupt Virtualization & Exception Dispatch

Confidential virtual machines must process interrupts (e.g., virtual timers, virtual network notifications) without permitting the host hypervisor to inject malicious interrupt vectors or snoop execution timing.

Arm CCA leverages the **Generic Interrupt Controller (GICv3 / GICv4)** with virtualization extensions:

```mermaid
graph TD
    subgraph Interrupt_Routing["Interrupt Handling & Virtualization Architecture"]
        direction TB
        subgraph Physical_Hardware["Physical Hardware Interrupt Controller"]
            GICD["GIC Distributor (GICD)"]
            GICR["GIC Redistributor (GICR)"]
            GICD --> GICR
        end
        
        subgraph Routing_Logic["Hypervisor & RMM Injection Logic"]
            HostRouting["Host Hypervisor (NS-EL2)<br/>• Traps physical IRQs<br/>• Decides which Realm vCPU receives virtual IRQ<br/>• Writes to rec_run.flags"]
            RMM_Injection["Realm Management Monitor (R-EL2)<br/>• Inspects rec_run<br/>• Writes to GIC List Registers (ICH_LR<n>_EL2)<br/>• Controls Virtual CPU Interface"]
        end
        
        subgraph Realm_Execution["Realm Guest (R-EL1)"]
            vCPU_IF["Virtual CPU Interface (ICH_VMCR_EL2)<br/>• Delivers Virtual IRQ to Guest Kernel<br/>• Realm handles IRQ without Host Inspection"]
        end
        
        GICR --> HostRouting
        HostRouting --> RMM_Injection
        RMM_Injection --> vCPU_IF
    end
    
    style Physical_Hardware fill:#fcf3cf,stroke:#b7950b,stroke-width:2px;
    style Routing_Logic fill:#ebf5fb,stroke:#2980b9,stroke-width:2px;
    style Realm_Execution fill:#d4efdf,stroke:#27ae60,stroke-width:2px;
```

### Interrupt Flow Mechanics
1. **Physical Interrupt Arrival**:
   - While a Realm is executing, a physical interrupt (e.g., physical NIC interrupt) fires.
   - The hardware configuration in `SCR_EL3` and `HCR_EL2` ensures the physical interrupt causes an immediate exit from Realm state to `R-EL2`.
   - The RMM sanitizes core registers and completes the context exit to `NS-EL2`. The Host Hypervisor services the physical interrupt.
2. **Virtual Interrupt Injection**:
   - When the host needs to deliver a virtual interrupt to a Realm vCPU, it cannot directly write to the GIC CPU interface registers of the Realm.
   - The host populates the `rec_run` shared structure with the target Virtual Interrupt ID (vINTID).
   - Upon the next `RMI_REC_ENTER`, the RMM parses the `rec_run` buffer, validates that the requested virtual interrupt is permissible, and writes the virtual interrupt into the hardware **GIC List Registers (`ICH_LR<n>_EL2`)**.
   - When the Realm resumes execution at R-EL1, the GIC hardware virtual CPU interface signals the interrupt directly to the guest kernel.

---
"""

module8_content = """# Module 8: Arm CCA Communication Interfaces: RMI, RSI, RHI, PSCI

## 8.1 The Realm Management Interface (RMI)

The **Realm Management Interface (RMI)** is the standard boundary interface between the **Host Hypervisor (`NS-EL2`)** and the **Realm Management Monitor (`R-EL2`)**, mediated by the Root EL3 Monitor.

All RMI operations are dispatched using the standard Arm Fast Call calling convention via `SMC` instructions, utilizing dedicated RMI Function IDs (encapsulated under the standard Arm Architecture SMC calling convention).

```mermaid
graph LR
    subgraph RMI_Boundary["Realm Management Interface (RMI) Dispatch Pipeline"]
        KVM["Host Hypervisor (Linux KVM / kvmtool)<br/>[NS-EL2]"] -->|"SMC RMI_Function_ID(Args...)"| EL3["TF-A EL3 (RMM Dispatcher)"]
        EL3 -->|"World Switch: NS -> Realm"| RMM["TF-RMM [R-EL2]<br/>Executes RMI Command"]
        RMM -->|"Returns Result Code"| EL3
        EL3 -->|"World Switch: Realm -> NS"| KVM
    end
    
    style KVM fill:#fadbd8,stroke:#c0392b,stroke-width:2px;
    style EL3 fill:#fcf3cf,stroke:#b7950b,stroke-width:2px;
    style RMM fill:#d6eaf8,stroke:#2980b9,stroke-width:2px;
```

### Comprehensive RMI Command Suite

| RMI Command Name | Key Input Parameters | Key Outputs / Effects | Architectural Purpose |
| :--- | :--- | :--- | :--- |
| **`RMI_VERSION`** | `req_version` | `ret_version` | Queries supported RMI specification version and negotiates interface level. |
| **`RMI_REALM_CREATE`** | `rd_pa`, `params_pa` | Status (`RMI_SUCCESS` / Error) | Allocates the Realm Descriptor (`RD`) granule in Realm PAS and initializes metadata. |
| **`RMI_REALM_ACTIVATE`**| `rd_pa` | Status | Finalizes the Realm Initial Measurement (RIM), permanently locking initial configuration. |
| **`RMI_REALM_DESTROY`** | `rd_pa` | Status | Tears down the Realm Descriptor once all subordinate granules have been purged. |
| **`RMI_REC_CREATE`** | `rd_pa`, `rec_pa`, `params_pa` | Status | Instantiates a virtual CPU (REC) within the Realm, binding it to the Realm Descriptor. |
| **`RMI_REC_DESTROY`** | `rec_pa` | Status | Deallocates and wipes a Realm Execution Context granule. |
| **`RMI_REC_ENTER`** | `rec_pa`, `run_pa` | Sanitized Exit Reason in `run_pa` | Context-switches physical core into Realm mode, running the target vCPU. |
| **`RMI_RTT_CREATE`** | `rd_pa`, `rtt_pa`, `ipa`, `level` | Status | Allocates a physical granule in Realm PAS to host a new Stage-2 RTT page table node. |
| **`RMI_RTT_DESTROY`** | `rd_pa`, `rtt_pa`, `ipa`, `level` | Status | Reclaims an empty RTT page table node and transitions the granule back to NS-PAS. |
| **`RMI_DATA_CREATE`** | `rd_pa`, `data_pa`, `ipa`, `src_pa`, `flags` | Status | Copies contents from `src_pa` (NS), transitions `data_pa` to Realm PAS, and updates RIM. |
| **`RMI_DATA_CREATE_UNKNOWN`** | `rd_pa`, `data_pa`, `ipa` | Status | Allocates a blank (uninitialized) page to Realm PAS without measuring content. |
| **`RMI_DATA_DESTROY`** | `rd_pa`, `data_pa` | Status | Zeroes the Realm memory granule completely and transitions its GPI back to Non-Secure. |
| **`RMI_RTT_MAP_UNPROTECTED`** | `rd_pa`, `ipa` | Status | Maps a Non-Secure physical page into the Realm's Stage-2 tables (for shared I/O). |
| **`RMI_RTT_READ_ENTRY`** | `rd_pa`, `ipa`, `level` | Entry attributes, RIPAS | Allows host to inspect translation state and RIPAS status of an IPA range. |
| **`RMI_PSCI_COMPLETE`** | `calling_rec_pa`, `target_rec_pa` | Status | Signals completion of a host-handled PSCI CPU_ON or CPU_OFF request. |

---

## 8.2 The Realm Services Interface (RSI)

The **Realm Services Interface (RSI)** is the privileged communication channel established between the **Realm Guest OS (`R-EL1`)** and the **Realm Management Monitor (`R-EL2`)**.

RSI calls are issued using `SMC` instructions executed at `R-EL1`. Unlike RMI calls (which involve EL3 world switching), RSI calls execute directly between `R-EL1` and `R-EL2` within Realm State, minimizing instruction latency.

```mermaid
graph TD
    subgraph RSI_Boundary["Realm Services Interface (RSI) Operations"]
        GuestKernel["Realm Guest Linux Kernel [R-EL1]"] -->|"SMC RSI_Function_ID(Args...)"| RMM["TF-RMM [R-EL2]"]
        
        subgraph RSI_Services["Available Services"]
            Cfg["RSI_REALM_CONFIG<br/>• Inspects Realm vCPU topology<br/>• Feature discovery"]
            IPA["RSI_IPA_STATE_SET / GET<br/>• Dynamic Memory Classification<br/>• Converts IPA to Private or Shared"]
            Attest["RSI_ATTESTATION_TOKEN_INIT / CONTINUE<br/>• Initiates crypto attestation token generation<br/>• Supplies tenant challenge nonce"]
            HostCall["RSI_HOST_CALL<br/>• Routes paravirtualized I/O request to Host"]
        end
        
        RMM --> RSI_Services
    end
    
    style GuestKernel fill:#d4efdf,stroke:#27ae60,stroke-width:2px;
    style RMM fill:#d6eaf8,stroke:#2980b9,stroke-width:2px;
    style RSI_Services fill:#fef9e7,stroke:#f39c12,stroke-width:2px;
```

### Comprehensive RSI Command Suite
1. **`RSI_ABI_VERSION`**:
   - Discovers and validates the supported RSI specification version.
2. **`RSI_REALM_CONFIG`**:
   - Returns a structured configuration descriptor containing the Realm's intermediate physical address size (`IPA_WIDTH`), hash algorithm used for attestation, and number of vCPUs.
3. **`RSI_IPA_STATE_SET` / `RSI_IPA_STATE_GET`**:
   - Used by the guest kernel memory manager to change an IPA range from `RIPAS_EMPTY` to `RIPAS_RAM` (requesting private RAM) or declaring an address range as **unprotected** (shared memory for VirtIO DMA).
4. **`RSI_ATTESTATION_TOKEN_INIT` & `RSI_ATTESTATION_TOKEN_CONTINUE`**:
   - Initiates attestation token generation. Because a signed cryptographic token can be several kilobytes in size (exceeding register space), the token is streamed into guest-provided buffer granules across multiple non-blocking calls.
5. **`RSI_MEASUREMENT_READ` & `RSI_MEASUREMENT_EXTEND`**:
   - Enables the guest to read the current RIM and write runtime measurements into the **Realm Extensible Measurements (REM[0..3])** registers (similar to extending a TPM PCR).
6. **`RSI_HOST_CALL`**:
   - Dispatches a structured hypercall request directly to the untrusted host hypervisor, carrying an address pointer to a shared Non-Secure parameter block.

---

## 8.3 The Realm Host Interface (RHI)

While the RMM provides strict isolation, real-world systems require complex communication between the Realm and the Host:
- Querying dynamic platform events.
- Attesting complex physical peripheral devices.
- Reading large platform firmware event logs.

Implementing complex parsing logic inside the RMM would bloat its TCB. Therefore, Arm defines the **Realm Host Interface (RHI)**:
- RHI defines standard protocol sets implemented by the **Host Hypervisor**, delivered to the Realm as an untrusted paravirtualized service.
- RHI traffic is tunneled through the RMM using `RSI_HOST_CALL`.

### Primary RHI Protocol Suites
1. **Host Session Protocol**:
   - Creates a generic, bidirectional communication channel between the Realm and host user-space agents (e.g., `kvmtool` or QEMU guest agent).
   - Operates in either blocking or non-blocking mode.
   - *Security Note*: Because data traversing the Host Session is provided by the untrusted host, the guest kernel must treat all incoming buffers as untrusted and authenticate payloads using end-to-end encryption (e.g., TLS or Diffie-Hellman session keys).
2. **Firmware Activity Log (FAL) Protocol**:
   - On platforms supporting live firmware activation, the platform RoT logs firmware updates in the FAL.
   - The Realm uses RHI to retrieve the FAL from the host, and subsequently validates the log against the cryptographically signed Platform Attestation Token.
3. **Device Assignment Protocol**:
   - Transfers peripheral device certificates, SPDM measurement transcripts, and PCIe IDE configuration blocks between the host orchestration stack and the Realm.

---

## 8.4 Power State Coordination Interface (PSCI) in Realms

The **Power State Coordination Interface (PSCI)** is the universal Arm standard for managing power states (CPU suspend, secondary core booting, core shutdown, and system reset).

In traditional environments, PSCI SMC calls are trapped and serviced directly by EL3 firmware. In Arm CCA, PSCI interactions are handled through a collaborative mediation flow:

```mermaid
sequenceDiagram
    autonumber
    participant Guest as Realm Guest Kernel (R-EL1)
    participant RMM as Realm Mgmt Monitor (R-EL2)
    participant Host as Host KVM (NS-EL2)

    Note over Guest,Host: Secondary Core Bootup Flow
    Guest->>RMM: SMC PSCI_CPU_ON(Target_vCPU, Entrypoint_IPA, Context_ID)
    RMM->>RMM: Validates target REC belongs to this Realm
    RMM->>RMM: Pre-configures target REC Entrypoint & PSTATE
    RMM->>Host: Exits to NS-EL2 with Exit Reason: RMI_EXIT_PSCI
    Host->>Host: Allocates physical PE thread & schedules target REC
    Host->>RMM: SMC RMI_PSCI_COMPLETE(Calling_REC, Target_REC)
    Host->>RMM: SMC RMI_REC_ENTER(Target_REC)
    RMM->>Guest: Starts execution of Secondary vCPU at Entrypoint
```

1. **`PSCI_CPU_ON`**:
   - The primary Realm vCPU issues `PSCI_CPU_ON` to boot a secondary virtual CPU.
   - The RMM intercepts the call, sets the secondary REC's program counter to the requested entrypoint, and triggers an exit to `NS-EL2`.
   - The host hypervisor spawns a host thread for the secondary vCPU and executes `RMI_PSCI_COMPLETE`.
2. **`PSCI_SYSTEM_OFF` & `PSCI_SYSTEM_RESET`**:
   - Signals the hypervisor that the Realm has halted, transitioning the Realm state machine to `SYSTEM_OFF`.

---
"""

module9_content = """# Module 9: Attestation Framework & Cryptographic Trust Chains

## 9.1 The Arm CCA Dual-Token Attestation Architecture

Cryptographic attestation is the cornerstone of confidential computing. Before a tenant provisions sensitive application code, proprietary neural network weights, or decryption keys into a Realm, the tenant must verify that the workload is executing on genuine Arm hardware in a verified security state.

Arm CCA defines an encapsulated **Dual-Token Attestation Model** rooted in the **PSA Certified Entity Attestation Token (EAT)** architecture (RFC 8392 / CBOR / COSE standards).

```mermaid
graph TD
    subgraph CCA_Token_Structure["Arm CCA Complete Attestation Token Structure (CBOR / COSE)"]
        direction TB
        
        subgraph Platform_Token["Platform Attestation Token (Signed by Platform RoT / PAK)"]
            P_ID["Implementation ID (Silicon Part & Stepping)"]
            P_LC["Platform Security Lifecycle State (Secured / Normal)"]
            P_CH["Hardware Challenge Nonce"]
            P_SW["Platform Firmware Hash & TCB Version (TF-A, RMM)"]
            P_SIG["Platform Signature: ECDSA / P-384 / ED25519"]
        end
        
        subgraph Realm_Token["Realm Attestation Token (Signed by RMM / RAK)"]
            R_CH["Tenant Challenge Nonce (Replay Prevention)"]
            R_RIM["Realm Initial Measurement (RIM) - Hash of initial code/data"]
            R_REM["Realm Extensible Measurements (REM[0..3]) - Runtime stages"]
            R_RPV["Realm Personalization Value (RPV) - Tenant metadata"]
            R_PUB["Realm Ephemeral Public Key (for Key Agreement)"]
            R_SIG["Realm Signature: ECDSA-P384"]
        end
        
        Platform_Token -->|"Cryptographically Bound"| Realm_Token
    end
    
    style CCA_Token_Structure fill:#fdfefe,stroke:#2c3e50,stroke-width:2px;
    style Platform_Token fill:#fcf3cf,stroke:#f39c12,stroke-width:2px;
    style Realm_Token fill:#d6eaf8,stroke:#2980b9,stroke-width:2px;
```

---

## 9.2 Token Formats & Cryptographic Claims

The CCA token is structured as a nested or tagged CBOR (Concise Binary Object Representation) document containing two distinct cryptographic scopes:

### 1. The Platform Attestation Token
Generated by the **Platform Hardware Root of Trust** (or Root EL3 Monitor) and signed with the **Platform Attestation Key (PAK)**:
- **`IMPLEMENTATION_ID`**: Identifies the silicon manufacturer, model, and silicon stepping.
- **`HARDWARE_VERSION`**: Hardware design revision and chip serial identifier.
- **`SECURITY_LIFECYCLE`**: Current lifecycle phase (e.g., `PSA_LIFECYCLE_SECURED`).
- **`BOOT_SEED`**: A cryptographically random value generated at system cold reset, uniquely identifying the current boot session.
- **`SOFTWARE_MEASUREMENTS`**: Array of cryptographic hashes measuring the platform firmware stages:
  - BL1 / BL2 Immutable Boot code.
  - BL31 Trusted Firmware-A (Monitor).
  - RMM image hash and version.

### 2. The Realm Attestation Token
Generated by the **Realm Management Monitor (TF-RMM)** and signed with an ephemeral **Realm Attestation Key (RAK)**:
- **`CHALLENGE`**: A 64-byte cryptographic nonce provided by the remote relying party to prevent replay attacks.
- **`RIM` (Realm Initial Measurement)**: SHA-256 or SHA-512 digest of all code, data, and Stage-2 page tables populated prior to `RMI_REALM_ACTIVATE`.
- **`REM` (Realm Extensible Measurements)**: Four 64-byte measurement registers (`REM[0]`, `REM[1]`, `REM[2]`, `REM[3]`) that record runtime software stages:
  - `REM[0]`: Hash of the EDK2 UEFI firmware image.
  - `REM[1]`: Hash of the Linux kernel image, command line parameters, and initramfs.
  - `REM[2]`: Hash of runtime application containers or workload configuration.
  - `REM[3]`: Reserved for dynamic tenant runtime measurements.
- **`RPV` (Realm Personalization Value)**: A 64-byte arbitrary value injected by the tenant during creation to bind the Realm to a specific tenant account or policy.
- **`HASH_ALGO_ID`**: Identifier for cryptographic hashing algorithm (`SHA-256` or `SHA-512`).

---

## 9.3 Cryptographic Key Hierarchy & Derivation

The security of the attestation model depends on an unbroken cryptographic key derivation tree anchored in immutable hardware silicon fuses:

```mermaid
graph TD
    subgraph Key_Hierarchy["Arm CCA Cryptographic Key Derivation Hierarchy"]
        direction TB
        HUK["Hardware Unique Key (HUK)<br/>[On-Chip OTP Fuses - Never leaves Silicon]"]
        
        subgraph Hardware_RoT["Platform Hardware Root of Trust Engine"]
            KDF_RoT["Hardware Key Derivation Function (HMAC-SHA256)"]
            PAK["Platform Attestation Key (PAK)<br/>(Asymmetric Private Key)"]
            PAK_Pub["Platform Public Key (PAK_Pub)"]
        end
        
        subgraph Factory_PKI["Silicon Manufacturer Public Key Infrastructure (PKI)"]
            Endorsement_Cert["Silicon Manufacturer Endorsement Certificate<br/>(Signs PAK_Pub with Manufacturer CA)"]
        end
        
        subgraph RMM_Layer["Realm Management Monitor (R-EL2)"]
            KDF_RMM["RMM Ephemeral Key Generator"]
            RAK["Realm Attestation Key (RAK)<br/>(Ephemeral Asymmetric Key per Realm)"]
            RAK_Pub["Realm Public Key (RAK_Pub)"]
        end
        
        HUK --> KDF_RoT
        KDF_RoT --> PAK
        PAK --> PAK_Pub
        PAK_Pub -.-> Endorsement_Cert
        
        PAK -->|"Signs RAK_Pub Binding Certificate"| RAK_Pub
        KDF_RMM --> RAK
        RAK --> RAK_Pub
    end
    
    style Key_Hierarchy fill:#f9f9f9,stroke:#34495e,stroke-width:2px;
    style Hardware_RoT fill:#fcf3cf,stroke:#f39c12,stroke-width:2px;
    style Factory_PKI fill:#eaf2f8,stroke:#2980b9,stroke-width:2px;
    style RMM_Layer fill:#d4efdf,stroke:#27ae60,stroke-width:2px;
```

### Key Derivation Flow
1. **Hardware Unique Key (HUK)**: Burned into write-locked OTP fuses during chip fabrication. Inaccessible to software; only readable by the on-chip crypto engine.
2. **Platform Attestation Key (PAK)**: Derived by the hardware crypto engine from the HUK and platform configuration parameters. The public counterpart (`PAK_Pub`) is certified by the silicon manufacturer's CA.
3. **Realm Attestation Key (RAK)**: Generated by the RMM when a Realm is created. The RMM derives the RAK using an ephemeral entropy pool, ensuring each Realm has a unique cryptographic identity.
4. **Binding Platform & Realm Scopes**: The Platform RoT signs the public key of the RAK or embeds a cryptographic digest of the RMM and RAK into the Platform Token, establishing an unbroken mathematical chain from the silicon manufacturer to the specific tenant Realm instance.

---

## 9.4 Complete Remote Attestation Protocol Flow

The end-to-end protocol workflow between the remote tenant verifier and the running Realm:

```mermaid
sequenceDiagram
    autonumber
    participant Tenant as Remote Tenant / Verifier
    participant Realm as Realm Guest OS (R-EL1)
    participant RMM as Realm Mgmt Monitor (R-EL2)
    participant RoT as Platform RoT / EL3
    participant ArmPKI as Silicon Manufacturer PKI

    Tenant->>Tenant: Generates 64-byte Cryptographic Nonce (Challenge)
    Tenant->>Realm: Transmits Nonce via TLS Connection
    Realm->>RMM: SMC RSI_ATTESTATION_TOKEN_INIT(Nonce, Buffer_PA)
    RMM->>RoT: Requests Platform Attestation Evidence
    RoT-->>RMM: Returns Signed Platform Token (PAK Signature)
    RMM->>RMM: Hashes RIM + REM[0..3] + RPV
    RMM->>RMM: Signs Realm Token using RAK
    RMM->>RMM: Packs Encapsulated Dual-Token (CBOR / COSE)
    RMM-->>Realm: Returns Complete Attestation Token
    Realm-->>Tenant: Transmits Token via TLS Connection
    
    Note over Tenant,ArmPKI: Verifier Evaluation Phase
    Tenant->>ArmPKI: Fetches Silicon Manufacturer Endorsement Certificate
    Tenant->>Tenant: Verifies PAK signature against Silicon CA
    Tenant->>Tenant: Verifies RAK signature against Platform Token
    Tenant->>Tenant: Asserts Platform Lifecycle == SECURED
    Tenant->>Tenant: Asserts Challenge Nonce matches transmitted Nonce
    Tenant->>Tenant: Compares RIM and REM measurements against golden references
    
    Note over Tenant,Realm: Secret Provisioning Phase
    Tenant->>Realm: Injects Decryption Keys & Proprietary Workload Payloads
```

---
"""

with open("arm-security/modules/module7.md", "w") as f:
    f.write(module7_content.strip() + "\n")

with open("arm-security/modules/module8.md", "w") as f:
    f.write(module8_content.strip() + "\n")

with open("arm-security/modules/module9.md", "w") as f:
    f.write(module9_content.strip() + "\n")

print("Generated Modules 7, 8, and 9 successfully.")
