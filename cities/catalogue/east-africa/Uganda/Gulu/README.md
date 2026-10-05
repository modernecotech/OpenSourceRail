# Gulu — Urban Rail Network

**Country:** UG · **Population:** 350,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Gulu-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.36 bn (88.0%) of external capital** and **$1.70 bn of external interest**. Capital plus saved interest totals **$3.06 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **48.304 km to 44.423 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **19 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **172 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **172 light-metro-3car trainsets / 516 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Gulu rail network on OpenStreetMap](gulu-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 19 / 2 |
| Route length | 54.9 km double track |
| Coverage / transfer reachability | 46.7% / 67% |
| Estimated station catchment | 163,450 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 172 × 3-car `light-metro-3car` trainsets (155 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 12.3 km | 5 | 38 | SW Mid ↔ NE Mid |
| line-2 | 26.3 km | 9 | 82 | SE Outer ↔ NW Outer |
| line-3 | 16.4 km | 5 | 52 | W Outer ↔ NE Mid |
| **Total** | **54.9 km** | **19 unique** | **172** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 25,538 train-km/day |
| Annual traction demand | 120.8 GWh |
| Station/depot PV / storage | 18.6 MW / 132.0 MWh |
| Aggregate charging power | 15.0 MW |
| Dedicated solar plant | 57.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 10.9 km / 82 kWh |
| Lowest traversal charging margin | line-1: 185 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $460 M |
| Stations | $76 M |
| Depots | $61 M |
| Rolling stock | $155 M |
| Dedicated solar plant | $46 M |
| Residual train control | $2.7 M |
| Charging microgrids | $3.3 M |
| EPC / project services | $53 M |
| **Total city programme** | **$858 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $185 M (21.6%) |
| Domestic / local capital | $672 M (78.4%) |
| Annual public construction commitment | $103 M / yr for 7 years |
| Annual post-grace debt service | $87 M / yr |
| External capital saved vs default turnkey sensitivity | $1.36 bn |
| Capital + lifetime external interest saved | $3.06 bn |
| Annual OPEX | $21 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 4 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 296 assets / 1,891 tasks | [`gulu-operations-manifest.json`](operations/gulu-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`gulu.toml`](gulu.toml) | Expanded simulator scenario |
| [`gulu.corridor.geojson`](gulu.corridor.geojson) | GIS corridor and stations |
| [`gulu.design-quality.yaml`](gulu.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh gulu
```
