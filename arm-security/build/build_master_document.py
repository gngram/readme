#!/usr/bin/env python3
"""
Master Builder for the ARM Security CCA & RME Comprehensive Architecture Guide.
Combines all modules, adds executive summary, tables of contents, detailed appendices,
glossaries, and generates arm-security/ARM_SECURITY_CCA_RME_COMPREHENSIVE_GUIDE.md.
"""

import os
import re

MODULES_DIR = "arm-security/modules"
OUTPUT_FILE = "arm-security/ARM_SECURITY_CCA_RME_COMPREHENSIVE_GUIDE.md"

preface = """# ARM SECURITY ARCHITECTURE: ARM CCA & REALM MANAGEMENT EXTENSION (RME)
## Comprehensive Technical Reference Manual & Architecture Study Guide
**Document Classification:** Technical Architecture Master Notes  
**Target Coverage:** Complete Arm Confidential Compute Architecture (Arm CCA) & Realm Management Extension (RME)  
**Primary Source Specifications:**
- *Learn the architecture - Introducing Arm Confidential Compute Architecture* (DEN0125 / Issue 4.0)
- *Learn the architecture - Arm Confidential Compute Architecture software stack* (DEN0127 / Issue 3.0)
- *Arm CCA Security Model Specification* (ARM-DEN-0096 / Issue 1.0 EAC)
- *Learn the architecture - Realm Management Extension Guide* (DEN0126 / Issue 1.2)
- *Arm Realm Management Extension (RME) System Architecture* (ARM-DEN-0129 / Issue C.a)

---

## Executive Summary & Guide Roadmap

The **Arm Confidential Compute Architecture (Arm CCA)**, introduced as a core pillar of the **Armv9-A** architecture, establishes a transformative security paradigm for multi-tenant cloud computing, enterprise virtualization, mobile security, and edge intelligence. 

Historically, computing trust models enforced an absolute hierarchy where higher exception levels possessed unrestricted visibility and control over lower exception levels. While functional for resource scheduling, this model created the **Hypervisor Privilege Paradox**: cloud tenants were compelled to trust the cloud service provider's hypervisor, host operating system, administrative staff, firmware, and physical hardware maintenance infrastructure with the confidentiality and integrity of their sensitive workloads.

Arm CCA, enabled in hardware by the **Realm Management Extension (RME)**, shatters this paradigm by decoupling **resource allocation** from **data access rights**:
- The **Host Hypervisor** retains complete responsibility for allocating physical memory, dispatching virtual CPUs, and servicing interrupts.
- However, the hypervisor is stripped of all architectural capability to read, write, tamper with, or snoop the memory, register context, or execution flow of confidential workloads, termed **Realms**.
- Isolation is enforced at hardware line speed by **Granule Protection Checks (GPC)**, backed by two-level **Granule Protection Tables (GPT)** in Root physical address space, inline **Memory Protection Engines (MPE)** with **Memory Encryption Contexts (MEC)**, enhanced **System MMUs (SMMUv3.2/3.3)** with **Device Protection Tables (DPT)**, and PCIe **Integrity and Data Encryption (IDE)**.

This manual provides an exhaustive, publication-grade architectural synthesis across 11 core modules, walking the reader from fundamental threat models and four-world security states down to assembly-level cache invalidation instructions, SMC calling conventions, attestation token structures, and hardware register bitfields.

```mermaid
graph TD
    subgraph Guide_Map["Guide Structure & Architectural Layers"]
        direction TB
        M1["Module 1: Introduction & The Confidential Computing Paradigm Shift"]
        M2["Module 2: Armv9-A Security States & Physical Address Spaces (PAS)"]
        M3["Module 3: Granule Protection Checks (GPC) & Granule Protection Tables (GPT)"]
        M4["Module 4: System Hardware Infrastructure & Memory Protection (MPE, MEC)"]
        M5["Module 5: System MMU (SMMUv3) & Device Assignment (RME-DA, PCIe IDE)"]
        M6["Module 6: Arm CCA Software Architecture & Firmware Stack (TF-A, TF-RMM)"]
        M7["Module 7: Realm Lifecycle, Execution Contexts (REC) & Stage-2 RTT"]
        M8["Module 8: Arm CCA Communication Interfaces (RMI, RSI, RHI, PSCI)"]
        M9["Module 9: Attestation Framework & Cryptographic Trust Chains"]
        M10["Module 10: Security Lifecycle, Debug, RAS & Side-Channel Hardening"]
        M11["Module 11: Comparative Analysis, System Register & Command Reference"]
        M12["Module 12: Architectural Glossary & Master Acronym Index"]
        
        M1 --> M2 --> M3 --> M4 --> M5 --> M6 --> M7 --> M8 --> M9 --> M10 --> M11 --> M12
    end
    
    style Guide_Map fill:#fdfefe,stroke:#2c3e50,stroke-width:2px;
    style M1 fill:#ebf5fb,stroke:#2980b9,stroke-width:2px;
    style M3 fill:#e8f8f5,stroke:#27ae60,stroke-width:2px;
    style M6 fill:#fef9e7,stroke:#f39c12,stroke-width:2px;
    style M9 fill:#f4ecf7,stroke:#8e44ad,stroke-width:2px;
    style M11 fill:#fadbd8,stroke:#c0392b,stroke-width:2px;
```

---

## Detailed Table of Contents

- [Executive Summary & Guide Roadmap](#executive-summary--guide-roadmap)
- [Module 1: Introduction & The Confidential Computing Paradigm Shift](#module-1-introduction--the-confidential-computing-paradigm-shift)
  - [1.1 The Evolution of Compute Isolation & Security Dilemma](#11-the-evolution-of-compute-isolation--security-dilemma)
  - [1.2 Limitations of Arm TrustZone for Cloud Multi-Tenancy](#12-limitations-of-arm-trustzone-for-cloud-multi-tenancy)
  - [1.3 The Arm Confidential Compute Architecture (Arm CCA) Paradigm](#13-the-arm-confidential-compute-architecture-arm-cca-paradigm)
  - [1.4 Trust Boundaries and TCB Minimization](#14-trust-boundaries-and-tcb-minimization)
  - [1.5 Ecosystem Roles & Responsibilities](#15-ecosystem-roles--responsibilities)
- [Module 2: Armv9-A Security States & Physical Address Spaces (PAS)](#module-2-armv9-a-security-states--physical-address-spaces-pas)
  - [2.1 The Four Security States in Armv9-A](#21-the-four-security-states-in-armv9-a)
  - [2.2 Physical Address Spaces (PAS)](#22-physical-address-spaces-pas)
  - [2.3 Legal PAS Access Matrix](#23-legal-pas-access-matrix)
  - [2.4 Translation Regimes & Controlling Output PAS](#24-translation-regimes--controlling-output-pas)
  - [2.5 Bus and Interconnect Extensions: Tagging Transactions](#25-bus-and-interconnect-extensions-tagging-transactions)
- [Module 3: Granule Protection Checks (GPC) & Granule Protection Tables (GPT)](#module-3-granule-protection-checks-gpc--granule-protection-tables-gpt)
  - [3.1 Hardware Granule Protection Checks (GPC) Architecture](#31-hardware-granule-protection-checks-gpc-architecture)
  - [3.2 Granule Protection Tables (GPT) Structure](#32-granule-protection-tables-gpt-structure)
  - [3.3 Two-Level GPT Lookup Walk & Descriptors](#33-two-level-gpt-lookup-walk--descriptors)
  - [3.4 Granule Protection Faults (GPF)](#34-granule-protection-faults-gpf)
  - [3.5 Dynamic Granule Transitions & Memory Scrubbing](#35-dynamic-granule-transitions--memory-scrubbing)
  - [3.6 GPC Bypass Windows: Mechanics and Security Bounds](#36-gpc-bypass-windows-mechanics-and-security-bounds)
- [Module 4: System Hardware Infrastructure & Memory Protection](#module-4-system-hardware-infrastructure--memory-protection)
  - [4.1 Processing Element (PE) Architecture & Granule Data Isolation (GDI)](#41-processing-element-pe-architecture--granule-data-isolation-gdi)
  - [4.2 Main Memory Protection Engine (MPE) & DRAM Encryption](#42-main-memory-protection-engine-mpe--dram-encryption)
  - [4.3 Memory Encryption Contexts (MEC) & MECIDs](#43-memory-encryption-contexts-mec--mecids)
  - [4.4 System Control Processor (SCP) & Trusted Subsystems](#44-system-control-processor-scp--trusted-subsystems)
  - [4.5 Multi-Chip Interconnects & Link Protection](#45-multi-chip-interconnects--link-protection)
  - [4.6 CXL.mem Integration & CXL-TSP](#46-cxlmem-integration--cxl-tsp)
- [Module 5: System MMU (SMMUv3.2/3.3) & Device Assignment (RME-DA & RME-CDA)](#module-5-system-mmu-smmuv3233--device-assignment-rme-da--rme-cda)
  - [5.1 System MMU Role in an RME-Enabled Platform](#51-system-mmu-role-in-an-rme-enabled-platform)
  - [5.2 StreamWorld Configurations & Stream Security](#52-streamworld-configurations--stream-security)
  - [5.3 The Address Translation Services (ATS) Security Dilemma & DPT](#53-the-address-translation-services-ats-security-dilemma--dpt)
  - [5.4 RME Device Assignment (RME-DA) & PCIe IDE](#54-rme-device-assignment-rme-da--pcie-ide)
- [Module 6: Arm CCA Software Architecture & Firmware Stack](#module-6-arm-cca-software-architecture--firmware-stack)
  - [6.1 Complete Software Topology & Trust Hierarchy](#61-complete-software-topology--trust-hierarchy)
  - [6.2 EL3 Firmware: Monitor & RMM Dispatcher (RMMD)](#62-el3-firmware-monitor--rmm-dispatcher-rmmd)
  - [6.3 Realm Management Monitor (TF-RMM) at R-EL2](#63-realm-management-monitor-tf-rmm-at-r-el2)
  - [6.4 Host Hypervisor (KVM / kvmtool / QEMU) at NS-EL2](#64-host-hypervisor-kvm--kvmtool--qemu-at-ns-el2)
  - [6.5 Realm Guest Environment: Linux & EDK2](#65-realm-guest-environment-linux--edk2)
- [Module 7: Realm Lifecycle, Execution Contexts (REC) & Stage-2 Translation (RTT)](#module-7-realm-lifecycle-execution-contexts-rec--stage-2-translation-rtt)
  - [7.1 Realm Lifecycle State Machine](#71-realm-lifecycle-state-machine)
  - [7.2 Realm Execution Context (REC) & Scheduling](#72-realm-execution-context-rec--scheduling)
  - [7.3 Realm Translation Tables (RTT) & RIPAS States](#73-realm-translation-tables-rtt--ripas-states)
  - [7.4 Interrupt Virtualization & Exception Dispatch](#74-interrupt-virtualization--exception-dispatch)
- [Module 8: Arm CCA Communication Interfaces: RMI, RSI, RHI, PSCI](#module-8-arm-cca-communication-interfaces-rmi-rsi-rhi-psci)
  - [8.1 The Realm Management Interface (RMI)](#81-the-realm-management-interface-rmi)
  - [8.2 The Realm Services Interface (RSI)](#82-the-realm-services-interface-rsi)
  - [8.3 The Realm Host Interface (RHI)](#83-the-realm-host-interface-rhi)
  - [8.4 Power State Coordination Interface (PSCI) in Realms](#84-power-state-coordination-interface-psci-in-realms)
- [Module 9: Attestation Framework & Cryptographic Trust Chains](#module-9-attestation-framework--cryptographic-trust-chains)
  - [9.1 The Arm CCA Dual-Token Attestation Architecture](#91-the-arm-cca-dual-token-attestation-architecture)
  - [9.2 Token Formats & Cryptographic Claims](#92-token-formats--cryptographic-claims)
  - [9.3 Cryptographic Key Hierarchy & Derivation](#93-cryptographic-key-hierarchy--derivation)
  - [9.4 Complete Remote Attestation Protocol Flow](#94-complete-remote-attestation-protocol-flow)
- [Module 10: Security Lifecycle, Debug, RAS & Microarchitectural Side-Channel Hardening](#module-10-security-lifecycle-debug-ras--microarchitectural-side-channel-hardening)
  - [10.1 System Security Lifecycle Management](#101-system-security-lifecycle-management)
  - [10.2 Debug, Trace & Profiling Controls in RME](#102-debug-trace--profiling-controls-in-rme)
  - [10.3 Reliability, Availability & Serviceability (RAS) Architecture](#103-reliability-availability--serviceability-ras-architecture)
  - [10.4 Microarchitectural Side-Channel & Fault Injection Mitigations](#104-microarchitectural-side-channel--fault-injection-mitigations)
- [Module 11: Comparative Analysis, System Register & Command Quick Reference](#module-11-comparative-analysis-system-register--command-quick-reference)
  - [11.1 Industry Comparative Analysis: Arm CCA vs. x86 Technologies](#111-industry-comparative-analysis-arm-cca-vs-x86-technologies)
  - [11.2 Master System Register Reference](#112-master-system-register-reference)
  - [11.3 Complete RMI & RSI Command Cheat-Sheet](#113-complete-rmi--rsi-command-cheat-sheet)
  - [11.4 Architectural Implementation Checklist & Golden Invariants](#114-architectural-implementation-checklist--golden-invariants)
- [Module 12: Architectural Glossary & Master Acronym Index](#module-12-architectural-glossary--master-acronym-index)

---
"""

