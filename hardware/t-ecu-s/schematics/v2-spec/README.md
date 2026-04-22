# T-ECU/S baseboard v2 — schematic specification

**Status:** v2 spec — PCB designer's input, not KiCad files yet.
**Date:** 2026-04-22
**Parent RFC:** [RFC 0007](../../../../docs/rfcs/0007-hardware-reference-designs.md)
**Follows:** v1 bring-up runbook at
[`docs/hardware/bring-up/t-ecu-s.md`](../../../../docs/hardware/bring-up/t-ecu-s.md)

## Scope

Every signal, connector, power rail, and safety-critical net the
v2 KiCad project needs. A PCB designer can capture the schematic
directly from this doc; no missing information should force
design-time guesswork.

v1 delivered bring-up procedures on dev boards. **v2 is the
first-article custom baseboard.** This doc is the input to the
KiCad schematic capture; the `*.kicad_sch` + `*.kicad_pcb` +
gerber files land once a reviewed schematic is produced from
this spec.

## Contents

| File | Scope |
|---|---|
| [`block-diagram.md`](block-diagram.md) | Top-level block diagram + inter-block nets |
| [`power-budget.md`](power-budget.md) | 24 V input → every rail, with worst-case current per consumer |
| [`pinout-rp2350.md`](pinout-rp2350.md) | Per-RP2350 pin allocation (A-channel + B-channel identical) |
| [`pinout-cm5.md`](pinout-cm5.md) | CM5 SODIMM pinout on the baseboard |
| [`connector-tables.md`](connector-tables.md) | Every external connector (M12, HSD Ethernet, M.2, header) with pin-by-pin function |
| [`safety-nets.md`](safety-nets.md) | The 2oo2 cross-check, the hardware watchdog, the external AND-gate relay stage |

## Board envelope (from v1 spec)

- Dimensions: 160 × 100 mm Eurocard.
- Layers: 4-layer FR-4, 0.15 mm trace/space, 0.3 mm min via.
- Form factor: DIN-rail mount via flanking Phoenix-Contact DIN
  adapters.
- Conformal coated (MG Chemicals 419) post-assembly.
- Connectors: M12 for field I/O on one long edge; HSD-style
  Ethernet on the opposite long edge; M.2 slot on the CM5 side.

## Revision control

The v2 spec is pinned at this commit. Any deviation during
schematic capture is logged in
[`deviations-log.md`](deviations-log.md) (created when first
deviation lands).

Schematic + layout lands under
[`hardware/t-ecu-s/schematics/v2-kicad/`](../) once produced.
Gerbers under [`hardware/t-ecu-s/gerbers/v2-rev-A/`](../../gerbers/).
BOM under [`hardware/t-ecu-s/bom/v2-rev-A.csv`](../../bom/).

## Licensing

This specification is CC-BY-SA 4.0 (inherits from the docs
tree). The downstream KiCad project + gerbers + BOM will be
CERN-OHL-S v2 per [ARCHITECTURE.md §9](../../../../docs/ARCHITECTURE.md#9-roadmap).
