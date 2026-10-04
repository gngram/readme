#!/usr/bin/env python3
"""
Generator for Modules 4 to 6 of the ARM Security Architecture Reference Guide.
"""

import os

os.makedirs("arm-security/modules", exist_ok=True)

module4_content = """# Module 4: System Hardware Infrastructure & Memory Protection

## 4.1 Processing Element (PE) Architecture & Granule Data Isolation (GDI)

The Armv9-A architecture with Realm Management Extension (RME) introduces critical microarchitectural enhancements to the Processing Element (PE) pipeline to guarantee strict temporal and spatial isolation across security states.

### Microarchitectural Flushes & State Sanitization
Whenever a physical PE transitions between security states (e.g., executing a world switch at Root EL3), hardware and firmware cooperate to enforce complete state isolation:
- **General-Purpose and Vector Registers**: Saved and restored by the EL3 monitor or RMM. Vector registers (Neon, SVE2, SME) and FPCR/FPSR are zeroized or context-switched to eliminate microarchitectural data remanence.
- **Translation Lookaside Buffers (TLBs)**: Every TLB entry is tagged with its originating Translation Regime and PAS. A Non-Secure translation lookup can never match a TLB entry tagged with Realm PAS.
- **Branch Target Buffers (BTBs) & Speculative Execution Barriers**: RME requires hardware protection against speculative cross-world side-channel attacks (e.g., Spectre-v2, Branch Target Injection). Architectural barrier instructions (`CSDB`, `ESB`, `SB`) and hardware speculation barriers (`FEAT_CSV2`, `FEAT_CSV3`) prevent malicious hypervisors from training branch predictors to steer speculative execution in Realms.

### Granule Data Isolation (GDI)
As defined in the *RME System Architecture* (ARM-DEN-0129), **Granule Data Isolation (GDI)** is a system-level property ensuring that data belonging to a physical granule assigned to one PAS is never exposed to another PAS through transient storage:
1. **Cache Tagging**: Internal L1, L2, and system-level caches (SLC) track the PAS attribute alongside physical cache line address tags. Even if two processes in different security states issue an access to identical physical address offsets, the cache tag comparison checks:
   $$\\text{Cache Hit} \\iff (\\text{PA} == \\text{Tag.PA}) \\land (\\text{Transaction.PAS} == \\text{Tag.PAS})$$
2. **Eviction and Line-Fill Scrubbing**: When a cache line is evicted or invalidated, its data cannot be speculatively snooped across security boundaries.

```
L1 / L2 / L3 Cache Line Tag Format in RME:
+---------------------------------------------------------------------------------+
| Physical Tag [PA_WIDTH-1 : 6] | PAS Tag [1:0] | MECID [15:0] | State / Dirty Bit|
+---------------------------------------------------------------------------------+
|                                Cache Data (64 Bytes)                            |
+---------------------------------------------------------------------------------+
```

---

## 4.2 Main Memory Protection Engine (MPE) & DRAM Encryption

While Granule Protection Checks prevent unauthorized on-chip access, external DRAM chips and inter-die memory buses remain vulnerable to physical tampering, cold-boot attacks, and passive bus interposers.

To eliminate physical attacks, RME platforms integrate a hardware **Memory Protection Engine (MPE)** into the DRAM memory controller pipeline.

```mermaid
graph LR
    subgraph MPE_Pipeline["Memory Protection Engine (MPE) Pipeline"]
        Core["Core / Interconnect<br/>(Plaintext Data + PAS + MECID)"] --> Cipher["MPE Cipher Core<br/>• AES-XTS / AES-GCM (128/256-bit)<br/>• Physical Address Tweak<br/>• Keystream Generation"]
        
        KeyEngine["Key Derivation Engine<br/>• Hardware Root Key<br/>• MECID Key Table"] --> Cipher
        
        Cipher --> EncryptedData["Encrypted Ciphertext Block"]
        Cipher --> Integrity["Integrity Tree Engine<br/>• HMAC / Poly1305 MAC<br/>• Merkle Tree Replay Filter"]
        
        EncryptedData --> DRAM[("External DRAM Modules")]
        Integrity --> DRAM
    end
    
    style MPE_Pipeline fill:#f4f6f7,stroke:#34495e,stroke-width:2px;
    style Cipher fill:#ebf5fb,stroke:#2980b9,stroke-width:2px;
    style KeyEngine fill:#fef9e7,stroke:#f39c12,stroke-width:2px;
```

### Cryptographic Primitives & Modes
The MPE operates at memory line speed (typically 64-byte bursts corresponding to cache lines):
1. **Confidentiality (Encryption)**:
   - Utilizes standard block ciphers such as **AES-XTS-128**, **AES-XTS-256**, or low-latency tweakable ciphers (e.g., Prince or QARMA-based ciphers).
   - The encryption key is dynamically combined with a physical address tweak, ensuring that identical 64-byte plaintext patterns written to different physical memory locations produce completely distinct ciphertexts (defeating pattern-recognition attacks).
2. **Integrity & Replay Protection**:
   - To defeat active physical tampering (e.g., bit-flipping or splicing attacks), the MPE generates a Message Authentication Code (MAC) for each 64-byte line.
   - To mitigate replay attacks (where an attacker records a valid ciphertext block and writes it back at a later time), the MPE maintains an on-chip **integrity tree (Merkle Tree)** with monotonic version counters rooted in on-chip SRAM.

---

## 4.3 Memory Encryption Contexts (MEC) & MECIDs

In cloud multi-tenant systems, thousands of confidential virtual machines may execute concurrently. If all Realms share a single global encryption key, a physical bus attack or microarchitectural bug in the memory controller could theoretically compromise multi-tenant isolation.

The **Memory Encryption Contexts (MEC)** extension introduces fine-grained, per-Realm cryptographic keys for main memory.

```mermaid
graph TD
    subgraph MEC_Architecture["Memory Encryption Contexts (MEC) Architecture"]
        direction TB
        subgraph Tenants["Independent Tenant Realms"]
            R1["Realm VM 1 (MECID = 0x0001)"]
            R2["Realm VM 2 (MECID = 0x0002)"]
            R3["Realm VM 3 (MECID = 0x0003)"]
        end
        
        subgraph Interconnect["Mesh Interconnect Fabric (CMN-700)"]
            Bus["AMBA Packet: [Address] + [PAS = Realm] + [MECID]"]
        end
        
        subgraph MPE_Unit["Memory Protection Engine (MPE)"]
            LUT["Key Lookup Table (Protected SRAM)<br/>MECID 0x0001 -> Key K_R1<br/>MECID 0x0002 -> Key K_R2<br/>MECID 0x0003 -> Key K_R3"]
            Crypto["Inline Cipher Engine"]
        end
        
        DRAM[("Physical DRAM")]
        
        R1 -->|Emits MECID 0x0001| Bus
        R2 -->|Emits MECID 0x0002| Bus
        R3 -->|Emits MECID 0x0003| Bus
        Bus --> LUT
        LUT --> Crypto
        Crypto --> DRAM
    end
    
    style Tenants fill:#eaf2f8,stroke:#2980b9,stroke-width:2px;
    style Interconnect fill:#fef9e7,stroke:#f1c40f,stroke-width:2px;
    style MPE_Unit fill:#e8f8f5,stroke:#27ae60,stroke-width:2px;
```

### MEC Mechanics & Allocation
- **MECID (Memory Encryption Context Identifier)**: A 16-bit identifier allocated by the RMM to each active Realm.
- **PAS and MECID Interaction**: While the GPC verifies that the transaction targets Realm PAS, the MPE checks the MECID:
  - If a transaction arrives at the memory controller with `PAS = Realm` and `MECID = 0x0002`, the MPE retrieves Key $K_{\\text{R2}}$ from its internal secure key store to decrypt the cache line.
  - If an attacker or hypervisor attempts to read Realm 2's memory using Realm 1's context or a Non-Secure context, the MPE uses the incorrect key, resulting in cryptographically scrambled garbage and an immediate integrity check failure.
- **MECID Mismatch Faults**: Any discrepancy between the MECID encoded in the transaction and the assigned granule configuration triggers a synchronous abort or system error report.

---

## 4.4 System Control Processor (SCP) & Trusted Subsystems

Enterprise SoCs incorporate autonomous microcontrollers for power, thermal, clock, and system lifecycle management:
- **System Control Processor (SCP)** / Manageability Subsystem.
- **Baseboard Management Controller (BMC)**.

### Architectural Threat
Because these microcontrollers often have direct bus master access to the system fabric to orchestrate dynamic frequency scaling (DVFS) and power states, a compromised SCP could potentially issue DMA reads into Realm or Root memory.

### RME Requirements for Subsystems (ARM-DEN-0129)
1. **Isolated & Shielded Locations**:
   - Firmware for the SCP must execute from dedicated ROM or private on-chip SRAM that is physically inaccessible to the main Application PEs.
2. **SCP Transaction Filtering**:
   - The interconnect must subject all SCP-initiated bus transactions to Granule Protection Checks. 
   - Under standard runtime states, the SCP is treated as an untrusted or strictly non-secure bus master: it is prohibited from initiating transactions targeting Root, Secure, or Realm PAS.
3. **Power Transitions & State Zeroization**:
   - When a core or cluster is placed into a low-power retention or power-down state (e.g., via PSCI), any hardware state registers saving Realm or Root context must be wiped before power rails collapse, or saved into Root-shielded SRAM.

---

## 4.5 Multi-Chip Interconnects & Link Protection

High-end server platforms deploy multi-socket configurations where multiple physical SoCs communicate over high-speed coherent inter-chip links (e.g., Arm CCIX or CXL across PCIe physical layers).

```mermaid
graph LR
    subgraph Socket0["SoC Socket 0"]
        Core0["PE Core Cluster"]
        CMN0["Coherent Mesh Interconnect"]
        MPE0["Memory Protection Engine"]
        Core0 <--> CMN0 <--> MPE0
    end
    
    subgraph InterChip_Link["Secure Multi-Chip Physical Link"]
        PHY_Link["Encrypted Coherent Link (PCIe / CXL / Proprietary)<br/>• Line-Rate AES-GCM Encryption<br/>• PAS and MECID Propagation<br/>• Replay Counter Verification"]
    end
    
    subgraph Socket1["SoC Socket 1"]
        CMN1["Coherent Mesh Interconnect"]
        MPE1["Memory Protection Engine"]
        Core1["PE Core Cluster"]
        MPE1 <--> CMN1 <--> Core1
    end
    
    CMN0 <===> PHY_Link <===> CMN1
    
    style Socket0 fill:#eaf2f8,stroke:#2980b9,stroke-width:2px;
    style Socket1 fill:#eaf2f8,stroke:#2980b9,stroke-width:2px;
    style InterChip_Link fill:#fef9e7,stroke:#e67e22,stroke-width:2px;
```

### Multi-Chip RME Requirements
1. **Link Encryption & Integrity**:
   - Inter-chip links carry cache coherency snoop requests, data transfers, and memory read/writes across physical printed circuit board (PCB) traces.
   - As mandated by ARM-DEN-0129 Chapter B8, multi-chip links must implement hardware-level authenticated encryption (e.g., MACsec or PCIe IDE) to protect transactions traversing external board traces against physical interposers.
2. **PAS Preservation Across Sockets**:
   - The coherent interconnect protocol must serialize the 2-bit PAS tag and the MECID into the packet headers across the physical link.
   - Sockets must establish a mutually verified cryptographic trust domain at system boot before permitting coherent Realm transactions to traverse the inter-chip fabric.

---

## 4.6 CXL.mem Integration & CXL-TSP

The advent of **Compute Express Link (CXL)** allows servers to expand physical memory via memory devices connected over PCIe physical layers (CXL.mem protocol).

### Challenges with External CXL Memory
Unlike on-package DRAM controllers, CXL memory modules reside across external PCIe slots and may contain independent controllers, making them vulnerable to device substitution and bus snooping.

### CXL-TSP (Trusted Security Protocol)
To support CXL memory in an RME architecture:
- The host memory controller and the CXL endpoint negotiate **CXL-TSP** session keys during platform boot.
- The SoC memory controller treats the CXL link as a secure cryptographically encapsulated tunnel.
- Transactions emitted to CXL memory maintain explicit PAS classification and per-granule integrity tags, ensuring that Realm memory hosted on CXL expanders retains identical security guarantees to local DRAM.

---
"""

