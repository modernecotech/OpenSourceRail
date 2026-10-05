# Beirut — Urban Rail Network

**Country:** LB · **Population:** 2,200,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Beirut-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.08 bn (88.6%) of external capital** and **$3.90 bn of external interest**. Capital plus saved interest totals **$6.98 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **110.202 km to 93.886 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **56 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **190 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **190 metro-4car trainsets / 760 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Beirut rail network on OpenStreetMap](beirut-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 56 / 10 |
| Route length | 123.1 km double track |
| Direct transfers / reachable line pairs | 80.0% / 100.0% |
| Residents within 800 m radial station catchments | 1,979,861 (2020 raster; 44.3% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 190 × 4-car `metro-4car` trainsets (170 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 31.0 km | 11 | 49 | SW Mid ↔ NE Outer |
| line-2 | 13.7 km | 8 | 30 | NW Mid ↔ S Mid |
| line-3 | 18.0 km | 9 | 36 | W Mid ↔ NE Outer |
| line-4 | 15.9 km | 8 | 31 | E Mid ↔ W Mid |
| line-5 | 15.5 km | 8 | 30 | NW Inner ↔ SE Mid |
| line-6 | 29.0 km | 12 | 14 | NE Mid ↔ NE Inner |
| **Total** | **123.1 km** | **56 unique** | **190** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 50,471 train-km/day |
| Annual traction demand | 318.3 GWh |
| Station/depot PV / storage | 44.4 MW / 312.0 MWh |
| Aggregate charging power | 81.0 MW |
| Dedicated solar plant | 131.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 10.2 km / 98 kWh |
| Lowest traversal charging margin | line-5: 229 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.03 bn |
| Stations | $337 M |
| Depots | $106 M |
| Rolling stock | $213 M |
| Dedicated solar plant | $105 M |
| Residual train control | $6.2 M |
| Charging microgrids | $17 M |
| EPC / project services | $120 M |
| **Total city programme** | **$1.93 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $398 M (20.6%) |
| Domestic / local capital | $1.53 bn (79.4%) |
| Annual public construction commitment | $363 M / yr for 8 years |
| Annual post-grace debt service | $331 M / yr |
| External capital saved vs default turnkey sensitivity | $3.08 bn |
| Capital + lifetime external interest saved | $6.98 bn |
| Annual OPEX | $49 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 9 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 508 assets / 2,719 tasks | [`beirut-operations-manifest.json`](operations/beirut-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`beirut.toml`](beirut.toml) | Expanded simulator scenario |
| [`beirut.corridor.geojson`](beirut.corridor.geojson) | GIS corridor and stations |
| [`beirut.design-quality.yaml`](beirut.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh beirut
```
