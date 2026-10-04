#!/usr/bin/env python3
"""
Generator for Modules 10 to 11 of the ARM Security Architecture Reference Guide.
"""

import os

os.makedirs("arm-security/modules", exist_ok=True)

module10_content = """# Module 10: Security Lifecycle, Debug, RAS & Microarchitectural Side-Channel Hardening

## 10.1 System Security Lifecycle Management

The security posture of an Arm CCA platform evolves across distinct lifecycle states governed by hardware non-volatile OTP fuses (as defined in **ARM-DEN-0096** and **ARM-DEN-0129**). 

The platform hardware root of trust enforces strict monotonic transitions between these lifecycle states, preventing regression to less secure factory modes.

```mermaid
stateDiagram-v2
    [*] --> CHIP_MANUFACTURING: Silicon Die Fabrication
    
    CHIP_MANUFACTURING --> DEVICE_MANUFACTURING: HUK Fused & Tested
    DEVICE_MANUFACTURING --> NORMAL_SECURED: OEM Root Keys Fused & Locked
    
    state NORMAL_SECURED {
        [*] --> Runtime_Production
        Runtime_Production --> Attestation_Operational: Pak Active
    }
    
    NORMAL_SECURED --> SECURE_DEBUG: Cryptographic Auth Token Presented
    SECURE_DEBUG --> NORMAL_SECURED: Debug Session Ended & Reset
    
    NORMAL_SECURED --> RETURN_TO_FACTORY: RMA Authorized (HUK Scrubbed)
    RETURN_TO_FACTORY --> DECOMMISSIONED: Permanent Kill Fuses Blown
    NORMAL_SECURED --> DECOMMISSIONED: Permanent Kill Fuses Blown
    
    DECOMMISSIONED --> [*]: Silicon Permanently Inoperable
```

### Lifecycle State Specifications
1. **`CHIP_MANUFACTURING`**:
   - Initial state during semiconductor fabrication.
   - JTAG interfaces are open. Test patterns verify logic integrity.
   - The Hardware Unique Key (HUK) is injected into OTP fuses and write-locked.
2. **`DEVICE_MANUFACTURING`**:
   - OEM / ODM board assembly phase.
   - OEM Root of Trust Public Keys (ROTPK) and anti-rollback monotonic counters are burned into platform fuses.
3. **`NORMAL_SECURED` (Production Deployment)**:
   - Standard operational state in cloud data centers.
   - External hardware debug (JTAG/Trace) into Root, Secure, and Realm domains is **permanently disabled in hardware**.
   - Attestation services report `PSA_LIFECYCLE_SECURED`.
   - Firmware anti-rollback checks are strictly enforced on every boot.
4. **`SECURE_DEBUG`**:
   - Authorized maintenance state for field failure analysis.
   - Requires presenting a cryptographically signed debug certificate signed by the platform RoT private key.
   - **Critical Security Invariant**: When transitioning to `SECURE_DEBUG`, the hardware automatically initiates a full system cold reset, purging all DRAM contents, clearing MPE key tables, and scrubbing on-chip caches before debug probes are enabled.
5. **`RETURN_TO_FACTORY` (RMA) & `DECOMMISSIONED`**:
   - For defective silicon return or end-of-life destruction.
   - Monotonic kill fuses are blown, permanently destroying on-chip key derivation ladders and disabling the PE.

---

## 10.2 Debug, Trace & Profiling Controls in RME

Traditional hardware debugging facilities (such as JTAG debuggers, trace buffers, and performance monitors) represent potent threat vectors in multi-tenant environments. A rogue cloud administrator with physical access could attach a hardware probe to capture live processor registers.

Arm RME introduces fine-grained, hardware-enforced **Debug Isolation Boundaries**:

```mermaid
graph TD
    subgraph Debug_Controls["RME Hardware Debug & Profiling Isolation Grid"]
        direction TB
        
        subgraph Probing_Sources["Debug & Profiling Sources"]
            JTAG["External JTAG Probe / Hardware In-Circuit Emulator"]
            SPE["Statistical Profiling Extension (FEAT_SPE)"]
            BRBE["Branch Record Buffer Extension (FEAT_BRBE)"]
            PMU["Performance Monitor Unit (FEAT_PMUv3)"]
        end
        
        subgraph Hardware_Gate["RME Security State Filtering Gate"]
            AuthCheck{"Is Security State == Realm or Root?"}
        end
        
        subgraph Enforcement["Enforcement Actions"]
            JTAG_Block["JTAG Signal Trapped / Register Bus Disabled"]
            SPE_Mute["SPE Sampling Muted (Drops PC Samples)"]
            BRBE_Purge["BRBE Purges History / Inhibits Branch Capture"]
            PMU_Filter["PMU Ineligible Cycles Excluded from Counters"]
        end
        
        Probing_Sources --> Hardware_Gate
        Hardware_Gate -->|YES: Realm / Root| Enforcement
        Hardware_Gate -->|NO: Non-Secure| Allowed["Standard Profiling / Debug Permitted"]
    end
    
    style Debug_Controls fill:#f9f9f9,stroke:#34495e,stroke-width:2px;
    style Probing_Sources fill:#ebf5fb,stroke:#2980b9,stroke-width:2px;
    style Enforcement fill:#fadbd8,stroke:#e74c3c,stroke-width:2px;
    style Allowed fill:#d4efdf,stroke:#27ae60,stroke-width:2px;
```

### Architectural Controls
1. **External Hardware Debug Authentication**:
   - Debug registers in the core PE are gated by authentication signals (`DBGEN`, `NIDEN`, `SPIDEN`, `SPNIDEN`, and RME-specific `RLMDEN` / Realm Debug Enable).
   - In production lifecycle states, `RLMDEN` is tied low, preventing external hardware debug probes from halting, inspecting, or stepping Realm execution.
2. **Statistical Profiling Extension (SPE - `FEAT_SPE`)**:
   - SPE periodically samples instruction execution profiles (recording PCs, branch behaviors, and data addresses).
   - In RME, whenever the PE executes in Realm or Root state, SPE sampling is automatically muted by hardware. No trace packets containing Realm virtual or physical addresses are written to memory buffers.
3. **Branch Record Buffer Extension (BRBE - `FEAT_BRBE`)**:
   - BRBE records recent branch execution paths.
   - To prevent hypervisors from inspecting branch histories to infer secret cryptographic branches in Realms, BRBE automatically clears the branch history buffer upon taking an exception from Realm state to `R-EL2` or `NS-EL2`.

---

## 10.3 Reliability, Availability & Serviceability (RAS) Architecture

In enterprise server architectures, the **Reliability, Availability, and Serviceability (RAS)** framework detects, records, and reports hardware memory faults (e.g., ECC single-bit errors, multi-bit uncorrectable faults, and interconnect parity errors).

### The Confidential Data Leakage Risk in RAS
When a hardware fault occurs, the processor or memory controller captures fault details into **RAS Error Records** (`ERR<n>STATUS`, `ERR<n>ADDR`, `ERR<n>MISC`):
- `ERR<n>ADDR` captures the physical address where the memory failure occurred.
- `ERR<n>MISC` often captures raw data bits or syndrome signatures from the failing memory burst.
- If an uncorrectable DRAM error occurs inside a Realm memory granule, and the hardware records the fault into a standard Non-Secure RAS record, the host hypervisor could inspect `ERR<n>MISC` to read private tenant plaintext!

```mermaid
sequenceDiagram
    autonumber
    participant DRAM as DRAM / MPE Controller
    participant RAS as Hardware RAS Engine
    participant GPC as Granule Protection Checker
    participant Host as Host OS / Hypervisor

    DRAM->>RAS: ECC Uncorrectable Error Detected at Physical Address PA_X
    RAS->>GPC: Queries PAS of PA_X
    GPC-->>RAS: Returns PAS == REALM
    
    Note over RAS: Scrubbing Phase (Mandated by ARM-DEN-0129)
    RAS->>RAS: Zeros out ERR<n>MISC (Scrubs confidential data syndrome)
    RAS->>RAS: Masks lower address bits in ERR<n>ADDR (reports only Granule Base)
    RAS->>RAS: Sets ERR<n>STATUS.V = 1 (Valid) & Sets Poison Bit
    
    RAS->>Host: Signals RAS Error Interrupt to Host (NS-EL2)
    Host->>RAS: Reads Sanitized Error Record
    Host->>Host: Hypervisor offline-migrates or isolates physical page safely
```

### RME Architectural RAS Invariants (ARM-DEN-0129 Chapter B4)
1. **Confidential Data Scrubbing**:
   - Whenever an error record is associated with a physical address whose GPI is `Realm` or `Root`, the hardware **must purge any potentially confidential data** from `ERR<n>MISC` before asserting error syndrome registers.
2. **Address Range Masking**:
   - `ERR<n>ADDR` is masked to report only the base granule address, preventing microarchitectural timing introspection of specific cache line offsets.
3. **Error Poisoning**:
   - Rather than returning uncorrectable stale data, the memory controller marks the cache line as **Poisoned**. Any subsequent read by the Realm triggers a synchronous Data Abort with poison syndrome, allowing the Realm kernel to terminate the affected process without compromising system integrity.

---

## 10.4 Microarchitectural Side-Channel & Fault Injection Mitigations

Modern processors are susceptible to microarchitectural timing side channels (such as cache eviction timing, branch predictor poisoning, and transient execution) as well as physical fault injection attacks (clock/voltage glitching).

Arm CCA integrates defense-in-depth mitigations:

| Attack Vector | Vulnerability Mechanism | Arm CCA Hardware Mitigation |
| :--- | :--- | :--- |
| **Spectre-v2 / BTI** | Malicious hypervisor trains branch target predictors at `NS-EL2` to steer speculative execution in Realm guest at `R-EL1`. | **Branch Target Identification (`FEAT_BTI`)** & hardware branch predictor context invalidation upon world switch (`FEAT_CSV2`). |
| **Meltdown / Rogue Load**| Speculative read of unauthorized physical memory before permission checks retire. | **Granule Protection Check (GPC)** is wired directly into load/store speculative replay units, terminating speculative execution of cross-PAS loads immediately. |
| **Microarchitectural Timing** | Hypervisor reads high-resolution Performance Monitor Unit (`PMU`) cycle counters before and after Realm execution to infer cache hit/miss behavior. | **PMU Counter Filtering**: System PMU registers can be configured by RMM to inhibit cycle and event counting during Realm execution slices. |
| **Cryptographic Timing** | Secret-dependent execution time in cryptographic loops (e.g., modular exponentiation, AES S-boxes). | **Data Independent Timing (`FEAT_DIT`)**: When `PSTATE.DIT` is set, instruction execution time on PEs is guaranteed to be completely independent of input data values. |
| **Clock / Voltage Glitching** | Physical attacker manipulates SoC power supply rails to induce bit flips in GPC logic or bypass address checking. | **Dual-Rail Verification & Redundant Comparators**: The RME specification mandates fault-tolerant redundant logic for GPT walkers and PAS comparison pipelines. |

---
"""

