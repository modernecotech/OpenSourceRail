# Buildable station kit catalogue

Generated station EBOM/MBOM and unsigned assembly travelers for the six
base station shells and the controlled elevated-interchange variant.

| Archetype | Platforms | Platform length m | Bays/platform | Product rows | Open product gaps | Auxiliary modules / installed m² | BOM | Traveler |
|---|---:|---:|---:|---:|---:|---:|---|---|
| `halt` | 1 | 55.5 | 10 | 25 | 10 | 1 / 187.0 | `build/bom/stations/halt.csv` | [`md`](travelers/halt.md) |
| `standard` | 2 | 59.5 | 10 | 28 | 12 | 7 / 1309.0 | `build/bom/stations/standard.csv` | [`md`](travelers/standard.md) |
| `major` | 2 | 59.5 | 12 | 29 | 13 | 8 / 1496.0 | `build/bom/stations/major.csv` | [`md`](travelers/major.md) |
| `interchange` | 4 | 59.5 | 10 | 29 | 13 | 10 / 1870.0 | `build/bom/stations/interchange.csv` | [`md`](travelers/interchange.md) |
| `interchange-elevated` | 4 | 59.5 | 10 | 30 | 15 | 12 / 2244.0 | `build/bom/stations/interchange-elevated.csv` | [`md`](travelers/interchange-elevated.md) |
| `terminal` | 2 | 59.5 | 14 | 36 | 20 | 10 / 1870.0 | `build/bom/stations/terminal.csv` | [`md`](travelers/terminal.md) |
| `depot-terminal` | 2 | 59.5 | 14 | 43 | 27 | 5 / 935.0 | `build/bom/stations/depot-terminal.csv` | [`md`](travelers/depot-terminal.md) |

Auxiliary area is quantised upward into repeatable 8.5 m × 22 m solar-roof
modules rather than left as an unbuildable square-metre allowance.
Site structural, foundation, drainage, egress, and electrical approvals remain gates.
See the generated [`open release gap register`](open-release-gaps.md) for
the supplier, site, utility, and component-design closures behind these counts.
