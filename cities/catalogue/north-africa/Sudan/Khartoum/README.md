# Khartoum — Urban Rail Network

**Country:** SD · **Population:** 5,829,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Khartoum-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$9.53 bn (88.0%) of external capital** and **$12.31 bn of external interest**. Capital plus saved interest totals **$21.84 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **357.668 km to 287.692 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **116 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**9 line-local depots** provide **542 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **542 metro-6car trainsets / 3252 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Khartoum rail network on OpenStreetMap](khartoum-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 116 / 22 |
| Route length | 357.2 km double track |
| Coverage / transfer reachability | 42.1% / 53% |
| Estimated station catchment | 2,454,009 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 542 × 6-car `metro-6car` trainsets (490 peak revenue) |
| Peak network throughput | 259,200 passengers/hour |
| Practical service capacity | 2,276,640 passenger-trips/day |
| Annual paid-trip planning range | 415.5–664.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 33.1 km | 11 | 63 | SE Mid ↔ NW Mid |
| line-2 | 29.8 km | 9 | 54 | E Mid ↔ W Mid |
| line-3 | 49.0 km | 16 | 95 | NW Mid ↔ SE Outer |
| line-4 | 25.9 km | 11 | 51 | NW Mid ↔ S Mid |
| line-5 | 34.1 km | 11 | 63 | N Mid ↔ SW Mid |
| line-6 | 28.6 km | 11 | 52 | S Mid ↔ NE Mid |
| line-7 | 35.8 km | 11 | 64 | W Outer ↔ SE Mid |
| line-8 | 30.0 km | 10 | 57 | W Mid ↔ N Outer |
| line-9 | 90.9 km | 26 | 43 | NW Mid ↔ NW Mid |
| **Total** | **357.2 km** | **116 unique** | **542** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,952 one-way journeys / 144,993 train-km/day |
| Annual traction demand | 1,371.8 GWh |
| Station/depot PV / storage | 73.8 MW / 552.0 MWh |
| Aggregate charging power | 210.0 MW |
| Dedicated solar plant | 635.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-8: 15.0 km / 242 kWh |
| Lowest traversal charging margin | line-8: 153 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $3.41 bn |
| Stations | $528 M |
| Depots | $246 M |
| Rolling stock | $911 M |
| Dedicated solar plant | $508 M |
| Residual train control | $18 M |
| Charging microgrids | $43 M |
| EPC / project services | $361 M |
| **Total city programme** | **$6.02 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.31 bn (21.7%) |
| Domestic / local capital | $4.71 bn (78.3%) |
| Annual public construction commitment | $719 M / yr for 10 years |
| Annual post-grace debt service | $655 M / yr |
| External capital saved vs default turnkey sensitivity | $9.53 bn |
| Capital + lifetime external interest saved | $21.84 bn |
| Annual OPEX | $137 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 46 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,210 assets / 6,975 tasks | [`khartoum-operations-manifest.json`](operations/khartoum-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`khartoum.toml`](khartoum.toml) | Expanded simulator scenario |
| [`khartoum.corridor.geojson`](khartoum.corridor.geojson) | GIS corridor and stations |
| [`khartoum.design-quality.yaml`](khartoum.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh khartoum
```
