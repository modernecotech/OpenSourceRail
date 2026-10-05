# Mukalla — Urban Rail Network

**Country:** YE · **Population:** 550,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Mukalla-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$7.35 bn (90.8%) of external capital** and **$9.50 bn of external interest**. Capital plus saved interest totals **$16.85 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **44.723 km to 42.781 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **44 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **211 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **211 light-metro-3car trainsets / 633 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Mukalla rail network on OpenStreetMap](mukalla-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 44 / 5 |
| Route length | 60.6 km double track |
| Coverage / transfer reachability | 59.2% / 100% |
| Estimated station catchment | 325,600 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 211 × 3-car `light-metro-3car` trainsets (190 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 15.7 km | 17 | 67 | SW Mid ↔ NE Mid |
| line-2 | 19.0 km | 12 | 64 | E Mid ↔ SW Mid |
| line-3 | 25.8 km | 15 | 80 | NE Outer ↔ SW Mid |
| **Total** | **60.6 km** | **44 unique** | **211** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 28,169 train-km/day |
| Annual traction demand | 133.2 GWh |
| Station/depot PV / storage | 27.0 MW / 140.0 MWh |
| Aggregate charging power | 21.5 MW |
| Dedicated solar plant | 38.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 7.0 km / 57 kWh |
| Lowest traversal charging margin | line-3: 73 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $3.61 bn |
| Stations | $306 M |
| Depots | $66 M |
| Rolling stock | $190 M |
| Dedicated solar plant | $31 M |
| Residual train control | $3.0 M |
| Charging microgrids | $4.5 M |
| EPC / project services | $292 M |
| **Total city programme** | **$4.50 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $746 M (16.6%) |
| Domestic / local capital | $3.75 bn (83.4%) |
| Annual public construction commitment | $649 M / yr for 10 years |
| Annual post-grace debt service | $590 M / yr |
| External capital saved vs default turnkey sensitivity | $7.35 bn |
| Capital + lifetime external interest saved | $16.85 bn |
| Annual OPEX | $90 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 4 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 469 assets / 2,710 tasks | [`mukalla-operations-manifest.json`](operations/mukalla-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`mukalla.toml`](mukalla.toml) | Expanded simulator scenario |
| [`mukalla.corridor.geojson`](mukalla.corridor.geojson) | GIS corridor and stations |
| [`mukalla.design-quality.yaml`](mukalla.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh mukalla
```
