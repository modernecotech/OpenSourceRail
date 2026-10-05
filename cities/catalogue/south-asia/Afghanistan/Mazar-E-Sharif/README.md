# Mazar-E-Sharif — Urban Rail Network

**Country:** AF · **Population:** 600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Mazar-E-Sharif-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.59 bn (88.6%) of external capital** and **$2.06 bn of external interest**. Capital plus saved interest totals **$3.65 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **49.411 km to 42.790 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **22 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **177 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **177 light-metro-3car trainsets / 531 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Mazar-E-Sharif rail network on OpenStreetMap](mazar-e-sharif-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 22 / 2 |
| Route length | 57.2 km double track |
| Direct transfers / reachable line pairs | 33.3% / 33.3% |
| Residents within 800 m radial station catchments | 136,462 (2020 raster; 29.7% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 177 × 3-car `light-metro-3car` trainsets (160 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 13.2 km | 6 | 40 | E Outer ↔ NW Mid |
| line-2 | 24.2 km | 8 | 75 | E Outer ↔ SW Outer |
| line-3 | 19.8 km | 8 | 62 | SW Outer ↔ E Outer |
| **Total** | **57.2 km** | **22 unique** | **177** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 26,582 train-km/day |
| Annual traction demand | 125.7 GWh |
| Station/depot PV / storage | 20.1 MW / 128.5 MWh |
| Aggregate charging power | 10.0 MW |
| Dedicated solar plant | 40.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 11.3 km / 81 kWh |
| Lowest traversal charging margin | line-1: 43 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $573 M |
| Stations | $105 M |
| Depots | $61 M |
| Rolling stock | $159 M |
| Dedicated solar plant | $33 M |
| Residual train control | $2.9 M |
| Charging microgrids | $2.2 M |
| EPC / project services | $63 M |
| **Total city programme** | **$999 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $204 M (20.5%) |
| Domestic / local capital | $795 M (79.5%) |
| Annual public construction commitment | $140 M / yr for 10 years |
| Annual post-grace debt service | $128 M / yr |
| External capital saved vs default turnkey sensitivity | $1.59 bn |
| Capital + lifetime external interest saved | $3.65 bn |
| Annual OPEX | $23 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 8 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 319 assets / 1,999 tasks | [`mazar-e-sharif-operations-manifest.json`](operations/mazar-e-sharif-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`mazar-e-sharif.toml`](mazar-e-sharif.toml) | Expanded simulator scenario |
| [`mazar-e-sharif.corridor.geojson`](mazar-e-sharif.corridor.geojson) | GIS corridor and stations |
| [`mazar-e-sharif.design-quality.yaml`](mazar-e-sharif.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh mazar-e-sharif
```
