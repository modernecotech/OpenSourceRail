# Najran — Urban Rail Network

**Country:** SA · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Najran-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.60 bn (88.9%) of external capital** and **$1.97 bn of external interest**. Capital plus saved interest totals **$3.57 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **43.784 km to 39.320 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **19 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **160 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **160 light-metro-3car trainsets / 480 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Najran rail network on OpenStreetMap](najran-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 19 / 2 |
| Route length | 51.9 km double track |
| Direct transfers / reachable line pairs | 66.7% / 100.0% |
| Residents within 800 m radial station catchments | 45,372 (2020 raster; 16.6% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 160 × 3-car `light-metro-3car` trainsets (144 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 19.0 km | 7 | 60 | W Outer ↔ NE Mid |
| line-2 | 20.2 km | 7 | 61 | E Outer ↔ SW Outer |
| line-3 | 12.7 km | 5 | 39 | SE Mid ↔ N Outer |
| **Total** | **51.9 km** | **19 unique** | **160** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 24,112 train-km/day |
| Annual traction demand | 114.1 GWh |
| Station/depot PV / storage | 19.8 MW / 128.0 MWh |
| Aggregate charging power | 9.5 MW |
| Dedicated solar plant | 37.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 5.0 km / 40 kWh |
| Lowest traversal charging margin | line-3: 31 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $615 M |
| Stations | $86 M |
| Depots | $59 M |
| Rolling stock | $144 M |
| Dedicated solar plant | $30 M |
| Residual train control | $2.6 M |
| Charging microgrids | $2.0 M |
| EPC / project services | $64 M |
| **Total city programme** | **$1.00 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $200 M (19.9%) |
| Domestic / local capital | $802 M (80.1%) |
| Annual public construction commitment | $70 M / yr for 5 years |
| Annual post-grace debt service | $48 M / yr |
| External capital saved vs default turnkey sensitivity | $1.60 bn |
| Capital + lifetime external interest saved | $3.57 bn |
| Annual OPEX | $49 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 7 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 286 assets / 1,797 tasks | [`najran-operations-manifest.json`](operations/najran-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`najran.toml`](najran.toml) | Expanded simulator scenario |
| [`najran.corridor.geojson`](najran.corridor.geojson) | GIS corridor and stations |
| [`najran.design-quality.yaml`](najran.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh najran
```
