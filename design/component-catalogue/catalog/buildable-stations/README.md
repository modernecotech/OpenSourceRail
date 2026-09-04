# Buildable station kit catalogue

Generated station EBOM/MBOM and unsigned assembly travelers for the six
base station shells and the controlled elevated-interchange variant.

| Archetype | Platforms | Platform length m | Bays/platform | Product rows | Open product gaps | Auxiliary modules / installed m² | Definition | Traveler |
|---|---:|---:|---:|---:|---:|---:|---|---|
| `halt` | 1 | 55.5 | 10 | 25 | 10 | 1 / 187.0 | [`md`](variants/halt.md) | [`md`](travelers/halt.md) |
| `standard` | 2 | 59.5 | 10 | 28 | 12 | 7 / 1309.0 | [`md`](variants/standard.md) | [`md`](travelers/standard.md) |
| `major` | 2 | 59.5 | 12 | 29 | 13 | 8 / 1496.0 | [`md`](variants/major.md) | [`md`](travelers/major.md) |
| `interchange` | 4 | 59.5 | 10 | 29 | 13 | 10 / 1870.0 | [`md`](variants/interchange.md) | [`md`](travelers/interchange.md) |
| `interchange-elevated` | 4 | 59.5 | 10 | 30 | 15 | 12 / 2244.0 | [`md`](variants/interchange-elevated.md) | [`md`](travelers/interchange-elevated.md) |
| `terminal` | 2 | 59.5 | 14 | 36 | 20 | 10 / 1870.0 | [`md`](variants/terminal.md) | [`md`](travelers/terminal.md) |
| `depot-terminal` | 2 | 59.5 | 14 | 43 | 27 | 5 / 935.0 | [`md`](variants/depot-terminal.md) | [`md`](travelers/depot-terminal.md) |

Auxiliary area is quantised upward into repeatable 8.5 m × 22 m solar-roof
modules rather than left as an unbuildable square-metre allowance.
Site structural, foundation, drainage, egress, and electrical approvals remain gates.
See the generated [`open release gap register`](open-release-gaps.md) for
the supplier, site, utility, and component-design closures behind these counts.
The [`factory/release work packages`](factory-release-work-packages.md) classify
all 45 unique products as reusable-definition, supplier-configuration or
deployment-specific scope. The intentionally open [`readiness register`](factory-release-readiness.md)
and [evidence template](evidence/factory-release-record-template.json) prevent
catalogue maturity from being mistaken for fabrication or construction release.
The [`reference defaults`](default-product-specifications.md) give all 29 open
product families practical concept/RFQ values plus mandatory override triggers.
The generated [`station product reconciliation`](station-product-reconciliation.md)
checks the BOM, traveler, drawing, FreeCAD and IFC identities in both directions.
The shared [station systems screening](../../../../engineering/analysis/stations/screening-summary.md)
runs OpenSees, JuPedSim and SWMM across the family. EnergyPlus/FDS execute the
baseline and proposed depot thermal/fire cases; the baseline failures, screened
mitigation and [open deployment work packages](../../../../engineering/analysis/stations/mitigation-work-packages.md)
remain evidence for detailed design, not construction release.
