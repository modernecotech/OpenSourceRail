# OpenSourceRail — hardware reference designs

Physical host classes for the software stack. Reference designs
scoped in [RFC 0007](../docs/rfcs/0007-hardware-reference-designs.md);
schematics and board-release artifacts land under each subdirectory as
the RFC 0007 rollout matures.

**Two-vendor palette — Raspberry Pi and Radxa only.** Every class
below picks from those two vendors. No NXP, ST, MilkV, StarFive,
Rockchip-direct, or bespoke silicon. Rationale in
[RFC 0007 §3 constraint 3](../docs/rfcs/0007-hardware-reference-designs.md#3-common-platform-choices).

| Class | Role | SoC baseline | RFC 0007 §  |
|---|---|---|---|
| [`t-ecu-s/`](t-ecu-s/) | Train safety kernel (SIL-4) | 2 × Raspberry Pi RP2350 (2oo2) + Raspberry Pi CM5 app processor | §4 |
| [`t-ecu-a/`](t-ecu-a/) | Train application (SIL-2/-0) | Raspberry Pi CM5 (Radxa CM5 drop-in) | §5 |
| [`t-obs/`](t-obs/) | Train obstacle detection (SIL-4 interface) | 2 × Raspberry Pi RP2350 (2oo2) + Raspberry Pi CM5 sensor pre-processor | RFC 0015 §5 |
| [`w-sbc/`](w-sbc/) | Wayside (SIL-4 / SIL-2) | Radxa CM5 (RK3588S, industrial temp) | §6 |
| [`s-sbc/`](s-sbc/) | Station / depot (SIL-0) | Raspberry Pi CM5 + commodity carrier | §7 |

`O-SRV` (ops server) is commodity hardware and has no reference
design in tree.

## Layout

Each class subdirectory has the same shape:

```
<class>/
├── README.md         class overview, SoC rationale, peripherals list
├── schematics/       KiCad 8 projects (*.kicad_sch, *.kicad_pcb), once drawn
├── gerbers/          Fab outputs packaged as .zip per board revision
└── bom/              BOM.csv with Mouser / Digi-Key / LCSC lines
```

Current status:

| Class | Board-level spec | KiCad / gerbers / board BOM |
|---|---|---|
| `t-ecu-s` | Complete `schematics/v2-spec/` package with block diagram, power budget, connector tables, pinouts, and safety nets | Pending release package |
| `t-ecu-a` | `schematics/v2-spec/` overview and block diagram | Pending release package |
| `t-obs` | Complete `schematics/v2-spec/` package aligned with the T-ECU/S safety pattern | Pending release package |
| `w-sbc` | `schematics/v2-spec/` overview and block diagram | Pending release package |
| `s-sbc` | `schematics/v2-spec/` overview | Pending release package |

The release gates for KiCad, gerbers, board BOMs, bring-up logs, and
safety bench records are tracked in
[`release-checklist.md`](release-checklist.md). Until a host class
meets that checklist it is a board-level specification, not released
fabrication hardware.

For trainset quantities and the boundary between hardware docs,
mechanical CAD envelopes, and the rolling-stock procurement BOM, see
[`rolling-stock-integration.md`](rolling-stock-integration.md).

## Licensing

Hardware designs (schematics, layouts, gerbers, BOM) are licensed
under **CERN-OHL-S v2**. Firmware stays under **Apache-2.0**
(inherited from the Rust crates). Documentation under
**CC-BY-SA 4.0**. See [ARCHITECTURE.md §9](../docs/ARCHITECTURE.md#9-roadmap)
for the project-wide licensing rationale.

## Contributing

High-leverage contributions are KiCad capture, board DFM review,
procurement BOM completion, and DIY build feedback against
[`diy-assembly/`](diy-assembly/).
