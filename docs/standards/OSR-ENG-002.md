# OSR-ENG-002: Automated reference part generation

Version 1.0.0 · internal process standard · adopted 2026-10-10.

This OpenSourceRail standard governs automated **reference design studies**.
It supplements [OSR-ENG-001](OSR-ENG-001.md). It grants no supplier release,
ISO conformity, production authority or railway operating approval. Project and
legal requirements retain the precedence established by OSR-ENG-001.

The [industry register](../../engineering/reference-parts/industry-basis.json)
records primary sources, review date, numerical data actually adopted and
separate OSR assumptions. Public summaries guide method selection; full ISO
clause review and project applicability remain open. In particular,
[ISO 12405-4:2018](https://www.iso.org/standard/71407.html) covers road-vehicle
battery performance tests. Any railway use requires explicit applicability review.
ISO 1101, 898-1, 16047 and 17025 method/traceability references follow OSR-ENG-001;
their public catalogue descriptions do not supply manufacturing tolerances,
bolt preload or acceptance limits.

| Requirement | Internal mandatory rule | Executable verification |
|---|---|---|
| OSR-AP-001 | A generated family shall retain the authoritative count, length, bogie and axle datums. | Full-family count/position tests for all five families; complete-passage planner |
| OSR-AP-002 | Each physical mass shall belong to one nonoverlapping instance scope; expanded kit mass shall be removed from its aggregate. | Shared scope validator, independent total weight/reaction balance and passenger loading test |
| OSR-AP-003 | Battery architecture changes shall regenerate geometry, quantities, mass/inertia, energy, current, resistance and thermal inputs together. | Parallel-string change propagation and cutlist conservation tests |
| OSR-AP-004 | Generated reference geometry shall be valid within its declared primitive and packaging domain. | Positive/finite dimensions, balanced nonoverlapping holes and battery-bay rejection tests; native FreeCAD solids |
| OSR-AP-005 | Every physical joint shall bind known instance datums and a typed mechanical interface with units and signs. | Interface/model identity, endpoint, joint coverage, unit and limit tests; native assembly datum reconciliation |
| OSR-AP-006 | Every required catalogue allocation shall have a coverage record stating representation, evidence and unresolved limitations. | Unique complete coverage and unresolved-slot tests |
| OSR-AP-007 | Electrical and thermal calculations shall retain separate energy balances and current/SOC/temperature constraint states. | Independent `P=VI`, `I²R`, exact cooling and charge/discharge energy checks |
| OSR-AP-008 | Generated quantities and QA characteristics shall retain instance identity; absent acceptance limits shall remain open. | Cutlist sums and QA open-limit tests |
| OSR-AP-009 | Source and generated-output hashes shall bind each package; verification shall reproduce its compiled results. | CLI generate/verify and altered-output rejection tests |
| OSR-AP-010 | Reference, numerical, engineering and physical acceptance states shall remain distinct. | Coverage/review false-release and null engineering-approval tests |

Energy checks use a 1e-7 J absolute residual tolerance in the controlled unit tests.
Train mass accounting uses 1e-12 relative reconciliation tolerance. These are
internal numerical implementation checks, not ISO or railway acceptance limits.
Native assembly residuals and refinement thresholds remain governed by OSR-ENG-001.

Generated inspection nominal values are design targets. Acceptance intervals,
measurement calibration/uncertainty, joint capacity, fatigue, fire protection,
electromagnetic compatibility and operating cases require their own controlled
evidence. None can be closed by a CAD placement constraint or a numerical mass sum.