module5_content = """# Module 5: System MMU (SMMUv3.2/3.3) & Device Assignment (RME-DA & RME-CDA)

## 5.1 System MMU Role in an RME-Enabled Platform

In complex computing systems, peripheral devices (e.g., Network Interface Cards, NVMe SSD controllers, GPUs, and hardware accelerators) utilize Direct Memory Access (DMA) to read and write system memory directly. 

Without hardware protection, a malicious peripheral or a compromised hypervisor configuring DMA descriptors could issue memory transactions targeting Realm private memory, bypassing core CPU MMUs entirely.

To prevent DMA-based compromise and to enable direct, confidential hardware acceleration, the **Arm System Memory Management Unit (SMMUv3.2 and SMMUv3.3)** incorporates architectural extensions for RME:
1. **PAS-Aware Stream Translation**: Every DMA transaction emitted by an endpoint device is assigned a **StreamID**. The SMMU maps the StreamID to a security domain and translation context.
2. **Granule Protection Check (GPC) Integration**: The SMMU incorporates an internal GPC pipeline and GPC TLB, validating that physical addresses generated by DMA translation do not violate Granule Protection Tables before emitting transactions to the system interconnect.

```mermaid
graph TD
    subgraph SMMU_Architecture["SMMUv3 RME Pipeline with Granule Protection Checks"]
        direction TB
        Device["PCIe Endpoint Device / DMA Controller<br/>(Emits StreamID + Virtual Address)"]
        
        subgraph SMMU_Core["SMMUv3.2 / SMMUv3.3 Core"]
            STE["Stream Table Entry (STE)<br/>• StreamWorld: Non-Secure / Secure / Realm / Root<br/>• Stage-1 Context Bank<br/>• Stage-2 Translation Base"]
            
            S1_Trans["Stage-1 Translation (VA -> IPA)"]
            S2_Trans["Stage-2 Translation (IPA -> PA + Desired PAS)"]
            
            subgraph SMMU_GPC["SMMU Granule Protection Checker"]
                SMMU_GPC_TLB["SMMU GPC TLB Cache"]
                SMMU_GPC_Logic["PAS Verification Logic"]
            end
        end
        
        Device --> STE
        STE --> S1_Trans --> S2_Trans --> SMMU_GPC
        SMMU_GPC_TLB -.-> SMMU_GPC_Logic
        
        SMMU_GPC -->|Pass: Authorized PAS| CMN["System Interconnect (Tagged with PAS)"]
        SMMU_GPC -->|Fail: Misrouted DMA| SMMU_Fault["GPC Fault Interrupt (Routed to Root EL3)"]
    end
    
    style SMMU_Architecture fill:#f9f9f9,stroke:#34495e,stroke-width:2px;
    style SMMU_Core fill:#ebf5fb,stroke:#2980b9,stroke-width:2px;
    style SMMU_GPC fill:#e8f8f5,stroke:#27ae60,stroke-width:2px;
    style SMMU_Fault fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
```

---

## 5.2 StreamWorld Configurations & Stream Security

The SMMU configuration structure is rooted in the **Stream Table**, indexed by the peripheral's `StreamID`. Each Stream Table Entry (STE) contains the **`STRW` (StreamWorld)** configuration:

| `STRW` Field | Associated Security Domain | Output Permitted PAS | Description |
| :---: | :---: | :---: | :--- |
| `0b00` | **Non-Secure (NS)** | Non-Secure PAS Only | Standard PCIe devices (legacy NICs, NVMe disks). Cannot target Realm memory. |
| `0b01` | **Secure** | Secure & Non-Secure PAS | Secure World peripherals (e.g., Hardware Security Modules, TPMs). |
| `0b10` | **Realm** | Realm & Non-Secure PAS | Devices assigned directly to a Realm (Confidential Accelerators, Realm vNICs). |
| `0b11` | **Root** | All PAS (Root, Realm, Secure, NS) | Highly privileged platform controllers. |

---

## 5.3 The Address Translation Services (ATS) Security Dilemma & DPT

High-performance PCIe devices utilize **Address Translation Services (ATS)**. Under ATS, rather than the SMMU translating every single DMA read/write transaction:
1. The device issues an ATS translation request to the SMMU.
2. The SMMU translates the address and returns the translated physical address to the device.
3. The device caches the translation in its internal **Address Translation Cache (ATC)** and subsequently issues DMA requests using physical addresses directly.

### The ATS Vulnerability in Confidential Computing
In a confidential compute environment, ATS creates an unacceptable security flaw:
> *A physical PCIe endpoint is outside the processor chip package. An attacker can compromise the device firmware or tap the PCIe bus, manipulating the device's internal ATC to emit arbitrary physical addresses into Realm memory, bypassing the SMMU.*

```mermaid
graph TD
    subgraph ATS_Vulnerability_DPT["ATS Dilemma & Device Protection Table (DPT) Mitigation"]
        direction TB
        subgraph Compromised_Device["Untrusted / Compromised PCIe Device"]
            ATC["Peripheral ATC (Device TLB)<br/>[Attacker overrides cached PA to point to Realm RAM]"]
        end
        
        subgraph SMMU_Validation["SMMUv3.3 with Device Protection Table (DPT)"]
            ATS_Req["Direct DMA Write (Target PA)"]
            DPT_Engine["DPT Validator Engine<br/>• Walks Root/Realm DPT<br/>• Verifies PA was genuinely granted to this StreamID"]
        end
        
        Compromised_Device -->|Emits DMA with Raw PA| ATS_Req
        ATS_Req --> DPT_Engine
        DPT_Engine -->|Mismatch: Device lied about translation| Abort["Transaction Aborted + GPC Alert"]
        DPT_Engine -->|Match: Valid authorized mapping| DRAM["DRAM Access Granted"]
    end
    
    style Compromised_Device fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
    style SMMU_Validation fill:#e8f8f5,stroke:#27ae60,stroke-width:2px;
    style Abort fill:#f5b7b1,stroke:#c0392b,stroke-width:2px;
```

### The Solution: Device Protection Table (DPT)
To allow the performance benefits of ATS without compromising Realm security, Arm SMMUv3.3 introduces the **Device Protection Table (DPT)**:
- Even when full ATS is enabled, all memory transactions emitted by the device must pass through an ultra-fast hardware **DPT check** at the PCIe Root Port or SMMU.
- The DPT acts as an independent hardware firewall recording which specific physical address ranges have been legally mapped to each peripheral device.
- If a device attempts a DMA transaction using an address that does not match an active entry in the DPT for its StreamID, the transaction is dropped immediately and logged as a DPT violation.

---

## 5.4 RME Device Assignment (RME-DA) & PCIe IDE

To enable confidential cloud workloads to utilize specialized accelerators (such as GPUs for private AI inference, tensor processing units, or high-speed SmartNICs) without exposing data to the hypervisor, Arm defines **RME Device Assignment (RME-DA)** and **RME Coherent Device Assignment (RME-CDA)**.

### The Three-Layer Device Assignment Stack
Securing an external PCIe peripheral in Arm CCA requires three coordinated protocols:

```mermaid
graph TD
    subgraph Device_Assignment_Stack["RME Device Assignment Security Hierarchy"]
        direction TB
        L3["Layer 3: TDISP (Trusted Device Interface Security Protocol)<br/>• Standardized configuration & interface state machine<br/>• Arm Vendor-Defined Messages (VDMs)"]
        L2["Layer 2: PCIe IDE (Integrity and Data Encryption)<br/>• Hardware line-rate AES-GCM encryption on physical PCIe lanes<br/>• Prevents PCIe physical interposers and bus sniffers"]
        L1["Layer 1: SPDM (Security Protocol and Data Model)<br/>• Mutual authentication between SoC Root of Trust and Device RoT<br/>• Device certificate verification & measurement attestation"]
        
        L1 --> L2 --> L3
    end
    
    style L3 fill:#d6eaf8,stroke:#2980b9,stroke-width:2px;
    style L2 fill:#ebf5fb,stroke:#3498db,stroke-width:2px;
    style L1 fill:#fcf3cf,stroke:#f39c12,stroke-width:2px;
```

1. **SPDM (Security Protocol and Data Model - DMTF standard)**:
   - Before an accelerator is assigned to a Realm, the platform Root of Trust and the RMM communicate with the device's embedded micro-controller.
   - The device presents its X.509 certificate chain rooted in the device manufacturer's CA.
   - The RMM requests cryptographic measurements of the device's internal firmware.
2. **PCIe IDE (Integrity and Data Encryption - PCI-SIG standard)**:
   - Establishes point-to-point cryptographic encryption between the host PCIe Root Complex and the endpoint device controller.
   - Every Transaction Layer Packet (TLP) is encrypted with AES-GCM and stamped with a 96-bit cryptographic MAC, protecting all PCIe traffic against physical interposers.
3. **TDISP (Trusted Device Interface Security Protocol)**:
   - Standardizes the interface states: `CONFIG_LOCKED`, `UNLOCKED`, `LOCKED`, and `RUN`.
   - The Host Hypervisor coordinates device setup, but cannot enter the `RUN` state or manipulate device DMA registers without cryptographic authorization from the RMM.

### Arm Vendor-Defined Messages (VDMs) for TDISP
As specified in **ARM-DEN-0129 Appendix 2**, Arm CCA extends standard TDISP messaging using PCIe Vendor-Defined Messages (VDMs) with Arm's Vendor ID:
- `GET_VERSION_REQ` / `GET_VERSION_RESP`: Negotiates Arm RME-DA protocol capabilities.
- `SET_INTERFACE_REQ` / `SET_INTERFACE_RESP`: Binds a specific physical or virtual function (SR-IOV VF) to a target Realm.
- `GET_DEV_PROP_REQ` / `GET_DEV_PROP_RESP`: Retrieves device hardware properties, memory limits, and GPC compliance flags.

---
"""

