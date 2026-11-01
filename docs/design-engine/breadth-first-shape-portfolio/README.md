# Breadth-first shape portfolio

This source-bound research portfolio generated **54 physical body candidates** across **18 frame/shell/rib cells** and three parameter profiles. It retains **18 per-cell Pareto alternatives**. The separate cross-cell partial-quantity front contains 2 candidates.

## Scope and evidence

Each candidate holds the development baseline's 17 m car length and six-car formation context. The screen uses actual grammar-generated nominal stock, calculated stock mass properties, the current interface checks, declared DFMA operation counts and low/base/high Class C stock-only factory-gate cost. It does not run structural analysis, topology optimization or native CAD for all 54 alternatives. No global scalar winner or integrated selection is produced.

The cost is per one car body, with a six-body subtotal also recorded. It includes the current material-family proxy, purchase yield, setup and process-hour estimates, loaded skilled labour, machine allowance, QA allowance and factory overhead. It excludes installed joints and fasteners, unlocated equipment, final vehicle assembly, delivery, tooling investment, civil works, propulsion, operating costs, maintenance and lifecycle cost. The estimate is not a supplier quote or a measured production route.

The factory-gate production proxy uses the cost engine's two 8-hour shifts per day. The linked scenario defines civil work at two 8-hour shifts and operations at two 8-hour, two 9-hour and three 8-hour shifts per day; this body-shape study generates no civil estimate, operating cost or staffing plan.

## Composition cells

| Frame | Shell | Rib layout | Candidates | Per-cell Pareto IDs |
|---|---|---|---:|---|
| gfrp_axial_research | honeycomb-sandwich | full | 3 | `985dd7e2a16f` |
| gfrp_axial_research | honeycomb-sandwich | sparse | 3 | `3839908f5fc9` |
| aluminium_reference | sandwich | sparse | 3 | `7d08f0f81cdf` |
| aluminium_reference | honeycomb-sandwich | full | 3 | `0d0e338383c4` |
| aluminium_reference | skin | sparse | 3 | `7dd363b22b6a` |
| aluminium_reference | skin | modular | 3 | `c492d8a03d1c` |
| gfrp_axial_research | skin | modular | 3 | `258341ba59ae` |
| aluminium_reference | sandwich | modular | 3 | `7556016591d5` |
| aluminium_reference | honeycomb-sandwich | sparse | 3 | `139f6ea1b059` |
| aluminium_reference | skin | full | 3 | `94ab6167a3e4` |
| gfrp_axial_research | sandwich | sparse | 3 | `0d89b59dddb8` |
| gfrp_axial_research | sandwich | modular | 3 | `09790d64546e` |
| gfrp_axial_research | honeycomb-sandwich | modular | 3 | `24fc7f4c633d` |
| gfrp_axial_research | skin | full | 3 | `6caeb2202c81` |
| aluminium_reference | sandwich | full | 3 | `c89e23b31a2c` |
| aluminium_reference | honeycomb-sandwich | modular | 3 | `00110081b0f3` |
| gfrp_axial_research | sandwich | full | 3 | `efdf2b1d11d1` |
| gfrp_axial_research | skin | sparse | 3 | `e16e16ba8dba` |

## Interpretation limits

The archive preserves alternatives within each material/shape production family. Its metrics are partial quantity estimates and cannot establish that a candidate carries required loads, meets fatigue/fire/accessibility requirements, fits all installed equipment, is cheaper as a railway, or can be manufactured at the estimated hours. Pin-graph and stock totals are not body qualification. Unknown values stay unknown.

This first executable breadth step composes the existing aluminium/GFRP frames, skin/sandwich/honeycomb shells and full/sparse/modular rib rules. Curved or variable-thickness shells, cellular/lattice internals, organic implicit geometry, topology optimization, and coupled guideway/station shape families remain future geometry/evaluator adapters. They are not represented by cosmetic labels.

The study does not alter the selected v0.6 body or railway, dispatch native solvers, or approve any candidate. Physical and engineering acceptance remain false.

## Reproduce and verify

```bash
./osr design portfolio plan
./osr design portfolio build
./osr design portfolio verify
```

[Result](result.json) · [All generated physical candidates](candidates.json.gz) · [Manifest](manifest.json)
