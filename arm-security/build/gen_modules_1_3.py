#!/usr/bin/env python3
"""
Generator for Modules 1 to 3 of the ARM Security Architecture Reference Guide.
"""

import os

os.makedirs("arm-security/modules", exist_ok=True)

module1_content = """# Module 1: Introduction & The Confidential Computing Paradigm Shift

## 1.1 The Evolution of Compute Isolation & Security Dilemma

Modern computing platforms have historically relied on a hierarchical privilege ring model. In standard multi-tenant computing environments—such as infrastructure-as-a-service (IaaS) public clouds, software-as-a-service (SaaS) hosting, and enterprise multi-workload virtualization—security enforcement is predicated on privilege asymmetry:
- Applications at Exception Level 0 (`EL0`) are governed and constrained by the operating system kernel at Exception Level 1 (`EL1`).
- Operating system kernels are managed, scheduled, and multiplexed by the hypervisor / Virtual Machine Monitor (VMM) running at Exception Level 2 (`EL2`).
- The entire platform initialization, power orchestration, and root-of-trust runtime dispatch are governed by Secure Monitor firmware executing at Exception Level 3 (`EL3`).

While this hierarchical model ensures that higher exception levels can enforce security policies over lower exception levels, it introduces a fundamental architectural liability known as the **Hypervisor Privilege Paradox**:
> *Whoever possesses the privilege to allocate, manage, and schedule resources for a workload inherently possesses the architectural privilege to inspect, manipulate, tamper with, and exfiltrate that workload's code and execution state.*

```mermaid
graph TD
    subgraph Traditional_Privilege_Model["Traditional Privilege Hierarchy (Hierarchical Trust)"]
        direction TB
        EL3["EL3: Secure Monitor / Firmware<br/>(Full Architectural Supremacy)"]
        EL2["EL2: Hypervisor / Host OS (KVM, Xen, ESXi)<br/>(Complete Visibility into all VMs)"]
        EL1_VM1["EL1: Tenant VM 1 Kernel"]
        EL0_VM1["EL0: Tenant VM 1 Apps"]
        EL1_VM2["EL1: Tenant VM 2 Kernel"]
        EL0_VM2["EL0: Tenant VM 2 Apps"]
        
        EL3 --> EL2
        EL2 --> EL1_VM1
        EL2 --> EL1_VM2
        EL1_VM1 --> EL0_VM1
        EL1_VM2 --> EL0_VM2
    end
    
    style EL2 fill:#f96,stroke:#333,stroke-width:2px;
    style Traditional_Privilege_Model fill:#fdf2e9,stroke:#e67e22,stroke-width:2px;
```

In this classical design, the hypervisor's Trusted Computing Base (TCB) encompasses millions of lines of code across device emulators (e.g., QEMU), network device virtualization stacks (vhost-net, DPDK), complex physical memory allocators, virtual interrupt routing engines, and storage stacks. A security breach at any point within this vast hypervisor footprint compromises all hosted guest operating systems and their workloads simultaneously.

Furthermore, cloud tenants face threats beyond malicious software exploits:
1. **Rogue Administrative Access**: Cloud infrastructure administrators and service engineers with root privileges on bare-metal host systems can introspect guest physical memory via `/dev/mem`, read CPU register dumps, or attach debug monitors to virtual machines.
2. **Cold Boot & Physical Memory Probing**: Attackers with physical access to data center server hardware can attach interposers to DRAM memory buses, tap memory traces, perform rowhammer attacks, or conduct liquid nitrogen cold-boot memory dumps to extract plaintext cryptographic keys.
3. **Firmware & Management Engine Compromise**: Malicious Baseboard Management Controllers (BMCs), compromised Peripheral Component Interconnect Express (PCIe) peripheral firmware, or direct memory access (DMA) devices can bypass software-based OS memory mappings.

---

## 1.2 Limitations of Arm TrustZone for Cloud Multi-Tenancy

Prior to Armv9-A, Arm architecture provided the **Arm TrustZone** technology (introduced in Armv6KZ and expanded in Armv7-A and Armv8-A). TrustZone divides the processor execution environment into two strictly isolated hardware-enforced domains:
- **Normal World (Non-Secure State)**: Hosts the traditional operating system (Linux, Android, Windows) and applications, running across `EL0`, `EL1`, and `EL2`.
- **Secure World (Secure State)**: Hosts a Trusted OS (such as OP-TEE or proprietary vendor TEEs) and Trusted Applications (TAs), executing across `S-EL0`, `S-EL1`, and optionally `S-EL2`.

```mermaid
graph LR
    subgraph TrustZone_Architecture["Arm TrustZone (Dual-World Model)"]
        direction TB
        subgraph Normal_World["Normal World (Non-Secure)"]
            NS_EL2["Host Hypervisor (KVM / Xen)"]
            NS_EL1["Guest VM / OS Kernel"]
            NS_EL0["User Applications"]
            NS_EL2 --> NS_EL1 --> NS_EL0
        end
        
        subgraph Secure_Monitor["Root / Monitor"]
            EL3["EL3 Secure Monitor (TF-A)"]
        end
        
        subgraph Secure_World["Secure World"]
            S_EL2["Secure Partition Manager (SPMD/SPMC)"]
            S_EL1["Trusted OS (OP-TEE, Hafnium)"]
            S_EL0["Trusted Applications (TAs)"]
            S_EL2 --> S_EL1 --> S_EL0
        end
        
        NS_EL2 -- "SMC Call" --> EL3
        S_EL2 -- "ERET / Return" --> EL3
    end
    
    style Normal_World fill:#eaf2f8,stroke:#2980b9,stroke-width:2px;
    style Secure_World fill:#e8f8f5,stroke:#27ae60,stroke-width:2px;
    style Secure_Monitor fill:#fcf3cf,stroke:#f39c12,stroke-width:2px;
```

While TrustZone is exceptionally successful for mobile devices, embedded systems, and automotive security (for services such as DRM keystores, fingerprint biometric authentication, Apple Pay/Google Wallet enclave tokens, and secure payment processing), it possesses architectural characteristics that make it fundamentally unsuitable for general-purpose multi-tenant cloud virtualization:

| Architectural Property | Arm TrustZone (Secure World) | Multi-Tenant Cloud Virtualization Requirement |
| :--- | :--- | :--- |
| **Trust Model** | Monolithic OEM/Silicon Provider Trust. The silicon vendor and OEM control the Secure World root keys and sign all Trusted Applications. | Mutually distrusting third-party tenants who must trust neither the silicon vendor, the cloud host, nor each other. |
| **Concurrency & Scalability** | Designed for a small number of static, cooperative Trusted Services with limited memory footprints. | Highly dynamic creation, execution, and destruction of hundreds of arbitrary virtual machines with gigabytes or terabytes of RAM. |
| **Programming Paradigm** | Specialized microkernel APIs (GlobalPlatform TEE specifications) requiring refactoring applications into client-server TA models. | Unmodified, off-the-shelf standard operating systems (Ubuntu, Debian, Red Hat, Windows Server) and standard VM orchestration tooling. |
| **Resource Scheduling** | Normal world hypervisor cannot dynamically reclaim, swap, or allocate memory to Secure World on demand without complex static partitions. | Cloud hypervisor must retain control over physical resource scheduling, overcommit, and hardware dispatch without seeing tenant data. |
| **Attestation** | Verifies platform manufacturing state, but does not offer fine-grained tenant-controlled cryptographic attestation for dynamic VMs. | Standardized, verifiable remote attestation measuring dynamic guest VM boot state, initial memory, and runtime firmware. |

---

## 1.3 The Arm Confidential Compute Architecture (Arm CCA) Paradigm

To address the limitations of both hypervisor virtualization and TrustZone, Arm introduced the **Arm Confidential Compute Architecture (Arm CCA)** as part of the Armv9-A architecture extension. 

Arm CCA fundamentally transforms the computing trust model by establishing a complete operational separation between:
1. **Resource Management (Scheduling & Allocation)**: Remains under the control of the untrusted Host Hypervisor (e.g., Linux KVM, VMware ESXi).
2. **Access Permission & Confidentiality (Data Access & Protection)**: Strictly enforced at hardware line speed by processor hardware extensions, memory protection units, and a dedicated, minimal, open-source firmware component called the **Realm Management Monitor (RMM)**.

```mermaid
graph TD
    subgraph CCA_Paradigm["Arm CCA Orthogonal Decoupling Model"]
        direction TB
        subgraph Resource_Control["Untrusted Control Plane (Hypervisor / Host)"]
            HYP["Host Hypervisor (KVM / Xen)<br/>• Physical Memory Allocation<br/>• Virtual CPU Scheduling<br/>• I/O Device Emulation Routing"]
        end
        
        subgraph Hardware_Enforced_Gate["Hardware Memory & State Boundary"]
            RME_HW["Armv9-A RME (Granule Protection Checks - GPC)<br/>Memory Protection Engine (MPE)<br/>Root of Trust Hardware Engine"]
        end
        
        subgraph Protected_Workload["Protected Execution Plane (Realms)"]
            REALM1["Confidential VM (Realm 1)<br/>• Unmodified Guest OS<br/>• Proprietary Tenant Payload<br/>• Private Data in Memory"]
            REALM2["Confidential VM (Realm 2)<br/>• Unmodified Guest OS<br/>• Proprietary Tenant Payload<br/>• Private Data in Memory"]
        end
        
        HYP -->|"Allocates Memory & Dispatches PEs"| RME_HW
        RME_HW -->|"Blocks Unauthorized Read/Write/Snoop"| HYP
        RME_HW --- REALM1
        RME_HW --- REALM2
    end
    
    style Resource_Control fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
    style Hardware_Enforced_Gate fill:#d4efdf,stroke:#27ae60,stroke-width:2px;
    style Protected_Workload fill:#d6eaf8,stroke:#2980b9,stroke-width:2px;
```

### Core Terminology
- **Realm**: An isolated execution environment running a complete, unmodified virtual machine (including guest operating system kernel and applications). A Realm's memory contents, general-purpose register state, system registers, vector registers, and translation tables are completely shielded from the host hypervisor, other Realms, and the Secure World.
- **Host**: The hypervisor and host operating system running in the Non-Secure world responsible for allocating physical memory granules to Realms, assigning virtual CPU time slices, and routing interrupts.
- **Realm Execution Context (REC)**: The architectural structure representing a virtual CPU within a Realm, analogous to a vCPU thread in standard virtualization, but containing cryptographic protections and hardware-enforced isolation.
- **Realm Translation Table (RTT)**: The Stage-2 translation table hierarchy that maps Intermediate Physical Addresses (IPAs) used by the Realm to Physical Addresses (PAs) in the Realm Physical Address Space.
- **Granule Protection Check (GPC)**: The hardware circuit residing inside the processor Memory Management Unit (MMU) that intercepts physical memory accesses after Stage-1 and Stage-2 translations to verify whether the physical address access conforms to the assigned Physical Address Space.

---

## 1.4 Trust Boundaries and TCB Minimization

The overarching design objective of Arm CCA is the radical reduction of the **Trusted Computing Base (TCB)** for tenant workloads.

In a traditional cloud deployment, the TCB of an application comprises:
$$\\text{TCB}_{\\text{Traditional}} = \\text{Hardware} + \\text{Firmware/UEFI} + \\text{Host OS/Hypervisor} + \\text{Device Emulators} + \\text{Host Admin Stack} + \\text{Guest OS}$$

Under the Arm CCA security model (as formally specified in **ARM-DEN-0096**), the Host Hypervisor, cloud administrative tooling, and peripheral device emulation layers are **completely eliminated from the tenant's TCB**:
$$\\text{TCB}_{\\text{Arm CCA}} = \\text{Silicon RoT Hardware} + \\text{EL3 Monitor Firmware (TF-A)} + \\text{Realm Management Monitor (TF-RMM)} + \\text{Guest OS}$$

```
+---------------------------------------------------------------------------------+
|                                 TENANT TCB COMPARISON                            |
+---------------------------------------------------------------------------------+
| TRADITIONAL VIRTUALIZATION                      | ARM CCA CONFIDENTIAL VM        |
+-------------------------------------------------+--------------------------------+
| [X] Cloud Admin / Host Operator (Inside TCB)    | [ ] Cloud Admin (OUTSIDE TCB)  |
| [X] Host Hypervisor / KVM / QEMU (Inside TCB)   | [ ] Host Hypervisor (OUTSIDE)  |
| [X] Device Emulation Stacks (Inside TCB)        | [ ] Device Emulation (OUTSIDE) |
| [X] BMC / Out-of-band Mgmt (Inside TCB)         | [ ] BMC / Out-of-band (OUTSIDE)|
| [X] Secure World Firmware (Inside TCB)          | [ ] Secure World (OUTSIDE TCB) |
| [X] Physical DRAM Interposers (Threat Vector)   | [ ] DRAM Interposers (Mitigated)|
|-------------------------------------------------+--------------------------------|
| [✓] Guest OS & Applications                     | [✓] Guest OS & Applications    |
| [✓] Physical Processor Hardware                 | [✓] Processor Hardware (Armv9) |
|                                                 | [✓] EL3 Monitor (Minimal TF-A) |
|                                                 | [✓] Realm Mgmt Monitor (TF-RMM)|
+---------------------------------------------------------------------------------+
```

### The Three Fundamental Security Guarantees
As defined in the *Arm CCA Security Model* (ARM-DEN-0096):
1. **Confidentiality & Integrity to Realm Owner**:
   - The platform guarantees that no software executing outside the Realm (including the hypervisor at `NS-EL2`, any Secure World code at `S-EL0`–`S-EL2`, or other Realms) can observe or alter the code, data, registers, or execution flow of the Realm.
   - Physical memory bus attacks (snooping, bus modification, DRAM extraction) are mitigated via inline hardware memory encryption and cryptographic integrity tagging.
2. **Isolation Guarantee to Hosting Environment**:
   - The platform guarantees that a compromised, malicious, or malfunctioning Realm cannot compromise the stability, confidentiality, or integrity of the Host Hypervisor, other virtual machines, the Secure World, or the hardware platform.
   - A Realm cannot perform unauthorized physical address accesses, launch denial-of-service attacks on memory buses, or hijack exception handlers of the host.
3. **Cryptographic Attestation & Verifiability**:
   - Before provisioning confidential data (such as proprietary AI weights, healthcare records, or financial transaction keys) into a Realm, the Realm owner can cryptographically verify:
     - The authentic hardware identity of the silicon.
     - The patch version and integrity of the platform firmware (`EL3` Monitor and RMM).
     - The initial measurement and launch state of the Realm payload.

---

## 1.5 Ecosystem Roles & Responsibilities

The Arm CCA architecture establishes distinct ecosystem roles with formal boundaries, ensuring clear division of cryptographic keys, privileges, and operational duties:

```mermaid
sequenceDiagram
    autonumber
    participant Silicon as Silicon Provider (Arm / Chipmaker)
    participant OEM as Platform Manufacturer (OEM/ODM)
    participant CSP as Cloud Service Provider (Host)
    participant Tenant as Realm Owner (Tenant)
    participant CCA as Arm CCA Hardware & Firmware

    Silicon->>CCA: Fuses RoT Public Keys & Hardware Root Keys (HUK)
    OEM->>CCA: Flashes Signed Immutable EL3 Boot Firmware
    CSP->>CCA: Deploys Host OS & KVM Hypervisor (NS-EL2)
    Tenant->>CSP: Requests Creation of Confidential Realm VM
    CSP->>CCA: Invokes RMI to Allocate Memory & Spawn Realm REC
    CCA-->>Tenant: Generates Signed Cryptographic Attestation Token
    Tenant->>Tenant: Verifies Token against Silicon RoT & Expected Measurement
    Tenant->>CCA: Injects Encrypted Tenant Secrets & Starts Execution
```

1. **Silicon Provider (Arm & Silicon Partners)**:
   - Implements the Armv9.1-A (and later) architecture featuring the Realm Management Extension (RME).
   - Injects the Hardware Unique Key (HUK) and Platform RoT Public Keys into on-chip non-volatile One-Time Programmable (OTP) fuses during chip manufacturing.
   - Publishes public endorsement certificates that link the chip's unique identity to verified silicon authenticity.
2. **Platform Manufacturer (OEM / ODM)**:
   - Integrates the SoC into server boards, incorporating power management, BMC, DRAM controllers, and PCIe root complexes.
   - Provisions platform initial boot code (BL1, BL2) adhering to Arm Base System Architecture (BSA) and Server Base System Architecture (SBSA).
3. **Cloud Service Provider (CSP / Host)**:
   - Manages physical compute, storage, and networking hardware.
   - Deploys the host operating system and hypervisor (e.g., Linux KVM).
   - Controls physical resource scheduling, CPU pin assignments, dynamic memory overcommit, and hardware teardown.
   - *Crucially, the CSP does NOT need to be trusted by the tenant for data confidentiality or execution integrity.*
4. **Realm Owner (Tenant)**:
   - Builds and owns the confidential workload, operating system image, and sensitive data.
   - Defines security policies, evaluates attestation evidence, and releases decryption keys directly to the Realm across an encrypted, authenticated channel.

---
"""