module12_content = """# Module 12: Architectural Glossary & Master Acronym Index

## 12.1 Comprehensive Technical Glossary

- **Arm CCA (Arm Confidential Compute Architecture)**: The overarching system architecture extending Armv9-A to provide hardware-enforced execution environments (Realms) that isolate confidential workloads from privileged software.
- **RME (Realm Management Extension)**: The hardware architectural feature set in Armv9.1-A (and later) defining the four security states, Granule Protection Checks (GPC), Granule Protection Tables (GPT), and new physical address spaces.
- **Root State**: The highest architectural security domain in Armv9-A RME, active at Exception Level 3 (`EL3`), hosting platform root firmware (TF-A). Replaces legacy Secure EL3.
- **Realm State**: The execution state in Armv9-A dedicated to confidential virtual machines and their supervisor monitor, executing at `R-EL0`, `R-EL1`, and `R-EL2`.
- **PAS (Physical Address Space)**: One of four architecturally separated physical memory domains: Root PAS, Realm PAS, Secure PAS, and Non-Secure PAS.
- **Granule**: The minimum atomic unit of physical memory tracking in RME (4KB, 16KB, or 64KB).
- **GPC (Granule Protection Check)**: The hardware comparison logic inside the MMU and SMMU that validates the physical address and output PAS of every memory transaction against the Granule Protection Table.
- **GPT (Granule Protection Table)**: The two-level architectural table structure in Root PAS defining the ownership (GPI) of every physical memory granule in the system.
- **GPI (Granule Protection Information)**: The 4-bit attribute associated with each physical granule indicating its assigned PAS (Root, Realm, Secure, Non-Secure, or Any).
- **GPF (Granule Protection Fault)**: A hardware exception generated when a memory transaction's target PAS does not match the GPI recorded in the GPT.
- **RMM (Realm Management Monitor)**: The trusted privileged firmware layer executing at Realm EL2 (`R-EL2`) responsible for managing Realm contexts, Realm stage-2 translation tables, and Realm attestation.
- **REC (Realm Execution Context)**: The architectural state structure representing a virtual CPU within a Realm.
- **RD (Realm Descriptor)**: The primary metadata structure allocated in Realm PAS tracking configuration, lifecycle state, and measurement hashes for a Realm instance.
- **RTT (Realm Translation Table)**: The Stage-2 translation table hierarchy that maps Intermediate Physical Addresses (IPAs) used by the Realm to Physical Addresses (PAs) in the Realm PAS or Non-Secure PAS.
- **RIPAS (Realm IPA State)**: The architectural state of an IPA within a Realm's stage-2 translation map (`RIPAS_EMPTY`, `RIPAS_RAM`, `RIPAS_DESTROYED`).
- **RMI (Realm Management Interface)**: The SMC-based boundary interface between the Host Hypervisor (`NS-EL2`) and the RMM (`R-EL2`), mediated by the Root EL3 Monitor.
- **RSI (Realm Services Interface)**: The SMC-based boundary interface between the Realm Guest OS (`R-EL1`) and the RMM (`R-EL2`).
- **RHI (Realm Host Interface)**: The paravirtualized communication protocol enabling a Realm to request services, firmware logs, or device certificates from the untrusted host.
- **MPE (Memory Protection Engine)**: The inline cryptographic hardware engine residing in the DRAM memory controller performing line-rate encryption and MAC integrity checks.
- **MEC (Memory Encryption Contexts)**: The architectural extension enabling unique, per-Realm cryptographic keys (MECIDs) for main memory encryption.
- **MECID (Memory Encryption Context Identifier)**: A multi-bit tag (up to 16 bits) identifying the cryptographic key domain associated with a memory transaction.
- **DPT (Device Protection Table)**: An architectural validation structure inside the SMMU ensuring that peripheral devices utilizing Address Translation Services (ATS) do not emit unauthorized DMA transactions.
- **RME-DA (RME Device Assignment)**: The system architecture enabling PCIe peripheral devices and accelerators to be directly and securely assigned to a Realm.
- **PCIe IDE (Integrity and Data Encryption)**: The PCI-SIG standard for line-rate AES-GCM encryption and MAC verification across physical PCIe lanes.
- **TDISP (Trusted Device Interface Security Protocol)**: The standardized protocol governing the configuration, state machine, and binding of virtual device interfaces to confidential VMs.
- **RIM (Realm Initial Measurement)**: The cryptographic hash reflecting all code, initial data, and Stage-2 structures loaded into a Realm prior to activation.
- **REM (Realm Extensible Measurement)**: Monotonically extended cryptographic measurement registers (`REM[0..3]`) capturing runtime software stages within a Realm.
- **RPV (Realm Personalization Value)**: A 64-byte tenant-provided value embedded into the Realm's cryptographic identity at creation.
- **PAK (Platform Attestation Key)**: The asymmetric private signing key derived from the Hardware Unique Key (HUK) used to sign Platform Attestation Tokens.
- **RAK (Realm Attestation Key)**: The ephemeral asymmetric signing key generated by the RMM used to sign Realm Attestation Tokens.

---

## 12.2 Master Acronym Index

| Acronym | Expansion | Architectural Domain |
| :--- | :--- | :--- |
| **ABI** | Application Binary Interface | Software Interfaces |
| **ACE** | AXI Coherency Extensions | AMBA Interconnect |
| **AES-XTS** | Advanced Encryption Standard - XEX Tweakable Block Cipher with Ciphertext Stealing | Memory Cryptography |
| **ATC** | Address Translation Cache | PCIe Peripheral Hardware |
| **ATS** | Address Translation Services | PCIe / SMMU Subsystem |
| **BTI** | Branch Target Identification (`FEAT_BTI`) | Hardware Exploit Mitigation |
| **BRBE** | Branch Record Buffer Extension (`FEAT_BRBE`) | Processor Profiling |
| **CCA** | Confidential Compute Architecture | Arm Platform Architecture |
| **CDA** | Coherent Device Assignment | RME System Architecture |
| **CHI** | Coherent Hub Interface | AMBA Mesh Fabric |
| **CXL** | Compute Express Link | High-Speed Interconnect |
| **DIT** | Data Independent Timing (`FEAT_DIT`) | Cryptographic Hardening |
| **DPT** | Device Protection Table | System MMU Architecture |
| **EAT** | Entity Attestation Token | Cryptographic Attestation |
| **EL** | Exception Level (`EL0`, `EL1`, `EL2`, `EL3`) | Processor Architecture |
| **GDI** | Granule Data Isolation | RME System Properties |
| **GIC** | Generic Interrupt Controller (GICv3, GICv4) | Processor Architecture |
| **GPC** | Granule Protection Check | RME Core Hardware |
| **GPF** | Granule Protection Fault | Exception Architecture |
| **GPT** | Granule Protection Table | Memory Architecture |
| **HES** | Hardware Enforced Security | System Security Model |
| **HUK** | Hardware Unique Key | Root of Trust |
| **IDE** | Integrity and Data Encryption | PCI-SIG Standard |
| **IPA** | Intermediate Physical Address | Two-Stage MMU Virtualization |
| **KVM** | Kernel-based Virtual Machine | Host Virtualization |
| **MEC** | Memory Encryption Contexts | RME Hardware Extension |
| **MECID** | Memory Encryption Context Identifier | Memory Architecture |
| **MMU** | Memory Management Unit | Processor Architecture |
| **MPE** | Memory Protection Engine | DRAM Controller Hardware |
| **MPAM** | Memory System Resource Partitioning and Monitoring | System Quality of Service |
| **OTP** | One-Time Programmable (eFuses) | Silicon Hardware Security |
| **PAK** | Platform Attestation Key | Cryptographic Attestation |
| **PAS** | Physical Address Space | Memory Architecture |
| **PE** | Processing Element (Core) | Armv9-A Core Architecture |
| **PSCI** | Power State Coordination Interface | Arm Firmware Standards |
| **RAK** | Realm Attestation Key | Cryptographic Attestation |
| **RAS** | Reliability, Availability, and Serviceability | System Fault Architecture |
| **RCiEP** | Root Complex Integrated Endpoint | PCIe Architecture |
| **REC** | Realm Execution Context | Arm CCA Virtualization |
| **RHI** | Realm Host Interface | Paravirtualized Software |
| **RIM** | Realm Initial Measurement | Attestation Architecture |
| **RMI** | Realm Management Interface | CCA Software Stack |
| **RMM** | Realm Management Monitor | CCA Privileged Firmware |
| **RMMD** | RMM Dispatcher (in TF-A EL3) | EL3 Monitor Firmware |
| **RME** | Realm Management Extension | Arm Architecture Extension |
| **RoT** | Root of Trust | System Hardware Security |
| **ROTPK** | Root of Trust Public Key | Platform PKI |
| **RPV** | Realm Personalization Value | Attestation Architecture |
| **RSI** | Realm Services Interface | Realm Guest Software Stack |
| **RTT** | Realm Translation Table | Stage-2 Memory Management |
| **SCP** | System Control Processor | Platform Management Subsystem |
| **SMC** | Secure Monitor Call | Arm Calling Conventions |
| **SMMU** | System Memory Management Unit | System I/O Virtualization |
| **SPDM** | Security Protocol and Data Model | DMTF Peripheral Security |
| **SPE** | Statistical Profiling Extension (`FEAT_SPE`) | Processor Profiling |
| **TCB** | Trusted Computing Base | Platform Security Architecture |
| **TDISP** | Trusted Device Interface Security Protocol | PCI-SIG Security Protocol |
| **TF-A** | Trusted Firmware-A | Arm Open-Source Firmware |
| **TF-RMM**| Trusted Firmware Realm Management Monitor | Arm Open-Source Firmware |
| **TLB** | Translation Lookaside Buffer | Core Memory Management |
| **VDM** | Vendor-Defined Message | PCIe Messaging Protocol |
| **VMM** | Virtual Machine Monitor (Hypervisor) | Virtualization Stack |

---
"""

# Read all modules 1 to 11
modules_text = []
for i in range(1, 12):
    filename = os.path.join(MODULES_DIR, f"module{i}.md")
    with open(filename, "r") as f:
        modules_text.append(f.read().strip())

# Combine into master document
master_content = preface.strip() + "\n\n"
for mod in modules_text:
    master_content += mod + "\n\n---\n\n"
master_content += module12_content.strip() + "\n"

with open(OUTPUT_FILE, "w") as f:
    f.write(master_content)

print(f"Master guide successfully generated at: {OUTPUT_FILE}")

# Calculate statistics
words = len(re.findall(r'\b\w+\b', master_content))
lines = len(master_content.splitlines())
chars = len(master_content)
pages_approx = words / 425

print(f"Total Lines: {lines}")
print(f"Total Words: {words}")
print(f"Total Characters: {chars}")
print(f"Estimated Standard Technical Pages (~425 words/page): {pages_approx:.1f} pages")
