# Beni-Suef — Urban Rail Network

**Country:** EG · **Population:** 350,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Beni-Suef-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$892 M (88.7%) of external capital** and **$1.10 bn of external interest**. Capital plus saved interest totals **$1.99 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **39.986 km to 29.194 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **14 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **95 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **95 light-metro-3car trainsets / 285 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Beni-Suef rail network on OpenStreetMap](beni-suef-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 14 / 2 |
| Route length | 29.2 km double track |
| Direct transfers / reachable line pairs | 66.7% / 100.0% |
| Residents within 800 m radial station catchments | 178,760 (2020 raster; 19.3% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 95 × 3-car `light-metro-3car` trainsets (85 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 11.2 km | 5 | 37 | SW Outer ↔ NE Outer |
| line-2 | 10.2 km | 4 | 31 | N Outer ↔ SW Outer |
| line-3 |  7.8 km | 5 | 27 | NW Outer ↔ SE Mid |
| **Total** | **29.2 km** | **14 unique** | **95** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 13,575 train-km/day |
| Annual traction demand | 64.2 GWh |
| Station/depot PV / storage | 18.3 MW / 125.5 MWh |
| Aggregate charging power | 7.0 MW |
| Dedicated solar plant | 12.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 5.8 km / 47 kWh |
| Lowest traversal charging margin | line-2: 24 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $302 M |
| Stations | $74 M |
| Depots | $49 M |
| Rolling stock | $86 M |
| Dedicated solar plant | $10 M |
| Residual train control | $1.5 M |
| Charging microgrids | $1.6 M |
| EPC / project services | $36 M |
| **Total city programme** | **$559 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $113 M (20.3%) |
| Domestic / local capital | $445 M (79.7%) |
| Annual public construction commitment | $60 M / yr for 5 years |
| Annual post-grace debt service | $45 M / yr |
| External capital saved vs default turnkey sensitivity | $892 M |
| Capital + lifetime external interest saved | $1.99 bn |
| Annual OPEX | $15 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 2 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 187 assets / 1,113 tasks | [`beni-suef-operations-manifest.json`](operations/beni-suef-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`beni-suef.toml`](beni-suef.toml) | Expanded simulator scenario |
| [`beni-suef.corridor.geojson`](beni-suef.corridor.geojson) | GIS corridor and stations |
| [`beni-suef.design-quality.yaml`](beni-suef.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh beni-suef
```
