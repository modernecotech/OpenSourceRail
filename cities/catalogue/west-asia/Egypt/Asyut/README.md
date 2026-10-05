# Asyut — Urban Rail Network

**Country:** EG · **Population:** 600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Asyut-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.10 bn (88.1%) of external capital** and **$1.35 bn of external interest**. Capital plus saved interest totals **$2.45 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **39.893 km to 34.687 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **15 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **148 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **148 light-metro-3car trainsets / 444 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Asyut rail network on OpenStreetMap](asyut-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 15 / 1 |
| Route length | 46.0 km double track |
| Coverage / transfer reachability | 48.4% / 33% |
| Estimated station catchment | 290,400 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 148 × 3-car `light-metro-3car` trainsets (132 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  7.0 km | 4 | 24 | S Inner ↔ NW Mid |
| line-2 | 17.9 km | 5 | 57 | W Inner ↔ NE Outer |
| line-3 | 21.1 km | 6 | 67 | SE Outer ↔ W Outer |
| **Total** | **46.0 km** | **15 unique** | **148** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 21,376 train-km/day |
| Annual traction demand | 101.1 GWh |
| Station/depot PV / storage | 17.4 MW / 128.0 MWh |
| Aggregate charging power | 11.0 MW |
| Dedicated solar plant | 33.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 15.7 km / 126 kWh |
| Lowest traversal charging margin | line-1: 117 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $376 M |
| Stations | $53 M |
| Depots | $57 M |
| Rolling stock | $133 M |
| Dedicated solar plant | $26 M |
| Residual train control | $2.3 M |
| Charging microgrids | $2.5 M |
| EPC / project services | $44 M |
| **Total city programme** | **$694 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $148 M (21.4%) |
| Domestic / local capital | $546 M (78.6%) |
| Annual public construction commitment | $74 M / yr for 5 years |
| Annual post-grace debt service | $56 M / yr |
| External capital saved vs default turnkey sensitivity | $1.10 bn |
| Capital + lifetime external interest saved | $2.45 bn |
| Annual OPEX | $19 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 3 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 249 assets / 1,600 tasks | [`asyut-operations-manifest.json`](operations/asyut-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`asyut.toml`](asyut.toml) | Expanded simulator scenario |
| [`asyut.corridor.geojson`](asyut.corridor.geojson) | GIS corridor and stations |
| [`asyut.design-quality.yaml`](asyut.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh asyut
```
