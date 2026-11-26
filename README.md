# 4-Port Non-Blocking L2 Ethernet Switch (VOQ & iSLIP)

Industrial-grade 4-Port Gigabit Ethernet Layer-2 Store-and-Forward Switch implemented in **Verilog-2001**, featuring **Virtual Output Queuing (VOQ)**, two-dimensional **iSLIP scheduling**, dynamic MAC learning with aging, and AXI4-Stream interfaces.

---

## Architecture Highlights
- **Interface:** Port-level 8-bit AXI4-Stream (`tdata[7:0]`, `tvalid`, `tready`, `tlast`, `tuser`) operating at 125 MHz (1 Gbps line-rate per port, 4 Gbps aggregate non-blocking capacity).
- **Queuing & HoL Elimination:** 4 Virtual Output Queues per ingress port (16 BRAM Packet FIFOs total), completely eliminating Head-of-Line (HoL) blocking and achieving 100% throughput compared to the ~58.6% limit of single-FIFO switches.
- **2D Scheduler:** 4x4 Request-Grant-Accept two-dimensional round-robin iSLIP arbiter with desynchronization property.
- **Packet-Level Locking:** Scheduler grant/accept match is locked until `tlast` is acknowledged, preventing frame interleaving and byte corruption.
- **Store-and-Forward:** Frames are committed to queue only after full IEEE 802.3 CRC32 verification and length checking (64B min, 1518B max). Corrupted frames trigger write pointer rollback.
- **MAC Engine:** Dynamic source learning, destination lookup, non-reflection flooding (`(~(1 << ingress_port)) & 4'b1111`), and aging timer.
- **Timing & Synthesis:** Skid Buffers (2-stage register slices) on all interfaces to eliminate combinational loops; 100% synthesizable in Yosys and Vivado with zero latches.

---

## Repository Structure

```
.
├── rtl/                        # Verilog-2001 Synthesizable RTL Modules
│   ├── axis_skid_buffer.v      # Fully registered AXI4-Stream Register Slice (0 bubble cycles)
│   └── crc_func.vh             # 8-bit parallel IEEE 802.3 CRC32 matrix equations
├── tb/                         # Self-checking Testbenches
│   └── tb_axis_skid_buffer.v   # Skid buffer verification & random fuzzing testbench
├── docs/                       # Specifications and Architecture Documents
│   ├── L2_Ethernet_Switch_Technical_Architecture_Spec.pdf
│   └── generate_pdf.py         # ReportLab specification generator
└── README.md
```

---

## Development Roadmap & Status

| Phase | Module | Description | Status |
|---|---|---|---|
| **Phase 1** | `axis_skid_buffer.v` | Decouples ready/valid, breaks combinational loops | ✅ Completed |
| **Phase 1** | `crc32_checker.v` | 8-bit parallel Ethernet FCS & 0xDEBB20E3 verification | 🔄 In Progress |
| **Phase 1** | `packet_parser.v` | Ethernet header FSM, Runt (<64B) & Oversize (>1518B) drops | ⏳ Pending |
| **Phase 2** | `packet_fifo.v` & `voq_block.v` | BRAM store-and-forward FIFO with rollback & 16-VOQ matrix | ⏳ Pending |
| **Phase 3** | `mac_table.v` | Dynamic source learning, non-reflection flooding & aging | ⏳ Pending |
| **Phase 4** | `islip_scheduler_4x4.v` & `crossbar_4x4.v` | 2D Request-Grant-Accept arbiter with packet locking & 4x4 crossbar | ⏳ Pending |
| **Phase 5** | `stats_collector.v` & `switch_top.v` | Hardware counters & Top-level integration | ⏳ Pending |
| **Phase 6** | Cocotb / Scapy Framework | Python-based end-to-end traffic injection, `.pcap` capture & Throughput graphs | ⏳ Pending |

---

## Documentation
A full technical architecture and design specification is available in [`docs/L2_Ethernet_Switch_Technical_Architecture_Spec.pdf`](docs/L2_Ethernet_Switch_Technical_Architecture_Spec.pdf).
