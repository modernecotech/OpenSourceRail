# Tripoli-Lb — Urban Rail Network

**Country:** LB · **Population:** 730,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Tripoli-Lb-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.64 bn (89.5%) of external capital** and **$2.08 bn of external interest**. Capital plus saved interest totals **$3.72 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **42.354 km to 37.696 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **16 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **127 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **127 light-metro-3car trainsets / 381 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Tripoli-Lb rail network on OpenStreetMap](tripoli-lb-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 16 / 2 |
| Route length | 41.0 km double track |
| Coverage / transfer reachability | 40.5% / 67% |
| Estimated station catchment | 295,650 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 127 × 3-car `light-metro-3car` trainsets (114 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 11.8 km | 4 | 36 | NW Mid ↔ SE Mid |
| line-2 | 17.0 km | 7 | 53 | NE Outer ↔ SW Mid |
| line-3 | 12.2 km | 5 | 38 | W Mid ↔ SE Outer |
| **Total** | **41.0 km** | **16 unique** | **127** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 19,059 train-km/day |
| Annual traction demand | 90.2 GWh |
| Station/depot PV / storage | 18.9 MW / 126.5 MWh |
| Aggregate charging power | 8.0 MW |
| Dedicated solar plant | 29.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 5.4 km / 39 kWh |
| Lowest traversal charging margin | line-1: 38 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $680 M |
| Stations | $78 M |
| Depots | $53 M |
| Rolling stock | $114 M |
| Dedicated solar plant | $24 M |
| Residual train control | $2.0 M |
| Charging microgrids | $1.8 M |
| EPC / project services | $65 M |
| **Total city programme** | **$1.02 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $193 M (19.0%) |
| Domestic / local capital | $825 M (81.0%) |
| Annual public construction commitment | $194 M / yr for 8 years |
| Annual post-grace debt service | $177 M / yr |
| External capital saved vs default turnkey sensitivity | $1.64 bn |
| Capital + lifetime external interest saved | $3.72 bn |
| Annual OPEX | $25 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 4 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 234 assets / 1,442 tasks | [`tripoli-lb-operations-manifest.json`](operations/tripoli-lb-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`tripoli-lb.toml`](tripoli-lb.toml) | Expanded simulator scenario |
| [`tripoli-lb.corridor.geojson`](tripoli-lb.corridor.geojson) | GIS corridor and stations |
| [`tripoli-lb.design-quality.yaml`](tripoli-lb.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh tripoli-lb
```
