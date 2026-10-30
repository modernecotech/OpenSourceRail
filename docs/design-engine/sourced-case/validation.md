# Executed sourced-design research — 30 October 2026

The software campaign is complete within its declared numerical scope. It is not
an accepted railway design. No authenticated installed-train measurements,
accepted operating map, qualified journey or complete whole-life price is supplied.

## Candidate-to-cell execution

- Five equipped research body families, two distances and three propulsion contexts: **30 cases**, **270 load/fault journeys**, **188 conditional arrivals** and **188 conditional motion screens**.
- The scenarios are empty, normal and crowd-control loading; +2% and −2% gradients; low adhesion; one bank failed; power interruption; and emergency braking. Stalls and intentional intermediate stops remain results. This is not every required weather, fault, HIL or recovery test.
- The two hot-climate contexts use the same Parker/H300/APEX source conditions, with station-only and additional distributed wayside banks. The EMRAX context is a **25 °C source-domain control**, not a demonstrated 55 °C alternative or a preferred railway.
- All cases propagate the same body identity through force/energy/braking, source electrical caps, located axle/civil reactions, physical stock, production drafts and scoped public-price records.
- Required quasi-static current is not measured current response. Missing losses, cooling envelopes, contact correlation, brake fade and complete installed auxiliaries remain open.

Run identity: `1e5186cb6bee091976562fd3f3227be03d99517c54f0d76e363ddd52c8688322`.

Publication `acbbef4bc03db1a74aa810b8ad832a8bcdfd37c04c9a51f7bdf9c8114e75d43b`
records all 30 semantic replays. Actual IFC export and reopening inspected
**176,202 physical occurrences** across the five six-car inventories, geometry
publication `a7f040a7bb037d915f3cd8e31c2ddf2a7c8c836bfd15af1f1a16b9f123f2adb3`.
These are net stock primitives and explicit purchased bounding envelopes, not
supplier internals or qualified installed geometry.

The bounds below describe counted research stock, purchased envelopes and
explicit allowances per car. They are **not weighed tare or certified installed
mass**; extra architecture equipment has its own downstream accounts.

| Family | Counted mass bounds kg/car | Occurrences/car |
|---|---:|---:|
| V1 | 11,259.7–13,104.1 | 5,952 |
| V2 | 10,970.8–13,002.6 | 5,432 |
| V3 | 12,067.0–13,541.9 | 5,952 |
| V4 | 12,425.0–13,901.6 | 6,346 |
| V5 | 11,386.6–13,146.8 | 5,685 |

V2 and V5 needed actual roof-rib relocation before the cap/bond generator could
produce positive support stacks. V1/V3/V4 retain their physical identities. A
separate [interruption record](audits/direct-serial-interruption-2026-10-30/interruption-record.json)
and [captured state archive](audits/direct-serial-interruption-2026-10-30/interrupted-state.tar.gz)
retain the direct serial command's SIGINT. The copied state indexes five cases,
records six completed files, and contains twelve case files because the copy
raced with parallel workers; it is explicitly not publication input, and no
in-memory result was integrated. Earlier failed structural executions remain in
the structural archive with their original inputs and outcomes.

## Structural evaluator and physical redesign

Seven bounded native packages are retained. Earlier failures exposed a panel-width
variable error and inadequate four-point integration across long joined members.
Their sources and results remain in the archive, explicitly marked unsuitable
for stiffness interpretation.

The corrected distributed-contact evaluator passes an independent composite
I-section energy/kinematic patch and the **36 algebraic case/mesh checks** on V1
and V4. All 36 responses exceed its declared linear-kinematic domain. Small mesh
change alone does not qualify the model or body.

A separate V4 bolster revision adds 63.918 kg/car to the upper bound. Its normal
fine-mesh translation falls 0.21182→0.17753 m and rotation 0.16122→0.04492 rad.
All 18 algebraic checks pass; only the two empty-load responses remain in the
stated domain. Its new cell then receives fresh nine-context journeys,
civil/manufacturing/cost propagation and actual IFC export/reopening. It is a
[next experiment](../sourced-bolster/README.md), not a selected compliant vehicle.

## What public sources resolved

The [source registry](../../../engineering/sourced_case/data/) supplies exact
motor/winding variants, gear limits, bus HVAC dimensions/power, battery topology,
converter voltage/current conditions, material properties and independent method
cases. Conflicting document revisions, ambiguous HVAC units and unknown hot-site
ratings remain explicit.

The auxiliary study counts three EPC converters and nine low-voltage converters
per car, plus battery/BMS/cradle/cabling/protection/cabinet accounts. A separately
identified charging proposal can require more converters, shore supplies and
connectors. It does not silently enter the vehicle mass or integrated cell. Actual
connection time, 55 °C supply output, taper, interlocks and enclosure heat remain
unqualified. A short terminal layover is a real design constraint.

Public battery list prices are a scoped Class B subtotal, not a supplier quotation,
complete train price or lower bound on negotiated procurement. Unknown prices
cannot establish the cheapest railway. The integrated winner remains null.

## Acceptance work and review tools

The [closure display](closure-summary.json) and [complete source-bound report](closure.json.gz)
cover phases 0–9 and WP1–WP6, including a component/material dependency graph.
They list actual coupon/joint, drive/contact/duty, brake/control, vehicle weighing,
civil/site and commercial/production inputs. Physical and independent qualification
remain open; public specifications qualify only their own stated configurations.

The browser explorer has five bounded views, actual part/occurrence drill-down,
source trajectories and phase coverage. GET displays saved evidence; write
requests are rejected. Display sampling does not change the stored records.

Reproduction commands and scope are in the [source package](../../../engineering/sourced_case/README.md).
`verify-publication` reconstructs and semantically checks every case; `verify-geometry`
reopens all five revised inventories; `verify-methods` checks recorded native
packages. The independent CI jobs retain execution receipts and failed outputs.
The current selected baseline and 22-page reader continue to verify separately.

Numerical workers use ordinary subprocesses with address-space and wall-clock
limits. They are not filesystem/network sandboxes. The browser check separately
uses device-isolated software rendering. Neither isolation mode is engineering
acceptance.
