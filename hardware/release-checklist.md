# Hardware Release Checklist

This checklist turns the hardware gap into concrete release gates for
each host class. A board is not fabrication-ready until every item in
its row is present in-tree or linked to a controlled external release.

| Host class | KiCad capture | Gerbers | Board BOM | Bench evidence | Safety evidence |
|---|---|---|---|---|---|
| T-ECU/S | Pending | Pending | Pending | Pending | 2oo2 watchdog, relay-stage, cross-check, and power-fault bench logs |
| T-ECU/A | Pending | Pending | Pending | Pending | Non-safety host self-test and communications fault-injection logs |
| T-OBS | Pending | Pending | Pending | Pending | 2oo2 obstacle-clear output, sensor-fault injection, heater/washer tests |
| W-SBC | Pending | Pending | Pending | Pending | Wayside power, network isolation, intrusion/points IO fault-injection logs |
| S-SBC | Pending | Pending | Pending | Pending | Station/depot host self-test and safe-failure procedure evidence |

## Required Artifacts

Each board release creates:

- `hardware/<class>/schematics/vN-kicad/` with the KiCad project.
- `hardware/<class>/gerbers/vN-rev-X/` with the fabrication ZIP and
  drill files.
- `hardware/<class>/bom/vN-rev-X.csv` with manufacturer part numbers,
  alternates, lifecycle status, and supplier links.
- `hardware/<class>/bring-up/vN-rev-X.md` with power-rail checks,
  programming steps, smoke-test results, and known issues.
- `hardware/<class>/evidence/vN-rev-X/` with oscilloscope captures,
  watchdog/reset tests, safety-output truth tables, and DFM/DFT review.

## Release Rule

A host class may be referenced by the certification pack as
`released hardware` only after KiCad, gerbers, board BOM, bring-up
logs, and applicable safety evidence exist for the same revision.
Until then it remains a board-level specification.
