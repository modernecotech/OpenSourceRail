# Latakia — Urban Rail Network

**Country:** SY · **Population:** 700,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Latakia-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.82 bn (91.0%) of external capital** and **$4.94 bn of external interest**. Capital plus saved interest totals **$8.77 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **40.022 km to 26.327 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **11 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **92 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **92 light-metro-3car trainsets / 276 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Latakia rail network on OpenStreetMap](latakia-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 11 / 1 |
| Route length | 29.2 km double track |
| Direct transfers / reachable line pairs | 33.3% / 33.3% |
| Residents within 800 m radial station catchments | 162,350 (2020 raster; 25.9% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 92 × 3-car `light-metro-3car` trainsets (82 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 13.3 km | 4 | 40 | SW Mid ↔ E Outer |
| line-2 |  6.7 km | 4 | 23 | W Mid ↔ NE Mid |
| line-3 |  9.3 km | 3 | 29 | SW Mid ↔ NW Outer |
| **Total** | **29.2 km** | **11 unique** | **92** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 13,588 train-km/day |
| Annual traction demand | 64.3 GWh |
| Station/depot PV / storage | 17.4 MW / 124.0 MWh |
| Aggregate charging power | 5.5 MW |
| Dedicated solar plant | 16.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 6.3 km / 45 kWh |
| Lowest traversal charging margin | line-2: 37 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.99 bn |
| Stations | $42 M |
| Depots | $48 M |
| Rolling stock | $83 M |
| Dedicated solar plant | $13 M |
| Residual train control | $1.5 M |
| Charging microgrids | $1.2 M |
| EPC / project services | $152 M |
| **Total city programme** | **$2.34 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $379 M (16.2%) |
| Domestic / local capital | $1.96 bn (83.8%) |
| Annual public construction commitment | $369 M / yr for 10 years |
| Annual post-grace debt service | $338 M / yr |
| External capital saved vs default turnkey sensitivity | $3.82 bn |
| Capital + lifetime external interest saved | $8.77 bn |
| Annual OPEX | $46 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 4 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 168 assets / 1,031 tasks | [`latakia-operations-manifest.json`](operations/latakia-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`latakia.toml`](latakia.toml) | Expanded simulator scenario |
| [`latakia.corridor.geojson`](latakia.corridor.geojson) | GIS corridor and stations |
| [`latakia.design-quality.yaml`](latakia.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh latakia
```