module2_content = """# Module 2: Armv9-A Security States & Physical Address Spaces (PAS)

## 2.1 The Four Security States in Armv9-A

Prior to Armv9-A RME, the Arm architecture supported only two security states: **Non-Secure State** and **Secure State**. The current security state was determined by the `SCR_EL3.NS` bit. 

With the introduction of the **Realm Management Extension (FEAT_RME)** in Armv9.1-A, the architectural execution model is expanded to **four mutually isolated Security States**:
1. **Non-Secure State**: The standard operating environment hosting traditional hypervisors (KVM, Xen), guest operating systems, and client applications.
2. **Secure State**: The environment hosting platform firmware services, TrustZone Trusted OSs (e.g., OP-TEE, Trusted Services), and vendor-specific Trusted Applications.
3. **Realm State**: The execution environment dedicated strictly to Confidential Virtual Machines (Realms) and their privileged supervisor code.
4. **Root State**: The most privileged architectural state, reserved exclusively for the Exception Level 3 (`EL3`) firmware monitor (such as Trusted Firmware-A). Root state replaces the legacy concept of "Secure EL3".

```mermaid
graph TD
    subgraph Armv9_Four_Security_States["Armv9-A Four Security States & Exception Level Hierarchy"]
        direction TB
        
        subgraph Root_World["ROOT STATE"]
            EL3["Root EL3: Firmware Monitor (TF-A)<br/>• Controls Granule Protection Checks (GPC)<br/>• Owns GPTBR_EL3 / GPCCR_EL3<br/>• Context Switch Dispatcher (RMMD)"]
        end
        
        subgraph Realm_World["REALM STATE"]
            R_EL2["Realm EL2: Realm Management Monitor (TF-RMM)<br/>• Stage-2 Realm Translation (RTT)<br/>• Realm Contexts (REC)<br/>• Manages Realm Attestation"]
            R_EL1["Realm EL1: Realm Guest OS Kernel<br/>(Linux Kernel, EDK2 Firmware)"]
            R_EL0["Realm EL0: Tenant User Applications<br/>(AI Models, Databases, Microservices)"]
            R_EL2 --> R_EL1 --> R_EL0
        end
        
        subgraph Secure_World["SECURE STATE"]
            S_EL2["Secure EL2: Secure Partition Manager (SPMC)"]
            S_EL1["Secure EL1: Trusted OS (OP-TEE, Hafnium)"]
            S_EL0["Secure EL0: Trusted Applications (TAs)"]
            S_EL2 --> S_EL1 --> S_EL0
        end
        
        subgraph NonSecure_World["NON-SECURE STATE"]
            NS_EL2["Non-Secure EL2: Host Hypervisor (Linux KVM)<br/>• Resource Allocation<br/>• PE Scheduling & Interrupt Routing"]
            NS_EL1["Non-Secure EL1: Host OS Kernel"]
            NS_EL0["Non-Secure EL0: Host User Utilities (QEMU, kvmtool)"]
            NS_EL2 --> NS_EL1 --> NS_EL0
        end
        
        Root_World --- Realm_World
        Root_World --- Secure_World
        Root_World --- NonSecure_World
    end
    
    style Root_World fill:#fcf3cf,stroke:#b7950b,stroke-width:2px;
    style Realm_World fill:#d6eaf8,stroke:#2980b9,stroke-width:2px;
    style Secure_World fill:#d4efdf,stroke:#27ae60,stroke-width:2px;
    style NonSecure_World fill:#fadbd8,stroke:#c0392b,stroke-width:2px;
```

### Architectural Controls of Current Security State
The active security state of the Processing Element (PE) is determined by two control bits located in the Secure Configuration Register at EL3 (`SCR_EL3`):
- `SCR_EL3.NS` (Non-Secure bit)
- `SCR_EL3.NSE` (Non-Secure Extension bit)

The decoding of these bits governs which security state the PE executes in when transitioning to lower exception levels (`EL2`, `EL1`, `EL0`):

| `SCR_EL3.NSE` | `SCR_EL3.NS` | Exception Level | Architectural Security State | Description |
| :---: | :---: | :---: | :---: | :--- |
| `X` | `X` | **EL3** | **Root State** | Root state is active whenever executing at `EL3`, regardless of `NS`/`NSE` bit values. |
| `0` | `0` | **EL2, EL1, EL0** | **Secure State** | Traditional TrustZone Secure World. |
| `0` | `1` | **EL2, EL1, EL0** | **Non-Secure State** | Standard Normal World. |
| `1` | `1` | **EL2, EL1, EL0** | **Realm State** | Confidential Computing Realm World. |
| `1` | `0` | **EL2, EL1, EL0** | *Reserved* | Architecturally reserved (causes an illegal exception return if attempted). |

Transitions between different security states can **only** occur by taking an exception to Root EL3 (e.g., via an `SMC` instruction or an interrupt configured to route to EL3), executing the EL3 monitor context-save routine, reprogramming `SCR_EL3`, and executing an `ERET` instruction into the target security state. Direct horizontal transitions between Non-Secure, Secure, and Realm states are strictly impossible in hardware.

---

## 2.2 Physical Address Spaces (PAS)

A foundational innovation of RME is the complete decoupling between **Virtual Addresses (VA)**, **Intermediate Physical Addresses (IPA)**, and physical memory classification.

In legacy architectures, an address transaction emitted onto the system bus had an associated single-bit tag: `NS = 0` (Secure) or `NS = 1` (Non-Secure). Under RME, physical memory is partitioned into **four distinct Physical Address Spaces (PAS)**:
1. **Root PAS**: Houses sensitive `EL3` monitor code, private stacks, cryptographic keys, and the Granule Protection Tables (GPT) themselves.
2. **Realm PAS**: Houses Realm code, Realm private data, Realm Execution Context (REC) metadata, and Realm Stage-2 translation tables (RTT).
3. **Secure PAS**: Houses TrustZone Trusted OS images, Secure partitions, and Trusted Application memory.
4. **Non-Secure PAS**: Houses host hypervisor code, guest operating systems of traditional VMs, DMA buffers, and shared communication pools.

```mermaid
graph LR
    subgraph Virtual_To_Physical_Pipeline["Address Translation & PAS Assignment Pipeline"]
        VA["Virtual Address (VA)<br/>[EL0 / EL1]"] -->|"Stage 1 Translation"| IPA["Intermediate Physical Address (IPA)<br/>[EL1 / EL2]"]
        IPA -->|"Stage 2 Translation"| PA_With_PAS["Target Physical Address (PA)<br/>+ Desired Output PAS"]
        PA_With_PAS -->|"Granule Protection Check (GPC)"| Interconnect["Interconnect Bus (ACE5/CHI)<br/>Tagged with PAS[1:0]"]
    end
    
    style Virtual_To_Physical_Pipeline fill:#f8f9f9,stroke:#7f8c8d,stroke-width:2px;
```

Every physical bus transaction emitted by a PE, System MMU (SMMU), or DMA controller is qualified with an architectural 2-bit PAS tag:
- `0b00`: Non-Secure PAS
- `0b01`: Secure PAS
- `0b10`: Root PAS
- `0b11`: Realm PAS

---

## 2.3 Legal PAS Access Matrix

Hardware enforces strict, unbypassable boundary rules governing which Physical Address Spaces can be accessed by software executing in each Security State. 

Software executing in a given security state can only target physical memory belonging to a permissible subset of PASs. Any attempt by software to emit an access to an unauthorized PAS is blocked immediately by the core MMU or interconnect, triggering a synchronous exception:

```mermaid
graph TD
    subgraph Access_Matrix_Flow["Architectural Access Matrix (Security State -> Permitted PAS)"]
        ROOT_STATE["Root State (EL3)"]
        REALM_STATE["Realm State (R-EL2, R-EL1, R-EL0)"]
        SECURE_STATE["Secure State (S-EL2, S-EL1, S-EL0)"]
        NS_STATE["Non-Secure State (NS-EL2, NS-EL1, NS-EL0)"]
        
        PAS_ROOT[("Root PAS")]
        PAS_REALM[("Realm PAS")]
        PAS_SECURE[("Secure PAS")]
        PAS_NS[("Non-Secure PAS")]
        
        ROOT_STATE ==>|"Unrestricted Access"| PAS_ROOT
        ROOT_STATE ==>|"Unrestricted Access"| PAS_REALM
        ROOT_STATE ==>|"Unrestricted Access"| PAS_SECURE
        ROOT_STATE ==>|"Unrestricted Access"| PAS_NS
        
        REALM_STATE -->|"Full Access"| PAS_REALM
        REALM_STATE -->|"Shared Buffers Only"| PAS_NS
        REALM_STATE -.->|"STRICTLY BLOCKED"| PAS_ROOT
        REALM_STATE -.->|"STRICTLY BLOCKED"| PAS_SECURE
        
        SECURE_STATE -->|"Full Access"| PAS_SECURE
        SECURE_STATE -->|"Shared Buffers"| PAS_NS
        SECURE_STATE -.->|"STRICTLY BLOCKED"| PAS_ROOT
        SECURE_STATE -.->|"STRICTLY BLOCKED"| PAS_REALM
        
        NS_STATE -->|"Full Access"| PAS_NS
        NS_STATE -.->|"STRICTLY BLOCKED (GPF)"| PAS_ROOT
        NS_STATE -.->|"STRICTLY BLOCKED (GPF)"| PAS_REALM
        NS_STATE -.->|"STRICTLY BLOCKED (GPF)"| PAS_SECURE
    end
    
    style ROOT_STATE fill:#fcf3cf,stroke:#b7950b,stroke-width:2px;
    style REALM_STATE fill:#d6eaf8,stroke:#2980b9,stroke-width:2px;
    style SECURE_STATE fill:#d4efdf,stroke:#27ae60,stroke-width:2px;
    style NS_STATE fill:#fadbd8,stroke:#c0392b,stroke-width:2px;
    
    style PAS_ROOT fill:#f9e79f,stroke:#d4ac0d,stroke-width:2px;
    style PAS_REALM fill:#aed6f1,stroke:#3498db,stroke-width:2px;
    style PAS_SECURE fill:#a9dfbf,stroke:#2ecc71,stroke-width:2px;
    style PAS_NS fill:#f5b7b1,stroke:#e74c3c,stroke-width:2px;
```

### Comprehensive Access Enforcement Table

| Executing Security State | Target: Non-Secure PAS | Target: Secure PAS | Target: Realm PAS | Target: Root PAS | Architectural Result / Notes |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **Root (EL3)** | **ALLOWED** | **ALLOWED** | **ALLOWED** | **ALLOWED** | Root state has architectural supremacy. It can access all four physical address spaces. Essential for initializing GPTs, dispatching contexts, and managing system boot. |
| **Realm (R-EL2, R-EL1, R-EL0)** | **ALLOWED** | **BLOCKED** *(GPF)* | **ALLOWED** | **BLOCKED** *(GPF)* | Realm software can access Realm PAS (private data) and Non-Secure PAS (shared I/O communication buffers). Access to Secure PAS or Root PAS is blocked. |
| **Secure (S-EL2, S-EL1, S-EL0)** | **ALLOWED** | **ALLOWED** | **BLOCKED** *(GPF)* | **BLOCKED** *(GPF)* | Secure software can access Secure PAS and Non-Secure PAS. It has **zero visibility** into Realm PAS or Root PAS. |
| **Non-Secure (NS-EL2, NS-EL1, NS-EL0)** | **ALLOWED** | **BLOCKED** *(GPF)* | **BLOCKED** *(GPF)* | **BLOCKED** *(GPF)* | Host Hypervisor and normal OS can **only** access Non-Secure PAS. Any access to Root, Secure, or Realm PAS triggers an immediate Granule Protection Fault. |

---

## 2.4 Translation Regimes & Controlling Output PAS

Translation tables (Stage-1 and Stage-2) are configured to control which PAS a translated address targets.

### Translation Regimes Overview
1. **Non-Secure Translation Regimes**:
   - `NS-EL1&0`: Stage-1 translates VA to IPA/PA. If Stage-2 is enabled (`NS-EL2`), Stage-2 translates IPA to PA.
   - Non-Secure translation regimes **cannot generate physical addresses targeting Root, Secure, or Realm PAS**. Even if a malicious hypervisor configures its Stage-2 translation descriptors to point to a physical address owned by a Realm, the hardware MMU verifies the requested PAS against the current security state and blocks the access.
2. **Realm Translation Regimes**:
   - `Realm EL1&0`: Stage-1 translates Realm VA to Realm IPA.
   - `Realm EL2`: Stage-2 translates Realm IPA to target PA.
   - The Stage-2 translation descriptors managed by the RMM encode whether the output target is **Realm PAS** (for private Realm memory) or **Non-Secure PAS** (for shared I/O buffers).
   - In Realm translation table descriptors, the top bit of the address or specific attribute bits (such as bit 55 or bit 63 depending on formatting) select between Realm and Non-Secure PAS.
3. **Root & Secure Translation Regimes**:
   - Root EL3 uses `TTBR0_EL3` and translation table descriptors that can explicitly encode any of the four target PASs using descriptor attribute bits `NSE` and `NS`.

```
Descriptor Bit Encoding for Output PAS (Armv9-A Page Table Descriptors):
+--------------------------------------------------------------+
| Bit [56] (NSE) | Bit [5] (NS) | Output Physical Address Space|
+----------------+--------------+------------------------------+
|       0        |      0       | Secure PAS                   |
|       0        |      1       | Non-Secure PAS               |
|       1        |      0       | Root PAS                     |
|       1        |      1       | Realm PAS                    |
+--------------------------------------------------------------+
```

---

## 2.5 Bus and Interconnect Extensions: Tagging Transactions

Software-level enforcement at the core MMU is insufficient to guarantee complete platform confidentiality; peripheral devices, memory controllers, and multi-socket interconnects must also honor PAS boundaries.

To propagate PAS isolation across the SoC, Arm enhanced its AMBA bus specifications:
- **AMBA ACE5 / ACE5-Lite**: Extended with sideband signals carrying the PAS classification for every read, write, and snoop transaction:
  - `AWPAS[1:0]` (Write Address Physical Address Space)
  - `ARPAS[1:0]` (Read Address Physical Address Space)
- **AMBA CHI (Coherent Hub Interface) Issue E**: Extended with explicit PAS packet header fields that accompany transactions across the on-chip mesh fabric and coherent interconnect (e.g., CoreLink CMN-700).

```
AMBA Interconnect Signals:
  Core / PE ----[ ARADDR + ARPAS[1:0] ]----> Interconnect (CMN-700)
            <---[ RDATA  + RRESP      ]----
            ----[ AWADDR + AWPAS[1:0] ]----> Granule Protection Checker (GPC)
                                                      |
                                            Pass?     | Fail?
                                           +----------+----------+
                                           |                     |
                                      [ DRAM Controller ]   [ System Error / GPF ]
```

When an address packet arrives at a memory controller or coherent cache slice, the hardware ensures that the cached data lines are tagged with their corresponding PAS. This prevents **cache aliasing attacks**, where a non-secure process might attempt to read a cached physical line that was populated by a Realm.

---
"""

