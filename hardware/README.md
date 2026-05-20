# OpenSourceRail — hardware reference designs

Physical host classes for the software stack. Reference designs
scoped in [RFC 0007](../docs/rfcs/0007-hardware-reference-designs.md);
schematics land under each subdirectory as the v1 → v4 rollout
lands.

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

Until the v2 rollout of RFC 0007, each `schematics/` / `gerbers/` /
`bom/` directory is empty apart from a `.gitkeep` placeholder.

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

The hardware working group is not yet formed — contributions welcome
once RFC 0007 is ratified. Before then, issues with specific
disagreements on RFC 0007's class choices (SoC, peripherals, BOM
envelope) are the highest-leverage input.
