# Dakar — Urban Rail Network

**Country:** SN · **Population:** 4,030,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Dakar-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$40.24 bn (91.0%) of external capital** and **$50.44 bn of external interest**. Capital plus saved interest totals **$90.68 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **180.000 km to 176.306 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **116 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **382 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **382 metro-6car trainsets / 2292 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Dakar rail network on OpenStreetMap](dakar-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 116 / 20 |
| Route length | 211.0 km double track |
| Direct transfers / reachable line pairs | 66.7% / 100.0% |
| Residents within 800 m radial station catchments | 1,485,057 (2020 raster; 40.6% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 382 × 6-car `metro-6car` trainsets (344 peak revenue) |
| Peak network throughput | 172,800 passengers/hour |
| Practical service capacity | 1,473,120 passenger-trips/day |
| Annual paid-trip planning range | 268.8–430.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 34.9 km | 12 | 65 | E Outer ↔ W Mid |
| line-2 | 28.6 km | 22 | 81 | W Mid ↔ E Mid |
| line-3 | 27.2 km | 8 | 49 | W Mid ↔ NE Outer |
| line-4 | 22.4 km | 16 | 61 | NE Mid ↔ SW Mid |
| line-5 | 35.9 km | 24 | 90 | E Outer ↔ SW Mid |
| line-6 | 61.9 km | 34 | 36 | W Mid ↔ W Mid |
| **Total** | **211.0 km** | **116 unique** | **382** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 83,696 train-km/day |
| Annual traction demand | 791.8 GWh |
| Station/depot PV / storage | 61.8 MW / 452.0 MWh |
| Aggregate charging power | 224.0 MW |
| Dedicated solar plant | 312.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 13.1 km / 218 kWh |
| Lowest traversal charging margin | line-3: 187 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $21.07 bn |
| Stations | $772 M |
| Depots | $168 M |
| Rolling stock | $642 M |
| Dedicated solar plant | $250 M |
| Residual train control | $11 M |
| Charging microgrids | $45 M |
| EPC / project services | $1.59 bn |
| **Total city programme** | **$24.55 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $3.96 bn (16.1%) |
| Domestic / local capital | $20.60 bn (83.9%) |
| Annual public construction commitment | $2.17 bn / yr for 7 years |
| Annual post-grace debt service | $1.73 bn / yr |
| External capital saved vs default turnkey sensitivity | $40.24 bn |
| Capital + lifetime external interest saved | $90.68 bn |
| Annual OPEX | $480 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 15 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,027 assets / 5,548 tasks | [`dakar-operations-manifest.json`](operations/dakar-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`dakar.toml`](dakar.toml) | Expanded simulator scenario |
| [`dakar.corridor.geojson`](dakar.corridor.geojson) | GIS corridor and stations |
| [`dakar.design-quality.yaml`](dakar.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh dakar
```