module3_content = """# Module 3: Granule Protection Checks (GPC) & Granule Protection Tables (GPT)

## 3.1 Hardware Granule Protection Checks (GPC) Architecture

The centerpiece of hardware isolation in the Realm Management Extension is the **Granule Protection Check (GPC)** engine. 

While Stage-1 and Stage-2 MMUs translate Virtual Addresses to Physical Addresses and enforce read/write/execute permissions, the GPC serves as an independent, hardware-enforced **validator of physical address ownership**. The GPC evaluates physical addresses *after* all MMU translations are complete, immediately prior to dispatching transactions to L1/L2/L3 caches, system interconnects, or external memory controllers.

```mermaid
graph TD
    subgraph MMU_GPC_Pipeline["Processing Element (PE) Address Translation & Check Pipeline"]
        direction TB
        VA["Virtual Address (VA)"] --> S1["Stage-1 Translation (VA -> IPA / PA)<br/>Enforces Read/Write/Execute & User/Privilege"]
        S1 --> S2["Stage-2 Translation (IPA -> PA)<br/>Enforces Hypervisor / Realm Stage-2 Isolation"]
        S2 --> PA["Evaluated Physical Address (PA) + Output PAS"]
        
        subgraph GPC_Engine["Granule Protection Checker (Hardware Engine)"]
            TLB_GPC["GPC TLB (Lookaside Cache)<br/>Caches recent GPI lookups"]
            GPC_Logic["Comparison Logic:<br/>Does Output PAS == Granule Assigned PAS?"]
            GPT_Walker["Hardware GPT Walker:<br/>Traverses Level 0 & Level 1 GPTs in Root PAS"]
        end
        
        PA --> GPC_Engine
        TLB_GPC -.-> GPC_Logic
        GPT_Walker -.-> TLB_GPC
        
        GPC_Logic -->|MATCH: Legal Access| Bus["System Interconnect / Cache Hierarchy"]
        GPC_Logic -->|MISMATCH: Illegal Access| GPF["Granule Protection Fault (GPF)<br/>Synchronous Data/Instruction Abort"]
    end
    
    style MMU_GPC_Pipeline fill:#fdfefe,stroke:#2c3e50,stroke-width:2px;
    style GPC_Engine fill:#ebf5fb,stroke:#2980b9,stroke-width:2px;
    style GPF fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
    style Bus fill:#d4efdf,stroke:#27ae60,stroke-width:2px;
```

### The Granule Concept
Under RME, all physical memory in the system is discretized into uniform atomic units called **granules**. 
- The architectural granule size is configurable by platform firmware at system boot:
  - **4 KB** (standard granule, matching standard 4KB MMU pages)
  - **16 KB**
  - **64 KB** (frequently utilized in high-performance enterprise server configurations)
- At any given point in time, every physical granule in the system has a single, unambiguously assigned **Granule Protection Information (GPI)** attribute defining which of the four Physical Address Spaces it belongs to.

---

## 3.2 Granule Protection Tables (GPT) Structure

The ownership of every physical granule across the entire physical address range is tracked in a globally authoritative, hierarchical table structure called the **Granule Protection Table (GPT)**.

The GPT structure is located strictly in the **Root Physical Address Space**. It can only be mapped, modified, and written by firmware executing in **Root EL3**. Even the hypervisor at `NS-EL2` or the Realm Management Monitor at `R-EL2` cannot directly alter a GPT entry.

### System Control Registers
Granule Protection Checks are governed by two primary EL3 control registers:
1. **`GPCCR_EL3` (Granule Protection Check Configuration Register, EL3)**:
   - `GPC`: Global enable bit for Granule Protection Checks.
   - `PGS` (Physical Granule Size): Configures the system granule size (`0b00` = 4KB, `0b01` = 64KB, `0b10` = 16KB).
   - `L0GPTSZ` (Level 0 GPT Size): Encodes the physical address range covered by each Level 0 entry (e.g., 1GB, 512MB).
   - `PPS` (Protected Physical Address Size): Introduced in Armv9.1-A / `FEAT_RME_GPC3` to define the maximum physical address range covered by the GPT (up to 52 bits). Any physical address beyond `PPS` defaults strictly to Non-Secure PAS, avoiding unnecessary page table memory consumption.
2. **`GPTBR_EL3` (Granule Protection Table Base Register, EL3)**:
   - Holds the 64-bit base physical address (in Root PAS) of the root Level 0 Granule Protection Table.

```mermaid
graph TD
    subgraph Two_Level_GPT_Walk["Two-Level Granule Protection Table Structure"]
        direction TB
        GPTBR["GPTBR_EL3 (Points to Base of Level 0 Table in Root PAS)"]
        
        subgraph L0_Table["Level 0 Granule Protection Table (Indexed by PA[PA_WIDTH-1 : 30])"]
            L0E_0["L0 Entry 0 (1GB Block Descriptor: All Non-Secure)"]
            L0E_1["L0 Entry 1 (Table Descriptor -> Points to L1 Table)"]
            L0E_2["L0 Entry 2 (1GB Block Descriptor: All Realm)"]
            L0E_N["L0 Entry N (1GB Block Descriptor: Any / Completer-side)"]
        end
        
        subgraph L1_Table["Level 1 Granule Protection Table (Indexed by PA[29 : 16])"]
            L1_Desc0["L1 Entry 0 (Granule Descriptor: 16 GPIs for 16 Granules)"]
            L1_Desc1["L1 Entry 1 (Contiguous Descriptor)"]
            L1_DescK["L1 Entry K (...)"]
        end
        
        GPTBR --> L0_Table
        L0E_1 -->|"Points to PA of L1 Table in Root PAS"| L1_Table
        
        subgraph GPI_Breakdown["Granule Descriptor Anatomy (64 bits = 16 x 4-bit GPI Entries)"]
            GPI_0["GPI 0 [3:0]<br/>Granule 0: Realm"]
            GPI_1["GPI 1 [7:4]<br/>Granule 1: NS"]
            GPI_2["GPI 2 [11:8]<br/>Granule 2: Secure"]
            GPI_15["GPI 15 [63:60]<br/>Granule 15: Root"]
        end
        
        L1_Desc0 --> GPI_Breakdown
    end
    
    style Two_Level_GPT_Walk fill:#fcfcfc,stroke:#34495e,stroke-width:2px;
    style L0_Table fill:#fef9e7,stroke:#f1c40f,stroke-width:2px;
    style L1_Table fill:#ebf5fb,stroke:#3498db,stroke-width:2px;
    style GPI_Breakdown fill:#e8f8f5,stroke:#1abc9c,stroke-width:2px;
```

---

## 3.3 Two-Level GPT Lookup Walk & Descriptors

The architecture implements a flexible two-level lookup scheme:

### Level 0 Descriptors (L0GPTE)
Each entry in the Level 0 GPT covers a large, contiguous chunk of physical address space (typically **1 GB** per entry). A Level 0 entry is a 64-bit value that can take one of two distinct formats:
1. **Block Descriptor**:
   - Assigns the entire 1 GB physical memory block uniformly to a single PAS (or flags it as "Any", delegating checks to peripheral completer-side filters).
   - Highly efficient: eliminates the need to allocate Level 1 tables for large swaths of contiguous non-secure DRAM or memory-mapped I/O (MMIO) spaces.
2. **Table Descriptor**:
   - Indicates that the 1 GB region is finely subdivided into individual granules with varying PAS assignments.
   - Contains the 64-bit base physical address of the corresponding **Level 1 GPT** in Root PAS.

### Level 1 Descriptors (L1GPTE)
Each Level 1 table descriptor covers a portion of memory broken down to the system granule size. A Level 1 entry is a 64-bit descriptor that can be formatted as:
1. **Granule Descriptor**:
   - Encodes ownership for **16 contiguous granules**.
   - The 64-bit entry is divided into **16 separate 4-bit Granule Protection Information (GPI)** fields:
     $$\\text{L1GPTE}[4i+3 : 4i] = \\text{GPI for Granule } i \\quad (i \\in [0, 15])$$
2. **Contiguous Descriptor**:
   - Encodes that a block larger than a single granule (e.g., 2MB or 32MB) shares identical GPI properties.
   - Facilitates aggregated caching in the GPC TLBs, minimizing translation table walk penalties.

### GPI Value Encodings (4-bit field)

| GPI Encoding `[3:0]` | Assigned Physical Address Space | Architectural Behavior & Usage |
| :---: | :---: | :--- |
| `0b0000` | **Non-Secure (NS)** | Memory assigned to the host OS, standard VMs, or normal device buffers. |
| `0b0001` | **Root** | Memory holding EL3 monitor firmware, secure configuration, or GPT nodes. |
| `0b0010` | **Realm** | Memory holding Realm private data, REC execution states, or RTT page tables. |
| `0b0011` | **Secure** | Memory holding TrustZone firmware, Trusted OS stacks, or Secure storage. |
| `0b1000` | **Any** | Bypasses core GPC filtering; checks delegated to external programmable completer filters (used for legacy peripherals or shared MMIO fabrics). |
| *Others* | *Reserved* | Unassigned / Reserved. Triggers a Granule Protection Fault on any access. |

---

## 3.4 Granule Protection Faults (GPF)

When a processing element or bus initiator attempts a memory access where the output PAS generated by the translation regime does **not** match the GPI programmed in the Granule Protection Tables, hardware immediately aborts the transaction with a **Granule Protection Fault (GPF)**.

### Architectural Fault Classification
GPFs are classified into two broad categories:
1. **Synchronous Granule Protection Faults**:
   - Occur when a core PE instruction fetch or load/store instruction violates GPC rules.
   - Manifests as a **Synchronous Data Abort** or **Instruction Abort** taken to the current or higher Exception Level.
   - **Fault Syndrome Registers**:
     - `ESR_ELx.EC`: Contains Exception Class `0b100100` (Data Abort) or `0b100000` (Instruction Abort).
     - `ESR_ELx.DFSC` / `IFSC`: Contains specific Data/Instruction Fault Status Codes indicating:
       - `0b011100`: Granule Protection Fault on translation table walk (Level 0).
       - `0b011101`: Granule Protection Fault on translation table walk (Level 1).
       - `0b011110`: Granule Protection Fault on primary access.
     - `FAR_ELx` (Fault Address Register): Captures the precise Virtual Address that triggered the fault.
     - `HPFAR_EL2` / `HPFAR_EL3`: Captures the Intermediate Physical Address (IPA).
2. **Asynchronous / External Granule Protection Faults**:
   - Occur when background write-backs, prefetch operations, or external DMA controllers (via SMMU) violate GPC rules.
   - Signaled as an **SError Interrupt** (System Error) or routed directly to EL3 via an asynchronous fault interrupt line.

```
Synchronous Fault Dispatch Hierarchy:
  Illegal Access by NS-EL1 ---> Trapped to NS-EL2 (Host Hypervisor)
  Illegal Access by R-EL1  ---> Trapped to R-EL2 (TF-RMM)
  Illegal Access by R-EL2  ---> Trapped to Root EL3 (TF-A)
```

---

## 3.5 Dynamic Granule Transitions & Memory Scrubbing

A fundamental capability of Arm CCA is **dynamic physical memory reassignment**. Unlike traditional TrustZone, where memory carveouts for Secure World are fixed statically at boot time in the TrustZone Address Space Controller (TZASC), Arm CCA allows physical memory granules to be dynamically transitioned between Non-Secure and Realm states during runtime.

However, dynamically transitioning memory introduces a severe security hazard: **Information Remanence & Cross-World Data Leakage**.
- If a Non-Secure granule is transitioned to Realm PAS, stale hypervisor data might be read by the Realm (integrity risk).
- More critically, when a Realm is destroyed or releases memory back to Non-Secure PAS, private Realm data (passwords, encryption keys, decrypted customer data) would be exposed to the host if physical DRAM lines or cache lines are not scrubbed.

### The Granule Transition Protocol
To transition a granule safely, the architecture mandates an atomic, multi-stage protocol executed across the Host Hypervisor, RMM, and Root EL3 Monitor:

```mermaid
sequenceDiagram
    autonumber
    participant Host as Host Hypervisor (NS-EL2)
    participant RMM as Realm Mgmt Monitor (R-EL2)
    participant EL3 as Root Monitor (TF-A EL3)
    participant GPC as Hardware GPC & Caches

    Note over Host,GPC: Phase 1: Initiation
    Host->>RMM: Invokes RMI_DATA_CREATE(Target PA, Realm Context)
    RMM->>EL3: Invokes SMC_RMM_GPT_TRANSITION(PA, From: NS, To: Realm)
    
    Note over EL3,GPC: Phase 2: Hardware Enforcement & Invalidation
    EL3->>GPC: TLBI RPASALLOS / TLBI GPC (Invalidate cached GPC TLBs)
    EL3->>GPC: DC CIPAPA (Clean & Invalidate Physical Address to PoPA)
    EL3->>GPC: Updates Level 1 GPT Entry: GPI = 0b0010 (Realm)
    EL3->>GPC: DSB SY (Data Synchronization Barrier)
    EL3-->>RMM: Returns SUCCESS
    
    Note over RMM,GPC: Phase 3: Zeroing & Scrubbing
    RMM->>GPC: Zeroes entire granule (writes 0x00 to all bytes)
    RMM->>GPC: Maps PA into Realm Stage-2 Translation Table (RTT)
    RMM-->>Host: Returns SUCCESS
```

### Architectural Scrubbing & Invalidation Requirements
1. **Cache Clean and Invalidate to Point of Physical Authenticity (PoPA)**:
   - Before a granule changes PAS ownership, the processor must execute the dedicated cache maintenance instruction:
     ```assembly
     DC CIPAPA, Xt   /* Clean and Invalidate cache by Physical Address to PoPA */
     ```
   - This ensures that any dirty cache lines belonging to the old owner are flushed to DRAM and tagged lines are evicted, preventing stale cache hits under the new PAS.
2. **GPC TLB Invalidation**:
   - Processor GPC TLBs cache recent GPT entries. Firmware must execute:
     ```assembly
     TLBI RPASALLOS  /* TLB Invalidate all Physical Address Spaces, Outer Shareable */
     ```
   - This prevents stale GPC lookup entries from permitting illegal accesses.
3. **Mandatory Hardware Zeroing (Scrubbing)**:
   - When transitioning from Realm PAS back to Non-Secure PAS (via `RMI_DATA_DESTROY`), the RMM zeroizes the memory granule *before* EL3 updates the GPT to Non-Secure. 
   - Even if the host hypervisor attempts to read the physical address immediately upon transition, it reads only zeros.

---

## 3.6 GPC Bypass Windows: Mechanics and Security Bounds

In specific platform configurations, certain physical address ranges must bypass core GPC checking:
- **GPC Bypass Windows**: Architecturally defined physical memory windows configured in `GPCCR_EL3` where incoming transactions are automatically forwarded with `GPI = Any` or directly assigned to Non-Secure PAS without traversing the GPT walk.
- **Legitimate Use Cases**:
  - Legacy platform initialization before GPT structures are allocated in Root RAM.
  - High-bandwidth, fixed memory-mapped I/O (MMIO) fabrics where a hardware-programmable completer filter (such as an external firewall or peripheral filter) already enforces security boundaries.
- **Architectural Security Constraints**:
  - A GPC Bypass Window can **never** be configured over DRAM regions hosting Root PAS or Realm PAS memory.
  - Configuration of bypass windows is locked to Root EL3 and cannot be altered once the system transitions from initial boot to the runtime security lifecycle.

---
"""

with open("arm-security/modules/module1.md", "w") as f:
    f.write(module1_content.strip() + "\n")

with open("arm-security/modules/module2.md", "w") as f:
    f.write(module2_content.strip() + "\n")

with open("arm-security/modules/module3.md", "w") as f:
    f.write(module3_content.strip() + "\n")

print("Generated Modules 1, 2, and 3 successfully.")
