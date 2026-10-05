# Biratnagar — Urban Rail Network

**Country:** NP · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Biratnagar-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$836 M (90.1%) of external capital** and **$1.05 bn of external interest**. Capital plus saved interest totals **$1.88 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **26.684 km to 20.217 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **11 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **55 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **55 tram-2car trainsets / 110 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Biratnagar rail network on OpenStreetMap](biratnagar-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 11 / 1 |
| Route length | 25.3 km double track |
| Coverage / transfer reachability | 57.5% / 33% |
| Estimated station catchment | 172,500 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 55 × 2-car `tram-2car` trainsets (48 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 12.0 km | 5 | 25 | S Outer ↔ N Outer |
| line-2 |  4.3 km | 2 | 10 | SE Outer ↔ E Mid |
| line-3 |  9.0 km | 4 | 20 | W Outer ↔ NE Mid |
| **Total** | **25.3 km** | **11 unique** | **55** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 11,784 train-km/day |
| Annual traction demand | 37.2 GWh |
| Station/depot PV / storage | 17.4 MW / 124.0 MWh |
| Aggregate charging power | 5.5 MW |
| Dedicated solar plant | 4.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 4.3 km / 21 kWh |
| Lowest traversal charging margin | line-2: 26 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $351 M |
| Stations | $53 M |
| Depots | $41 M |
| Rolling stock | $31 M |
| Dedicated solar plant | $3.5 M |
| Residual train control | $1.3 M |
| Charging microgrids | $1.2 M |
| EPC / project services | $34 M |
| **Total city programme** | **$516 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $92 M (17.9%) |
| Domestic / local capital | $424 M (82.1%) |
| Annual public construction commitment | $42 M / yr for 7 years |
| Annual post-grace debt service | $33 M / yr |
| External capital saved vs default turnkey sensitivity | $836 M |
| Capital + lifetime external interest saved | $1.88 bn |
| Annual OPEX | $12 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 2 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 126 assets / 693 tasks | [`biratnagar-operations-manifest.json`](operations/biratnagar-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`biratnagar.toml`](biratnagar.toml) | Expanded simulator scenario |
| [`biratnagar.corridor.geojson`](biratnagar.corridor.geojson) | GIS corridor and stations |
| [`biratnagar.design-quality.yaml`](biratnagar.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh biratnagar
```
