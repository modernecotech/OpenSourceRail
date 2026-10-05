# Hama — Urban Rail Network

**Country:** SY · **Population:** 600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Hama-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.22 bn (88.6%) of external capital** and **$1.58 bn of external interest**. Capital plus saved interest totals **$2.80 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **44.726 km to 35.904 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **19 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **134 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **134 light-metro-3car trainsets / 402 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Hama rail network on OpenStreetMap](hama-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 19 / 1 |
| Route length | 41.7 km double track |
| Direct transfers / reachable line pairs | 100.0% / 100.0% |
| Residents within 800 m radial station catchments | 135,776 (2020 raster; 24.1% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 134 × 3-car `light-metro-3car` trainsets (120 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 17.8 km | 7 | 54 | NW Outer ↔ SE Mid |
| line-2 |  9.8 km | 6 | 34 | S Mid ↔ NE Mid |
| line-3 | 14.1 km | 6 | 46 | W Outer ↔ E Mid |
| **Total** | **41.7 km** | **19 unique** | **134** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 19,400 train-km/day |
| Annual traction demand | 91.8 GWh |
| Station/depot PV / storage | 19.5 MW / 127.5 MWh |
| Aggregate charging power | 9.0 MW |
| Dedicated solar plant | 25.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 7.0 km / 56 kWh |
| Lowest traversal charging margin | line-1: 38 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $423 M |
| Stations | $95 M |
| Depots | $55 M |
| Rolling stock | $121 M |
| Dedicated solar plant | $21 M |
| Residual train control | $2.1 M |
| Charging microgrids | $1.9 M |
| EPC / project services | $49 M |
| **Total city programme** | **$766 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $157 M (20.4%) |
| Domestic / local capital | $610 M (79.6%) |
| Annual public construction commitment | $117 M / yr for 10 years |
| Annual post-grace debt service | $108 M / yr |
| External capital saved vs default turnkey sensitivity | $1.22 bn |
| Capital + lifetime external interest saved | $2.80 bn |
| Annual OPEX | $18 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 4 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 256 assets / 1,556 tasks | [`hama-operations-manifest.json`](operations/hama-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`hama.toml`](hama.toml) | Expanded simulator scenario |
| [`hama.corridor.geojson`](hama.corridor.geojson) | GIS corridor and stations |
| [`hama.design-quality.yaml`](hama.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh hama
```