module11_content = """# Module 11: Comparative Analysis, System Register & Command Quick Reference

## 11.1 Industry Comparative Analysis: Arm CCA vs. x86 Technologies

Arm Confidential Compute Architecture represents a modern, clean-slate design that resolves many structural compromises present in earlier confidential computing architectures.

| Architectural Dimension | Arm CCA (Armv9-A / RME) | Intel TDX (Trust Domain Extensions) | AMD SEV-SNP (Secure Encrypted Virtualization) | Arm TrustZone (Legacy) |
| :--- | :--- | :--- | :--- | :--- |
| **Security Domains** | **4 Distinct States**:<br/>Root, Realm, Secure, Non-Secure | **2 Major Domains**:<br/>Legacy VMX Root/Non-Root & SEAM | **2 Domains**:<br/>Hypervisor vs Encrypted Guest Contexts | **2 Worlds**:<br/>Secure vs Non-Secure |
| **Root Supervisor** | **TF-RMM** at `R-EL2` (Open Source, standard C, minimal footprint) | **Intel TDX Module** in SEAM (Signed by Intel, closed microcode/firmware) | **AMD Secure Processor (ASP)** firmware (Off-core ARM Cortex-A5 core) | **Secure Monitor** at `EL3` (TF-A) |
| **Memory Isolation Mechanism** | **Granule Protection Checks (GPC)** via two-level hardware GPT walker | **Secure EPT** & Physical Address P-bit filtering | **Reverse Map Table (RMP)** checked by hardware nested page walker | **TZASC / TZC-400** (Coarse static memory carveouts) |
| **Granularity** | **4KB, 16KB, or 64KB** dynamic per-granule assignment | **4KB, 2MB, 1GB** page table assignment | **4KB, 2MB** dynamic page assignment | Coarse memory regions (Megabytes/Gigabytes) |
| **Attestation Architecture** | **Dual-Token Model**:<br/>Platform Token (PAK) + Realm Token (RAK) | **Quote Generation** via Intel SGX Quoting Enclave | **SNP Attestation Report** signed by VCEK / ASP | Single Platform Attestation via PSA / TEE |
| **Standard Peripheral I/O** | **RME-DA** via PCIe IDE + TDISP + SMMU DPT | **TDISP / IDE** via Intel VT-d | **TDISP / IDE** via AMD IOMMU | Direct MMIO or static TrustZone peripheral assignment |
| **Ecosystem Governance** | **Open Industry Standard** (Linaro, TrustedFirmware.org, Arm Architecture Specs) | **Proprietary Intel Specification** | **Proprietary AMD Specification** | **Proprietary Arm / GlobalPlatform** |

---

## 11.2 Master System Register Reference

The following table summarizes the primary architectural system registers introduced or expanded for Arm CCA and RME:

```
+----------------------------------------------------------------------------------------------------+
|                                    MASTER SYSTEM REGISTER REFERENCE                                |
+------------------+-------+--------+----------------------------------------------------------------+
| Register Name    | Level | Access | Architectural Purpose & Key Bitfields                          |
+------------------+-------+--------+----------------------------------------------------------------+
| GPCCR_EL3        | EL3   | RW     | Granule Protection Check Configuration Register                |
|                  |       |        | • Bit [0] GPC: Global Granule Protection Check Enable          |
|                  |       |        | • Bits [3:2] PGS: Physical Granule Size (4KB, 16KB, 64KB)      |
|                  |       |        | • Bits [7:4] L0GPTSZ: Level 0 GPT coverage block size          |
|                  |       |        | • Bits [11:8] PPS: Protected Physical address Size             |
+------------------+-------+--------+----------------------------------------------------------------+
| GPTBR_EL3        | EL3   | RW     | Granule Protection Table Base Register                         |
|                  |       |        | • Bits [51:12] BADDR: Base Physical Address of Level 0 GPT in  |
|                  |       |        |   Root Physical Address Space                                  |
+------------------+-------+--------+----------------------------------------------------------------+
| SCR_EL3          | EL3   | RW     | Secure Configuration Register                                  |
|                  |       |        | • Bit [0] NS: Non-Secure Execution State bit                   |
|                  |       |        | • Bit [42] NSE: Non-Secure Extension (Selects Realm State)    |
|                  |       |        | • Bit [43] TRND: Trap Random Number Generator                  |
+------------------+-------+--------+----------------------------------------------------------------+
| MFAR_EL3         | EL3   | RW     | Physical Fault Address Register                                |
|                  |       |        | • Captures target Physical Address on Granule Protection Fault |
+------------------+-------+--------+----------------------------------------------------------------+
| ESR_ELx          | EL1-3 | RO     | Exception Syndrome Register                                    |
|                  |       |        | • Bits [31:26] EC: Exception Class                             |
|                  |       |        | • Bits [5:0] IFSC/DFSC: Data/Instruction Fault Status Codes    |
|                  |       |        |   0b011100: GPF on L0 GPT walk                                 |
|                  |       |        |   0b011101: GPF on L1 GPT walk                                 |
|                  |       |        |   0b011110: GPF on primary physical access                     |
+------------------+-------+--------+----------------------------------------------------------------+
| VTCR_EL2         | EL2   | RW     | Virtualization Translation Control Register (Realm EL2)        |
|                  |       |        | • Bits [5:0] T0SZ: Realm Stage-2 IPA address space size        |
|                  |       |        | • Bits [30:28] PS: Physical Address Size                       |
+------------------+-------+--------+----------------------------------------------------------------+
| VTTBR_EL2        | EL2   | RW     | Virtualization Translation Table Base Register                 |
|                  |       |        | • Bits [47:1] BADDR: Base PA of Level 0/1 RTT in Realm PAS     |
|                  |       |        | • Bits [63:48] VMID: Virtual Machine Identifier                |
+------------------+-------+--------+----------------------------------------------------------------+
| ICH_LR<n>_EL2    | EL2   | RW     | Interrupt Controller Hyp Active Priorities / List Registers    |
|                  |       |        | • Used by RMM to inject Virtual Interrupts into Realm vCPUs    |
+------------------+-------+--------+----------------------------------------------------------------+
```

---

## 11.3 Complete RMI & RSI Command Cheat-Sheet

### Realm Management Interface (RMI) Commands (Dispatched from Host `NS-EL2` to RMM via EL3)

| Command Function ID | Invocable State | Critical Arguments | Return Values |
| :--- | :--- | :--- | :--- |
| `RMI_VERSION` | Any | `req_version` | `ret_version`, `status` |
| `RMI_REALM_CREATE` | Pre-Boot | `rd_pa`, `params_pa` | `status` (`RMI_SUCCESS`, `RMI_ERROR_INPUT`) |
| `RMI_REALM_ACTIVATE` | Pre-Boot | `rd_pa` | `status` |
| `RMI_REALM_DESTROY` | Halting | `rd_pa` | `status` |
| `RMI_REC_CREATE` | Pre-Boot | `rd_pa`, `rec_pa`, `params_pa` | `status` |
| `RMI_REC_DESTROY` | Teardown | `rec_pa` | `status` |
| `RMI_REC_ENTER` | Runtime | `rec_pa`, `run_pa` | `status`, populated `rec_run` buffer |
| `RMI_DATA_CREATE` | Pre-Boot | `rd_pa`, `data_pa`, `ipa`, `src_pa` | `status` |
| `RMI_DATA_DESTROY` | Teardown | `rd_pa`, `data_pa` | `status` |
| `RMI_RTT_CREATE` | Runtime | `rd_pa`, `rtt_pa`, `ipa`, `level` | `status` |
| `RMI_RTT_DESTROY` | Runtime | `rd_pa`, `rtt_pa`, `ipa`, `level` | `status` |
| `RMI_RTT_MAP_UNPROTECTED` | Runtime | `rd_pa`, `ipa` | `status` |
| `RMI_PSCI_COMPLETE` | Runtime | `calling_rec`, `target_rec` | `status` |

### Realm Services Interface (RSI) Commands (Dispatched from Realm `R-EL1` to RMM `R-EL2`)

| Command Function ID | Invocable State | Critical Arguments | Return Values |
| :--- | :--- | :--- | :--- |
| `RSI_ABI_VERSION` | Runtime | `req_version` | `ret_version` |
| `RSI_REALM_CONFIG` | Boot/Runtime | `config_pa` | `status`, populated config block |
| `RSI_IPA_STATE_SET` | Runtime | `start_ipa`, `size`, `ripas`, `flags` | `status`, `top_ipa` |
| `RSI_IPA_STATE_GET` | Runtime | `ipa` | `status`, `current_ripas` |
| `RSI_ATTESTATION_TOKEN_INIT` | Runtime | `challenge[64]`, `buf_pa` | `status`, `token_len` |
| `RSI_ATTESTATION_TOKEN_CONTINUE` | Runtime | `buf_pa`, `offset` | `status`, `written_len` |
| `RSI_MEASUREMENT_READ` | Runtime | `index`, `buf_pa` | `status`, measurement hash |
| `RSI_MEASUREMENT_EXTEND` | Runtime | `index`, `buf_pa`, `size` | `status` |
| `RSI_HOST_CALL` | Runtime | `params_pa` | `status` |

---

## 11.4 Architectural Implementation Checklist & Golden Invariants

For system architects, firmware developers, and hypervisor engineers implementing Arm CCA, the following **Seven Golden Invariants** must be preserved at all times:

1. **The Inviolability of Root PAS**:
   - The Root Physical Address Space (containing GPTs, EL3 stacks, and RoT keys) must never be mapped as writable by any translation regime other than Root EL3.
2. **Atomic Transition Scrubbing**:
   - No memory granule may transition from Realm PAS to Non-Secure PAS without being completely zeroized and cleaned/invalidated from all CPU and system caches (`DC CIPAPA`).
3. **No Speculative Leakage Across Security Boundaries**:
   - Microarchitectural speculation mechanisms (branch predictors, data caches, speculative load queues) must strictly honor GPC checks before committing results or updating microarchitectural state observable by lower-privilege states.
4. **Permanent Measurement Locking**:
   - Upon execution of `RMI_REALM_ACTIVATE`, the Realm Initial Measurement (RIM) register is irrevocably locked in hardware/firmware. No subsequent memory page can be inserted into the Realm's initial identity.
5. **Untrusted Host Principle**:
   - Every input parameter, memory pointer, interrupt injection request, and exit structure received from the Host Hypervisor at `NS-EL2` must be treated as potentially malicious and strictly bounds-checked by the RMM.
6. **Encrypted Inter-Socket Coherency**:
   - Coherent inter-chip mesh transactions carrying Realm PAS or Root PAS memory accesses across board traces must implement authenticated link encryption (e.g., PCIe IDE / MACsec) with replay prevention.
7. **Complete Teardown Invariant**:
   - A Realm Descriptor (`RD`) can never be destroyed or released while any subordinate memory granule, RTT node, or REC remains mapped to that Realm.

---
"""

with open("arm-security/modules/module10.md", "w") as f:
    f.write(module10_content.strip() + "\n")

with open("arm-security/modules/module11.md", "w") as f:
    f.write(module11_content.strip() + "\n")

print("Generated Modules 10 and 11 successfully.")
