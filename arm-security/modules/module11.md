# Module 11: Comparative Analysis, System Register & Command Quick Reference

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
