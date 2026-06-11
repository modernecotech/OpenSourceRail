# OpenSourceRail — hardware reference designs

Physical host classes for the software stack. Reference designs
scoped in [RFC 0007](../docs/rfcs/0007-hardware-reference-designs.md);
schematics and board-release artifacts land under each subdirectory as
the RFC 0007 rollout matures.

Hardware has two valid release tracks:

1. **Pilot / DIY integration track.** RFC 0019 assembles commodity
   SBCs, Pi Pico 2 boards, sensor modules, HATs, relays, power
   supplies, terminal blocks, DIN-rail enclosures, and prepared
   SD-card images. No KiCad or gerbers are required when the build
   uses only COTS modules. The release evidence is the controlled
   integration pack: exact SKUs, wiring/harness maps, connector maps,
   enclosure drawings, power and thermal margins, firmware images,
   self-test output, and bench records.
2. **Custom-board fabrication track.** RFC 0007 board-level specs can
   be captured into KiCad when a deployment needs OSR-specific carrier
   boards, power conditioning, safety I/O, or sensor-interface boards.
   That track needs KiCad, gerbers, board BOMs, DFM/DFT review,
   assembly drawings, and board bring-up evidence.

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
├── diy-assembly/     COTS/SBC pilot assembly notes per RFC 0019
├── schematics/       board-level specs; KiCad projects once custom boards are drawn
├── gerbers/          fab outputs for custom-board revisions
└── bom/              COTS integration BOMs or board BOMs, depending on release track
```

Current status:

| Class | Pilot / COTS integration | Custom-board package |
|---|---|---|
| `t-ecu-s` | `diy-assembly/` present; build evidence pending | Complete `schematics/v2-spec/` package; KiCad / gerbers / board BOM pending |
| `t-ecu-a` | `diy-assembly/` present; build evidence pending | `schematics/v2-spec/` overview and block diagram; KiCad / gerbers / board BOM pending |
| `t-obs` | `diy-assembly/` present; build evidence pending | Complete `schematics/v2-spec/` package; KiCad / gerbers / board BOM pending |
| `w-sbc` | `diy-assembly/` present; build evidence pending | `schematics/v2-spec/` overview and block diagram; KiCad / gerbers / board BOM pending |
| `s-sbc` | `diy-assembly/` present; build evidence pending | `schematics/v2-spec/` overview; custom board usually unnecessary |

The release gates for both tracks are tracked in
[`release-checklist.md`](release-checklist.md). Until a host class
meets the pilot track it is a design concept, not integration-qualified
pilot hardware. Until it meets the custom-board track it is not released
fabrication hardware.

For trainset quantities and the boundary between hardware docs,
mechanical CAD envelopes, and the rolling-stock procurement BOM, see
[`rolling-stock-integration.md`](rolling-stock-integration.md).

## Licensing

Hardware designs (schematics, layouts, gerbers, board BOMs, and
integration drawings) are licensed under **CERN-OHL-S v2**. Firmware
stays under **Apache-2.0**
(inherited from the Rust crates). Documentation under
**CC-BY-SA 4.0**. See [ARCHITECTURE.md §9](../docs/ARCHITECTURE.md#9-roadmap)
for the project-wide licensing rationale.

## Contributing

High-leverage contributions are DIY/COTS build feedback against
[`diy-assembly/`](diy-assembly/), integration BOM completion, wiring
and enclosure review, KiCad capture where custom boards are justified,
and board DFM review for the custom-board track.
