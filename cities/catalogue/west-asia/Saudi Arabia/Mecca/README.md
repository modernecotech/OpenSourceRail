# Mecca — Urban Rail Network

**Country:** SA · **Population:** 2,200,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Mecca-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.70 bn (88.9%) of external capital** and **$5.78 bn of external interest**. Capital plus saved interest totals **$10.47 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **182.907 km to 169.444 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **78 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **260 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **260 metro-4car trainsets / 1040 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Mecca rail network on OpenStreetMap](mecca-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 78 / 17 |
| Route length | 203.0 km double track |
| Direct transfers / reachable line pairs | 80.0% / 100.0% |
| Residents within 800 m radial station catchments | 442,071 (2020 raster; 24.3% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 260 × 4-car `metro-4car` trainsets (234 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 27.8 km | 11 | 48 | W Mid ↔ SE Outer |
| line-2 | 23.4 km | 9 | 40 | SE Mid ↔ W Mid |
| line-3 | 32.6 km | 13 | 54 | NE Outer ↔ SW Mid |
| line-4 | 30.2 km | 12 | 51 | N Mid ↔ S Outer |
| line-5 | 23.3 km | 10 | 41 | E Mid ↔ NW Outer |
| line-6 | 65.7 km | 23 | 26 | W Mid ↔ W Mid |
| **Total** | **203.0 km** | **78 unique** | **260** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 79,134 train-km/day |
| Annual traction demand | 499.1 GWh |
| Station/depot PV / storage | 49.5 MW / 337.5 MWh |
| Aggregate charging power | 106.5 MW |
| Dedicated solar plant | 205.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 12.9 km / 139 kWh |
| Lowest traversal charging margin | line-6: 203 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.76 bn |
| Stations | $389 M |
| Depots | $120 M |
| Rolling stock | $291 M |
| Dedicated solar plant | $164 M |
| Residual train control | $10 M |
| Charging microgrids | $22 M |
| EPC / project services | $181 M |
| **Total city programme** | **$2.94 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $589 M (20.0%) |
| Domestic / local capital | $2.35 bn (80.0%) |
| Annual public construction commitment | $205 M / yr for 5 years |
| Annual post-grace debt service | $141 M / yr |
| External capital saved vs default turnkey sensitivity | $4.70 bn |
| Capital + lifetime external interest saved | $10.47 bn |
| Annual OPEX | $134 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 26 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 693 assets / 3,735 tasks | [`mecca-operations-manifest.json`](operations/mecca-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`mecca.toml`](mecca.toml) | Expanded simulator scenario |
| [`mecca.corridor.geojson`](mecca.corridor.geojson) | GIS corridor and stations |
| [`mecca.design-quality.yaml`](mecca.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh mecca
```
