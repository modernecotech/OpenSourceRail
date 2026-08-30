# Hardware Release Checklist

This checklist turns the hardware gap into concrete release gates for
each host class. OSR has two hardware release tracks:

- **Pilot / DIY integration release:** commodity SBCs, Pi Pico 2
  boards, sensor modules, HATs, relay modules, power supplies,
  terminal blocks, and DIN-rail enclosures per
  [RFC 0019](../docs/rfcs/0019-diy-electronics.md). This track does
  not require KiCad or gerbers when no custom PCB is used.
- **Custom-board fabrication release:** OSR-specific carrier, power,
  safety-I/O, or sensor-interface boards per
  [RFC 0007](../docs/rfcs/0007-control-electronics-reference-designs.md). This
  track requires KiCad, gerbers, board BOMs, DFM/DFT review, and board
  bring-up evidence.

## Pilot / DIY Integration Track

| Host class | COTS BOM | Wiring / harness map | Enclosure + mounting | Power / thermal margin | SD image + self-test | Bench / safety evidence |
|---|---|---|---|---|---|---|
| T-ECU/S | Pending freeze | Pending | Pending | Pending | Pending | 2oo2 watchdog, relay-stage, cross-check, and power-fault bench logs |
| T-ECU/A | Pending freeze | Pending | Pending | Pending | Pending | Non-safety host self-test and communications fault-injection logs |
| T-OBS | Pending freeze | Pending | Pending | Pending | Pending | 2oo2 obstacle-clear output, sensor-fault injection, heater/washer tests |
| W-SBC | Pending freeze | Pending | Pending | Pending | Pending | Wayside power, network isolation, intrusion/points IO fault-injection logs |
| S-SBC | Pending freeze | Pending | Pending | Pending | Pending | Station/depot host self-test and safe-failure procedure evidence |

### Pilot Integration Artifacts

Each pilot integration release creates:

- `control-electronics/<class>/diy-assembly/README.md` with assembly order and
  role-specific commissioning steps.
- `control-electronics/<class>/diy-assembly/bom-vN.csv` with exact SKUs,
  alternates, lifecycle status, supplier links, and substitution
  rules.
- `control-electronics/<class>/diy-assembly/wiring-map-vN.md` with terminal
  blocks, connector pinouts, cable labels, ferrule sizes, and harness
  routing.
- `control-electronics/<class>/diy-assembly/enclosure-vN.md` with DIN-rail,
  cabinet, sensor-mount, ingress-protection, and service-clearance
  notes.
- `control-electronics/<class>/diy-assembly/power-thermal-vN.md` with input
  ranges, fuse ratings, rail loads, heat budget, and derating limits.
- `control-electronics/<class>/bring-up/vN.md` with SD-card image checksum,
  boot log, `osr-selftest` output, smoke-test results, and known
  issues.
- `control-electronics/<class>/evidence/vN/` with photos, oscilloscope captures
  where relevant, watchdog/reset tests, safety-output truth tables,
  sensor-fault logs, and commissioning sign-off.

## Custom-Board Fabrication Track

| Host class | KiCad capture | Gerbers | Board BOM | Bring-up evidence | Safety evidence |
|---|---|---|---|---|---|
| T-ECU/S | Pending | Pending | Pending | Pending | 2oo2 watchdog, relay-stage, cross-check, and power-fault bench logs |
| T-ECU/A | Pending | Pending | Pending | Pending | Non-safety host self-test and communications fault-injection logs |
| T-OBS | Pending | Pending | Pending | Pending | 2oo2 obstacle-clear output, sensor-fault injection, heater/washer tests |
| W-SBC | Pending | Pending | Pending | Pending | Wayside power, network isolation, intrusion/points IO fault-injection logs |
| S-SBC | Usually unnecessary | Usually unnecessary | Usually unnecessary | Pending | Station/depot host self-test and safe-failure procedure evidence |

### Custom-Board Artifacts

Each custom-board release creates:

- `control-electronics/<class>/schematics/vN-kicad/` with the KiCad project.
- `control-electronics/<class>/gerbers/vN-rev-X/` with the fabrication ZIP and
  drill files.
- `control-electronics/<class>/bom/vN-rev-X.csv` with manufacturer part numbers,
  alternates, lifecycle status, and supplier links.
- `control-electronics/<class>/bring-up/vN-rev-X.md` with power-rail checks,
  programming steps, smoke-test results, and known issues.
- `control-electronics/<class>/evidence/vN-rev-X/` with oscilloscope captures,
  watchdog/reset tests, safety-output truth tables, and DFM/DFT review.

## Release Rule

A host class may be referenced by the certification pack as
`pilot integration hardware` after the Pilot / DIY Integration Track is
closed for the same revision. It may be referenced as `released
fabrication hardware` only after the Custom-Board Fabrication Track is
closed for the same revision.
