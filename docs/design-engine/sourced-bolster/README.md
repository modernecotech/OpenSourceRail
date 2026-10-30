# Next physical experiment: V4 bogie load transfer

This separately identified aluminium-body revision adds full-depth transverse
bolsters, rail-web spreaders and diaphragms at the actual bogie pads. It replaces
local doublers and superseded splices, counts M8 retention and bounded weld
deposition, and preserves passenger/equipment requirements. It does not replace
the selected v0.6 reference or the five-family campaign.

The new body candidate is
`4fd7a56ff432b4a6e86c9722b5677a6b34893e9ac840b7e1dff5148ba09aad8b`.
Its upper mass bound rises by **63.918 kg/car**. The complete actual input, source
archive, tool/resource record, saved response and logs are sealed by
[the native publication](structural-methods.json), package
`8bdb4136b184b6a053322bf5f13b8d5940cfac47be71433c41192d5147a3cc45`.

The refreshed downstream cell is candidate
`091b50cdd0d85d0ee2489f6740186152032eea654caac0c5d191641af568143c`, evaluation
`562e31688d11ce7d9c40c45052c0f9a5579aadd4de2096272557181624bd85da`, publication
`d9782cb747585156c1344e0bab154aa9c99ad12b773aee5dbea2ae8c2013fe56`.

| Fine-mesh comparison | Ancestor | Bolster revision |
|---|---:|---:|
| Normal maximum translation | 0.21182 m | 0.17753 m |
| Normal maximum rotation | 0.16122 rad | 0.04492 rad |
| Crowd maximum translation | 0.37873 m | 0.32215 m |
| Normal mesh-change indicator | 1.94% | 1.58% |

All **18 case/mesh responses pass the algebraic residual checks**. Only the two
empty-load responses remain inside the evaluator's declared linear-kinematic
domain. Normal and crowd results therefore do not establish body compliance.
The local load-transfer hypothesis is useful, but side-sill, door-header,
skin/laminate, finite-joint and nonlinear response still need evaluation.

The [complete downstream cell publication](bolster-cell.json) carries this body
through a new 2 km canonical bundle, nine load/fault journeys, civil quantities,
manufacturing drafts, scoped price records and an actually reopened 38,988-
occurrence IFC. Six journeys arrive conditionally. Source current, hot-site
charging, physical braking, structural and whole-life-price qualification remain
open. The body and integrated cell have different identities.

The new pad-retention arrangement leaves approximately 13 mm static clearance to
the currently represented spring envelope. Dynamic suspension travel,
installation access, joint strength, welding/HAZ, fatigue and physical correlation
remain unverified. Neither a small mesh-change indicator nor a connected contact
graph grants manufacturing or operating release.

[Source generator](../../../engineering/sourced_redesign/README.md) ·
[main sourced campaign](../sourced-case/README.md) ·
[project introduction](../../../README.md)

```sh
./osr design sourced verify-methods --output docs/design-engine/sourced-bolster
tools/automation/osr-python tools/automation/sourced-bolster-package.py verify-publication docs/design-engine/sourced-bolster
```
