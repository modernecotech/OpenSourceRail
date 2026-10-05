# Zarqa — Urban Rail Network

**Country:** JO · **Population:** 700,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Zarqa-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.01 bn (88.8%) of external capital** and **$2.47 bn of external interest**. Capital plus saved interest totals **$4.48 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **53.070 km to 47.477 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **26 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **205 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **205 light-metro-3car trainsets / 615 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Zarqa rail network on OpenStreetMap](zarqa-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 26 / 3 |
| Route length | 66.8 km double track |
| Direct transfers / reachable line pairs | 100.0% / 100.0% |
| Residents within 800 m radial station catchments | 276,348 (2020 raster; 23.0% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 205 × 3-car `light-metro-3car` trainsets (185 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 28.4 km | 11 | 87 | NE Outer ↔ SW Outer |
| line-2 | 26.6 km | 10 | 80 | SW Outer ↔ NE Outer |
| line-3 | 11.9 km | 5 | 38 | N Mid ↔ E Mid |
| **Total** | **66.8 km** | **26 unique** | **205** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 31,074 train-km/day |
| Annual traction demand | 147.0 GWh |
| Station/depot PV / storage | 21.3 MW / 130.5 MWh |
| Aggregate charging power | 12.0 MW |
| Dedicated solar plant | 52.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 11.7 km / 94 kWh |
| Lowest traversal charging margin | line-3: 37 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $753 M |
| Stations | $126 M |
| Depots | $64 M |
| Rolling stock | $184 M |
| Dedicated solar plant | $42 M |
| Residual train control | $3.3 M |
| Charging microgrids | $2.6 M |
| EPC / project services | $79 M |
| **Total city programme** | **$1.26 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $252 M (20.1%) |
| Domestic / local capital | $1.00 bn (79.9%) |
| Annual public construction commitment | $112 M / yr for 5 years |
| Annual post-grace debt service | $80 M / yr |
| External capital saved vs default turnkey sensitivity | $2.01 bn |
| Capital + lifetime external interest saved | $4.48 bn |
| Annual OPEX | $39 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 10 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 371 assets / 2,327 tasks | [`zarqa-operations-manifest.json`](operations/zarqa-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`zarqa.toml`](zarqa.toml) | Expanded simulator scenario |
| [`zarqa.corridor.geojson`](zarqa.corridor.geojson) | GIS corridor and stations |
| [`zarqa.design-quality.yaml`](zarqa.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh zarqa
```
