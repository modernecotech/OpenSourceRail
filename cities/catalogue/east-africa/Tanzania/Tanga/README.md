# Tanga — Urban Rail Network

**Country:** TZ · **Population:** 400,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Tanga-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$6.61 bn (91.0%) of external capital** and **$8.28 bn of external interest**. Capital plus saved interest totals **$14.89 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **46.556 km to 36.150 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **22 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **132 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **132 light-metro-3car trainsets / 396 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Tanga rail network on OpenStreetMap](tanga-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 22 / 4 |
| Route length | 40.9 km double track |
| Coverage / transfer reachability | 49.8% / 100% |
| Estimated station catchment | 199,200 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 132 × 3-car `light-metro-3car` trainsets (119 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 17.7 km | 6 | 53 | NW Mid ↔ S Outer |
| line-2 | 13.1 km | 8 | 43 | W Mid ↔ NE Mid |
| line-3 | 10.0 km | 8 | 36 | NE Mid ↔ W Mid |
| **Total** | **40.9 km** | **22 unique** | **132** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 18,996 train-km/day |
| Annual traction demand | 89.9 GWh |
| Station/depot PV / storage | 20.7 MW / 129.5 MWh |
| Aggregate charging power | 11.0 MW |
| Dedicated solar plant | 35.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 6.4 km / 48 kWh |
| Lowest traversal charging margin | line-1: 50 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $3.43 bn |
| Stations | $136 M |
| Depots | $54 M |
| Rolling stock | $119 M |
| Dedicated solar plant | $28 M |
| Residual train control | $2.0 M |
| Charging microgrids | $2.4 M |
| EPC / project services | $262 M |
| **Total city programme** | **$4.03 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $650 M (16.1%) |
| Domestic / local capital | $3.38 bn (83.9%) |
| Annual public construction commitment | $383 M / yr for 7 years |
| Annual post-grace debt service | $309 M / yr |
| External capital saved vs default turnkey sensitivity | $6.61 bn |
| Capital + lifetime external interest saved | $14.89 bn |
| Annual OPEX | $80 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 3 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 269 assets / 1,595 tasks | [`tanga-operations-manifest.json`](operations/tanga-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`tanga.toml`](tanga.toml) | Expanded simulator scenario |
| [`tanga.corridor.geojson`](tanga.corridor.geojson) | GIS corridor and stations |
| [`tanga.design-quality.yaml`](tanga.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh tanga
```
