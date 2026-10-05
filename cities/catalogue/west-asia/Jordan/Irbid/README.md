# Irbid — Urban Rail Network

**Country:** JO · **Population:** 600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Irbid-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.06 bn (88.4%) of external capital** and **$1.30 bn of external interest**. Capital plus saved interest totals **$2.37 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **45.087 km to 34.784 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **17 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **121 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **121 light-metro-3car trainsets / 363 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Irbid rail network on OpenStreetMap](irbid-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 17 / 2 |
| Route length | 38.1 km double track |
| Coverage / transfer reachability | 49.3% / 100% |
| Estimated station catchment | 295,800 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 121 × 3-car `light-metro-3car` trainsets (108 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 11.0 km | 5 | 34 | S Mid ↔ N Outer |
| line-2 | 10.4 km | 5 | 34 | E Mid ↔ W Mid |
| line-3 | 16.7 km | 7 | 53 | NE Outer ↔ SW Outer |
| **Total** | **38.1 km** | **17 unique** | **121** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 17,721 train-km/day |
| Annual traction demand | 83.8 GWh |
| Station/depot PV / storage | 18.9 MW / 126.5 MWh |
| Aggregate charging power | 8.0 MW |
| Dedicated solar plant | 26.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 7.7 km / 55 kWh |
| Lowest traversal charging margin | line-1: 35 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $350 M |
| Stations | $88 M |
| Depots | $52 M |
| Rolling stock | $109 M |
| Dedicated solar plant | $21 M |
| Residual train control | $1.9 M |
| Charging microgrids | $1.8 M |
| EPC / project services | $42 M |
| **Total city programme** | **$667 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $139 M (20.8%) |
| Domestic / local capital | $528 M (79.2%) |
| Annual public construction commitment | $59 M / yr for 5 years |
| Annual post-grace debt service | $42 M / yr |
| External capital saved vs default turnkey sensitivity | $1.06 bn |
| Capital + lifetime external interest saved | $2.37 bn |
| Annual OPEX | $23 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 3 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 231 assets / 1,401 tasks | [`irbid-operations-manifest.json`](operations/irbid-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`irbid.toml`](irbid.toml) | Expanded simulator scenario |
| [`irbid.corridor.geojson`](irbid.corridor.geojson) | GIS corridor and stations |
| [`irbid.design-quality.yaml`](irbid.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh irbid
```
