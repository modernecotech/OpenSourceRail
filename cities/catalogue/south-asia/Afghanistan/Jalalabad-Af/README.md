# Jalalabad-Af — Urban Rail Network

**Country:** AF · **Population:** 350,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Jalalabad-Af-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.15 bn (88.6%) of external capital** and **$1.48 bn of external interest**. Capital plus saved interest totals **$2.63 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **43.025 km to 37.000 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **17 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **130 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **130 light-metro-3car trainsets / 390 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Jalalabad-Af rail network on OpenStreetMap](jalalabad-af-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 17 / 1 |
| Route length | 40.6 km double track |
| Direct transfers / reachable line pairs | 100.0% / 100.0% |
| Residents within 800 m radial station catchments | 133,703 (2020 raster; 23.0% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 130 × 3-car `light-metro-3car` trainsets (117 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  8.2 km | 5 | 28 | S Mid ↔ N Mid |
| line-2 | 20.4 km | 7 | 64 | SE Outer ↔ NW Outer |
| line-3 | 11.9 km | 5 | 38 | NE Outer ↔ S Mid |
| **Total** | **40.6 km** | **17 unique** | **130** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 18,866 train-km/day |
| Annual traction demand | 89.2 GWh |
| Station/depot PV / storage | 18.9 MW / 126.5 MWh |
| Aggregate charging power | 8.0 MW |
| Dedicated solar plant | 23.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 10.2 km / 74 kWh |
| Lowest traversal charging margin | line-1: 45 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $390 M |
| Stations | $90 M |
| Depots | $54 M |
| Rolling stock | $117 M |
| Dedicated solar plant | $19 M |
| Residual train control | $2.0 M |
| Charging microgrids | $1.8 M |
| EPC / project services | $46 M |
| **Total city programme** | **$720 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $148 M (20.6%) |
| Domestic / local capital | $572 M (79.4%) |
| Annual public construction commitment | $100 M / yr for 10 years |
| Annual post-grace debt service | $92 M / yr |
| External capital saved vs default turnkey sensitivity | $1.15 bn |
| Capital + lifetime external interest saved | $2.63 bn |
| Annual OPEX | $17 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 2 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 241 assets / 1,483 tasks | [`jalalabad-af-operations-manifest.json`](operations/jalalabad-af-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`jalalabad-af.toml`](jalalabad-af.toml) | Expanded simulator scenario |
| [`jalalabad-af.corridor.geojson`](jalalabad-af.corridor.geojson) | GIS corridor and stations |
| [`jalalabad-af.design-quality.yaml`](jalalabad-af.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh jalalabad-af
```
