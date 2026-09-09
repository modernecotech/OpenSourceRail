# LM3 First-Article Inspection and Test Plan

> Status: **unfilled protocol — not manufacturing, inspection or test evidence**.

This plan converts every factory release package into uniquely identified hold,
witness and record-review characteristics. Detailed result fields remain blank in
the JSON until copied into an authorised first-article build record.

Packages: **16** · Characteristics: **416**.

Point types: **H** mandatory hold, **W** witness, **R** record review.

## Package Index

| Package | Characteristics | H | W | R | Status |
|---|---:|---:|---:|---:|---|
| `LM3-FRP-010` — primary chassis, transverse structure and stepped-floor drawing pack | 27 | 17 | 3 | 7 | `open` |
| `LM3-FRP-020` — one-metre exterior module variant and retention drawing pack | 27 | 16 | 4 | 7 | `open` |
| `LM3-FRP-030` — panoramic front-glass carrier, seal and drainage interface pack | 24 | 14 | 4 | 6 | `open` |
| `LM3-FRP-040` — reversible front-lamp cassette and fascia-service pack | 23 | 13 | 4 | 6 | `open` |
| `LM3-FRP-050` — roof curb, HVAC, PV, antenna, fairing and access-zone pack | 32 | 20 | 5 | 7 | `open` |
| `LM3-FRP-060` — interior moulding, floor, service-access and fitout pack | 43 | 32 | 5 | 6 | `open` |
| `LM3-FRP-070` — common service rail, fastener and fixture-adapter pack | 22 | 12 | 4 | 6 | `open` |
| `LM3-FRP-080` — pre-cut exterior film artwork, application and repair pack | 25 | 18 | 2 | 5 | `open` |
| `LM3-FRP-090` — radiative roof-coating coupon and one-car trial pack | 21 | 13 | 3 | 5 | `open` |
| `LM3-FRP-100` — vehicle jacking, lifting, towing and field-rerailing interface pack | 21 | 11 | 4 | 6 | `open` |
| `LM3-FRP-110` — primary end, battery, door and window structural-interface pack | 31 | 18 | 5 | 8 | `open` |
| `LM3-FRP-120` — configurable train-end and articulation structural-interface pack | 29 | 17 | 5 | 7 | `open` |
| `LM3-FRP-130` — powered-bogie local frame, bracket and harness drawing pack | 25 | 15 | 5 | 5 | `open` |
| `LM3-FRP-140` — trailer-bogie local frame, bracket and harness drawing pack | 23 | 13 | 5 | 5 | `open` |
| `LM3-FRP-150` — battery tray, high-voltage and coolant local-hardware pack | 24 | 13 | 5 | 6 | `open` |
| `LM3-FRP-160` — low-voltage trainline harness and terminal-distribution pack | 19 | 10 | 4 | 5 | `open` |

## Execution Rules

- record actual results only while executing the identified work order and configuration
- a blank, planned or design-reference result does not satisfy a characteristic
- on failure stop, contain since the last accepted check, raise an NCR and extend inspection as the approved disposition requires
- do not waive a safety, structural, fire, braking, door, glazing, HV, lifting or recovery characteristic through routine sampling
- package acceptance requires every characteristic accepted, NCRs closed or expressly accepted, and named approvals recorded

Use [`manufacturing-control-record-template.json`](evidence/manufacturing-control-record-template.json)
for the detailed operation record and retain characteristic IDs when importing this plan into a QMS.
The factory release remains governed by [`factory-release-readiness.md`](factory-release-readiness.md).
