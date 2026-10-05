# Gazipur — Urban Rail Network

**Country:** BD · **Population:** 1,400,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Gazipur-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$6.63 bn (88.8%) of external capital** and **$8.32 bn of external interest**. Capital plus saved interest totals **$14.95 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **164.718 km to 156.721 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **91 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **342 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **342 metro-4car trainsets / 1368 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Gazipur rail network on OpenStreetMap](gazipur-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 91 / 16 |
| Route length | 253.5 km double track |
| Direct transfers / reachable line pairs | 93.3% / 100.0% |
| Residents within 800 m radial station catchments | 1,110,872 (2020 raster; 20.5% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 342 × 4-car `metro-4car` trainsets (307 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 33.1 km | 14 | 59 | S Mid ↔ N Mid |
| line-2 | 34.4 km | 13 | 58 | NW Mid ↔ E Outer |
| line-3 | 46.9 km | 17 | 79 | NE Outer ↔ SW Outer |
| line-4 | 45.2 km | 16 | 74 | SE Outer ↔ NW Outer |
| line-5 | 27.8 km | 9 | 46 | N Outer ↔ SW Mid |
| line-6 | 66.1 km | 22 | 26 | NW Mid ↔ W Mid |
| **Total** | **253.5 km** | **91 unique** | **342** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 102,525 train-km/day |
| Annual traction demand | 646.6 GWh |
| Station/depot PV / storage | 52.2 MW / 351.0 MWh |
| Aggregate charging power | 120.0 MW |
| Dedicated solar plant | 364.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 14.0 km / 140 kWh |
| Lowest traversal charging margin | line-5: 209 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.53 bn |
| Stations | $517 M |
| Depots | $136 M |
| Rolling stock | $383 M |
| Dedicated solar plant | $292 M |
| Residual train control | $13 M |
| Charging microgrids | $25 M |
| EPC / project services | $252 M |
| **Total city programme** | **$4.15 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $837 M (20.2%) |
| Domestic / local capital | $3.31 bn (79.8%) |
| Annual public construction commitment | $358 M / yr for 7 years |
| Annual post-grace debt service | $291 M / yr |
| External capital saved vs default turnkey sensitivity | $6.63 bn |
| Capital + lifetime external interest saved | $14.95 bn |
| Annual OPEX | $94 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 22 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 849 assets / 4,704 tasks | [`gazipur-operations-manifest.json`](operations/gazipur-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`gazipur.toml`](gazipur.toml) | Expanded simulator scenario |
| [`gazipur.corridor.geojson`](gazipur.corridor.geojson) | GIS corridor and stations |
| [`gazipur.design-quality.yaml`](gazipur.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh gazipur
```
