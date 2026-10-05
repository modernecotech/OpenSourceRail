# San-Salvador — Urban Rail Network

**Country:** SV · **Population:** 1,800,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only San-Salvador-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$5.56 bn (88.6%) of external capital** and **$6.84 bn of external interest**. Capital plus saved interest totals **$12.40 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **188.033 km to 173.941 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **92 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **307 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **307 metro-4car trainsets / 1228 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![San-Salvador rail network on OpenStreetMap](san-salvador-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 92 / 16 |
| Route length | 235.2 km double track |
| Direct transfers / reachable line pairs | 100.0% / 100.0% |
| Residents within 800 m radial station catchments | 579,393 (2020 raster; 26.9% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 307 × 4-car `metro-4car` trainsets (276 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 27.2 km | 16 | 58 | W Mid ↔ E Mid |
| line-2 | 33.0 km | 12 | 53 | N Mid ↔ SW Outer |
| line-3 | 34.5 km | 14 | 58 | SE Outer ↔ W Mid |
| line-4 | 36.2 km | 14 | 59 | SW Mid ↔ NE Outer |
| line-5 | 29.5 km | 11 | 48 | S Mid ↔ NW Outer |
| line-6 | 74.8 km | 25 | 31 | NW Mid ↔ W Mid |
| **Total** | **235.2 km** | **92 unique** | **307** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 91,977 train-km/day |
| Annual traction demand | 580.1 GWh |
| Station/depot PV / storage | 52.8 MW / 354.0 MWh |
| Aggregate charging power | 121.5 MW |
| Dedicated solar plant | 320.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-4: 13.6 km / 136 kWh |
| Lowest traversal charging margin | line-5: 215 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.99 bn |
| Stations | $520 M |
| Depots | $129 M |
| Rolling stock | $344 M |
| Dedicated solar plant | $256 M |
| Residual train control | $12 M |
| Charging microgrids | $25 M |
| EPC / project services | $211 M |
| **Total city programme** | **$3.49 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $718 M (20.6%) |
| Domestic / local capital | $2.77 bn (79.4%) |
| Annual public construction commitment | $398 M / yr for 5 years |
| Annual post-grace debt service | $302 M / yr |
| External capital saved vs default turnkey sensitivity | $5.56 bn |
| Capital + lifetime external interest saved | $12.40 bn |
| Annual OPEX | $86 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 21 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 815 assets / 4,406 tasks | [`san-salvador-operations-manifest.json`](operations/san-salvador-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`san-salvador.toml`](san-salvador.toml) | Expanded simulator scenario |
| [`san-salvador.corridor.geojson`](san-salvador.corridor.geojson) | GIS corridor and stations |
| [`san-salvador.design-quality.yaml`](san-salvador.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh san-salvador
```