module6_content = """# Module 6: Arm CCA Software Architecture & Firmware Stack

## 6.1 Complete Software Topology & Trust Hierarchy

The Arm Confidential Compute Architecture software stack coordinates firmware, hypervisor, and guest environments across all four security states.

```mermaid
graph TD
    subgraph Arm_CCA_Software_Topology["Arm CCA Software Stack & Execution Domains"]
        direction TB
        
        subgraph Root_Domain["Root State (EL3) - Platform RoT"]
            TFA["Trusted Firmware-A (TF-A)<br/>• EL3 Exception Handling<br/>• RMM Dispatcher (RMMD)<br/>• Granule Protection Table Management"]
        end
        
        subgraph Realm_Domain["Realm State - Confidential Execution"]
            subgraph R_EL2_Domain["Realm EL2"]
                RMM["Realm Management Monitor (TF-RMM)<br/>• Stage-2 Realm Translation (RTT)<br/>• Realm Contexts (REC)<br/>• RSI Handler & Attestation Token Issuer"]
            end
            subgraph R_EL1_0_Domain["Realm EL1 & EL0"]
                RealmKernel["Realm Guest Linux Kernel<br/>(CCA Enlightened)"]
                EDK2["EDK2 / OVMF Firmware"]
                RealmApps["Tenant User Applications"]
                EDK2 --> RealmKernel --> RealmApps
            end
            RMM --> R_EL1_0_Domain
        end
        
        subgraph NonSecure_Domain["Non-Secure State - Untrusted Infrastructure"]
            KVM["Host Hypervisor (Linux KVM / Xen)<br/>• Resource Allocation<br/>• vCPU Scheduling<br/>• Non-Secure Stage-2 MMU"]
            KVMTool["Host VMM / Orchestrator (kvmtool / QEMU)"]
            KVMTool --> KVM
        end
        
        subgraph Secure_Domain["Secure State - TrustZone Services"]
            SPM["Secure Partition Manager (SPMC)"]
            OPTEE["Trusted OS (OP-TEE)"]
            SPM --> OPTEE
        end
        
        NonSecure_Domain -- "RMI Commands (SMC)" --> TFA
        TFA -- "RMMD Dispatches RMI" --> R_EL2_Domain
        R_EL1_0_Domain -- "RSI Requests (SMC)" --> R_EL2_Domain
        R_EL2_Domain -- "GPT Transition (SMC)" --> TFA
    end
    
    style Root_Domain fill:#fcf3cf,stroke:#b7950b,stroke-width:2px;
    style Realm_Domain fill:#d6eaf8,stroke:#2980b9,stroke-width:2px;
    style NonSecure_Domain fill:#fadbd8,stroke:#c0392b,stroke-width:2px;
    style Secure_Domain fill:#d4efdf,stroke:#27ae60,stroke-width:2px;
```

---

## 6.2 EL3 Firmware: Monitor & RMM Dispatcher (RMMD)

Exception Level 3 (`EL3`) is the architectural bedrock of the platform. Executing in **Root State**, the EL3 firmware (implemented in open-source **Trusted Firmware-A / TF-A**) has complete physical access to the machine.

### Core Responsibilities of TF-A in Arm CCA
1. **Cold Boot & Platform Initialization**:
   - Executes the early boot stages (`BL1`, `BL2`, `BL31`).
   - Configures `GPCCR_EL3` and `GPTBR_EL3`, building the initial Level 0 and Level 1 Granule Protection Tables in Root PAS memory.
   - Disables all invasive debug interfaces for Realm and Root spaces unless hardware cryptographic debug authentication is satisfied.
2. **RMM Dispatcher (RMMD)**:
   - Resides inside TF-A as a privileged dispatch service.
   - When the Host Hypervisor issues a Secure Monitor Call (`SMC`) containing an **RMI function ID**, the processor traps to EL3.
   - The RMMD validates the SMC parameters, performs a context switch from Non-Secure state to Realm state, and executes an `ERET` to enter the Realm Management Monitor at `R-EL2`.
   - Conversely, when the RMM completes an operation or needs to return control to the host, the RMMD switches context back and returns execution to `NS-EL2`.
3. **GPT Dynamic Transition Service**:
   - Serves privileged SMC calls from the RMM to transition granules between `Non-Secure` and `Realm` PAS.
   - Executes the required hardware cache clean/invalidation (`DC CIPAPA`) and TLB invalidation (`TLBI RPASALLOS`) before committing GPT entry changes.

---

## 6.3 Realm Management Monitor (TF-RMM) at R-EL2

The **Realm Management Monitor (RMM)** is a purpose-built, highly optimized, trusted firmware layer executing at **Realm EL2 (`R-EL2`)**. 

The reference implementation, **TF-RMM**, is developed under the open governance of TrustedFirmware.org.

### Architectural Mandates of the RMM
1. **Zero Policy, Pure Mechanism**:
   - The RMM does **not** contain an operating system scheduler, virtual disk driver, or complex device emulator.
   - It acts purely as a deterministic hardware-isolation gatekeeper. Scheduling decisions remain strictly with the host hypervisor.
2. **Deterministic Memory Footprint**:
   - The RMM uses a static, pre-allocated memory model. It does not use dynamic runtime heap allocations (`malloc`), eliminating a massive class of memory corruption and heap fragmentation vulnerabilities.
3. **Execution Context Management**:
   - Allocates and maintains **Realm Execution Contexts (RECs)**.
   - When the host hypervisor decides to run a Realm vCPU, it invokes `RMI_REC_ENTER`. The RMM sanitizes the CPU registers, loads the Realm vCPU state, configures Realm Stage-2 translation, and enters Realm EL1/EL0.
4. **Attestation Token Generation**:
   - Manages the cryptographic measurement engine for Realms.
   - Serves requests from the Realm guest via the Realm Services Interface (RSI) to produce cryptographically signed attestation tokens.

---

## 6.4 Host Hypervisor (KVM / kvmtool / QEMU) at NS-EL2

In traditional virtualization, Linux KVM owns both resource allocation and execution privileges. In Arm CCA, KVM is adapted to operate as an **Untrusted Resource Manager**.

### KVM Architectural Adaptations for CCA
1. **Realm VM Lifecycle Management**:
   - KVM exposes standard `/dev/kvm` ioctl interfaces to userspace VMMs (such as `kvmtool` or QEMU):
     - `KVM_CREATE_VM` (flagged with `KVM_VM_TYPE_ARM_REALM`)
     - `KVM_ARM_REALM_CREATE_RD` (allocates Realm Descriptor)
     - `KVM_ARM_REALM_INIT_IPA_REALM` (populates initial guest image)
     - `KVM_ARM_REALM_ACTIVATE` (locks initial measurements and transitions Realm to Active)
2. **Unshared Memory Management**:
   - Standard KVM virtual machines have their guest physical memory mapped directly into the host process's virtual address space, allowing QEMU to inspect guest memory.
   - For Realms, KVM allocates normal host memory pages, but then issues `RMI_DATA_CREATE` SMCs to hand the pages over to the RMM. The hardware GPC immediately converts the granules to Realm PAS, revoking KVM's read and write permissions.
3. **Fault & Exit Handling**:
   - When a Realm triggers an exit (e.g., an MMIO access to an emulated virtio device, a timer interrupt, or a PSCI power call), the hardware exits to R-EL2.
   - The RMM sanitizes the exit state: general-purpose register contents are scrubbed, and only a minimal exit reason structure is returned to KVM at `NS-EL2`.

---

## 6.5 Realm Guest Environment: Linux & EDK2

Software running inside a Realm executes at **Realm EL1** (Operating System Kernel) and **Realm EL0** (User Applications).

### Realm Enlightenment
An operating system executing inside a Realm does not require radical architectural redesign, but it does require **CCA Enlightenment**:
1. **Shared vs. Private Memory Classification**:
   - Real-world virtual machines must communicate with host-emulated devices (e.g., virtio-net, virtio-blk). Because the host hypervisor cannot read Realm PAS memory, DMA buffers used for virtio communication must reside in **Non-Secure PAS**.
   - The enlightened Linux kernel implements a bouncing buffer mechanism (such as the Linux `swiotlb` / Software I/O TLB framework). When the guest driver prepares a network packet for transmission, it copies the data from private Realm memory to an explicit shared Non-Secure memory pool.
   - The guest dynamically requests the RMM to mark specific address ranges as Non-Secure using the **Realm Services Interface (`RSI_IPA_STATE_SET`)**.
2. **EDK2 / OVMF UEFI Firmware for Realms**:
   - Open-source EDK2 provides the standard UEFI boot environment inside the Realm.
   - EDK2 initializes the virtual platform, discovers virtual ACPI tables populated by the host, measures the UEFI boot environment into the Realm's runtime attestation registers, and boots the guest Linux kernel.

---
"""

with open("arm-security/modules/module4.md", "w") as f:
    f.write(module4_content.strip() + "\n")

with open("arm-security/modules/module5.md", "w") as f:
    f.write(module5_content.strip() + "\n")

with open("arm-security/modules/module6.md", "w") as f:
    f.write(module6_content.strip() + "\n")

print("Generated Modules 4, 5, and 6 successfully.")
