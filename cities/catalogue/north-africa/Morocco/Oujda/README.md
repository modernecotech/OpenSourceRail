# Oujda — Urban Rail Network

**Country:** MA · **Population:** 600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Oujda-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$823 M (88.6%) of external capital** and **$1.01 bn of external interest**. Capital plus saved interest totals **$1.83 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **37.500 km to 26.930 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **15 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **89 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **89 light-metro-3car trainsets / 267 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Oujda rail network on OpenStreetMap](oujda-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 15 / 2 |
| Route length | 26.9 km double track |
| Direct transfers / reachable line pairs | 66.7% / 100.0% |
| Residents within 800 m radial station catchments | 195,532 (2020 raster; 35.2% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 89 × 3-car `light-metro-3car` trainsets (79 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 10.4 km | 6 | 34 | W Outer ↔ E Outer |
| line-2 |  8.6 km | 5 | 28 | N Outer ↔ SE Outer |
| line-3 |  8.0 km | 4 | 27 | N Outer ↔ SW Outer |
| **Total** | **26.9 km** | **15 unique** | **89** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 12,523 train-km/day |
| Annual traction demand | 59.2 GWh |
| Station/depot PV / storage | 18.6 MW / 126.0 MWh |
| Aggregate charging power | 7.5 MW |
| Dedicated solar plant | 9.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 3.7 km / 30 kWh |
| Lowest traversal charging margin | line-3: 27 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $263 M |
| Stations | $82 M |
| Depots | $47 M |
| Rolling stock | $80 M |
| Dedicated solar plant | $7.8 M |
| Residual train control | $1.3 M |
| Charging microgrids | $1.6 M |
| EPC / project services | $33 M |
| **Total city programme** | **$516 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $105 M (20.4%) |
| Domestic / local capital | $410 M (79.6%) |
| Annual public construction commitment | $36 M / yr for 5 years |
| Annual post-grace debt service | $25 M / yr |
| External capital saved vs default turnkey sensitivity | $823 M |
| Capital + lifetime external interest saved | $1.83 bn |
| Annual OPEX | $16 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 0 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 185 assets / 1,076 tasks | [`oujda-operations-manifest.json`](operations/oujda-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`oujda.toml`](oujda.toml) | Expanded simulator scenario |
| [`oujda.corridor.geojson`](oujda.corridor.geojson) | GIS corridor and stations |
| [`oujda.design-quality.yaml`](oujda.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh oujda
```
