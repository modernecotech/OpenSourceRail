# Kathmandu — Urban Rail Network

**Country:** NP · **Population:** 1,442,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kathmandu-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.17 bn (88.4%) of external capital** and **$5.22 bn of external interest**. Capital plus saved interest totals **$9.39 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **147.692 km to 127.816 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **71 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **233 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **233 metro-4car trainsets / 932 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Kathmandu rail network on OpenStreetMap](kathmandu-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 71 / 13 |
| Route length | 169.6 km double track |
| Direct transfers / reachable line pairs | 93.3% / 100.0% |
| Residents within 800 m radial station catchments | 2,742,140 (2020 raster; 36.3% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 233 × 4-car `metro-4car` trainsets (210 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 31.9 km | 11 | 50 | SE Outer ↔ NW Outer |
| line-2 | 24.9 km | 12 | 46 | SW Outer ↔ NE Mid |
| line-3 | 15.4 km | 8 | 31 | N Mid ↔ S Mid |
| line-4 | 20.5 km | 11 | 42 | N Mid ↔ SW Outer |
| line-5 | 25.9 km | 10 | 43 | E Outer ↔ W Outer |
| line-6 | 51.0 km | 19 | 21 | W Mid ↔ W Mid |
| **Total** | **169.6 km** | **71 unique** | **233** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 66,995 train-km/day |
| Annual traction demand | 422.6 GWh |
| Station/depot PV / storage | 48.3 MW / 331.5 MWh |
| Aggregate charging power | 100.5 MW |
| Dedicated solar plant | 261.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 13.7 km / 132 kWh |
| Lowest traversal charging margin | line-5: 216 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.44 bn |
| Stations | $413 M |
| Depots | $114 M |
| Rolling stock | $261 M |
| Dedicated solar plant | $209 M |
| Residual train control | $8.5 M |
| Charging microgrids | $21 M |
| EPC / project services | $158 M |
| **Total city programme** | **$2.62 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $548 M (20.9%) |
| Domestic / local capital | $2.07 bn (79.1%) |
| Annual public construction commitment | $208 M / yr for 7 years |
| Annual post-grace debt service | $169 M / yr |
| External capital saved vs default turnkey sensitivity | $4.17 bn |
| Capital + lifetime external interest saved | $9.39 bn |
| Annual OPEX | $59 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 13 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 630 assets / 3,374 tasks | [`kathmandu-operations-manifest.json`](operations/kathmandu-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kathmandu.toml`](kathmandu.toml) | Expanded simulator scenario |
| [`kathmandu.corridor.geojson`](kathmandu.corridor.geojson) | GIS corridor and stations |
| [`kathmandu.design-quality.yaml`](kathmandu.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kathmandu
```
