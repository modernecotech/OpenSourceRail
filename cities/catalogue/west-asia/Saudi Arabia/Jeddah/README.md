# Jeddah — Urban Rail Network

**Country:** SA · **Population:** 4,700,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Jeddah-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$26.07 bn (90.2%) of external capital** and **$32.05 bn of external interest**. Capital plus saved interest totals **$58.12 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **310.121 km to 287.814 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **128 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**9 line-local depots** provide **560 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **560 metro-6car trainsets / 3360 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Jeddah rail network on OpenStreetMap](jeddah-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 128 / 24 |
| Route length | 347.0 km double track |
| Direct transfers / reachable line pairs | 75.0% / 100.0% |
| Residents within 800 m radial station catchments | 855,985 (2020 raster; 22.3% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 560 × 6-car `metro-6car` trainsets (503 peak revenue) |
| Peak network throughput | 259,200 passengers/hour |
| Practical service capacity | 2,276,640 passenger-trips/day |
| Annual paid-trip planning range | 415.5–664.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 47.3 km | 17 | 91 | S Mid ↔ NW Outer |
| line-2 | 30.3 km | 11 | 56 | S Mid ↔ NW Mid |
| line-3 | 39.2 km | 13 | 73 | N Outer ↔ SE Mid |
| line-4 | 45.4 km | 16 | 84 | N Mid ↔ S Outer |
| line-5 | 33.2 km | 13 | 67 | E Outer ↔ W Mid |
| line-6 | 30.2 km | 14 | 60 | SE Outer ↔ W Inner |
| line-7 | 23.3 km | 9 | 46 | NE Outer ↔ S Inner |
| line-8 | 24.0 km | 10 | 47 | NE Mid ↔ SW Inner |
| line-9 | 74.2 km | 25 | 36 | NW Mid ↔ NW Mid |
| **Total** | **347.0 km** | **128 unique** | **560** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,952 one-way journeys / 144,092 train-km/day |
| Annual traction demand | 1,363.2 GWh |
| Station/depot PV / storage | 77.1 MW / 574.0 MWh |
| Aggregate charging power | 232.0 MW |
| Dedicated solar plant | 627.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-4: 16.8 km / 270 kWh |
| Lowest traversal charging margin | line-7: 192 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $12.58 bn |
| Stations | $693 M |
| Depots | $251 M |
| Rolling stock | $941 M |
| Dedicated solar plant | $502 M |
| Residual train control | $17 M |
| Charging microgrids | $47 M |
| EPC / project services | $1.02 bn |
| **Total city programme** | **$16.05 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.82 bn (17.6%) |
| Domestic / local capital | $13.23 bn (82.4%) |
| Annual public construction commitment | $1.13 bn / yr for 5 years |
| Annual post-grace debt service | $768 M / yr |
| External capital saved vs default turnkey sensitivity | $26.07 bn |
| Capital + lifetime external interest saved | $58.12 bn |
| Annual OPEX | $447 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 34 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,289 assets / 7,351 tasks | [`jeddah-operations-manifest.json`](operations/jeddah-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`jeddah.toml`](jeddah.toml) | Expanded simulator scenario |
| [`jeddah.corridor.geojson`](jeddah.corridor.geojson) | GIS corridor and stations |
| [`jeddah.design-quality.yaml`](jeddah.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh jeddah
```
