# Meru-Ke — Urban Rail Network

**Country:** KE · **Population:** 250,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Meru-Ke-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$658 M (89.9%) of external capital** and **$825 M of external interest**. Capital plus saved interest totals **$1.48 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **22.876 km to 17.610 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **9 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **51 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **51 tram-2car trainsets / 102 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Meru-Ke rail network on OpenStreetMap](meru-ke-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 9 / 1 |
| Route length | 22.8 km double track |
| Coverage / transfer reachability | 68.8% / 100% |
| Estimated station catchment | 172,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 51 × 2-car `tram-2car` trainsets (44 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 11.5 km | 4 | 24 | S Outer ↔ N Outer |
| line-2 |  3.2 km | 2 | 9 | NE Inner ↔ NW Mid |
| line-3 |  8.1 km | 3 | 18 | E Inner ↔ SW Outer |
| **Total** | **22.8 km** | **9 unique** | **51** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 10,592 train-km/day |
| Annual traction demand | 33.4 GWh |
| Station/depot PV / storage | 16.5 MW / 122.5 MWh |
| Aggregate charging power | 4.0 MW |
| Dedicated solar plant | 3.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 8.1 km / 40 kWh |
| Lowest traversal charging margin | line-3: 21 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $268 M |
| Stations | $39 M |
| Depots | $41 M |
| Rolling stock | $29 M |
| Dedicated solar plant | $2.4 M |
| Residual train control | $1.1 M |
| Charging microgrids | $950 k |
| EPC / project services | $26 M |
| **Total city programme** | **$407 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $74 M (18.2%) |
| Domestic / local capital | $333 M (81.8%) |
| Annual public construction commitment | $43 M / yr for 7 years |
| Annual post-grace debt service | $36 M / yr |
| External capital saved vs default turnkey sensitivity | $658 M |
| Capital + lifetime external interest saved | $1.48 bn |
| Annual OPEX | $10 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 1 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 110 assets / 616 tasks | [`meru-ke-operations-manifest.json`](operations/meru-ke-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`meru-ke.toml`](meru-ke.toml) | Expanded simulator scenario |
| [`meru-ke.corridor.geojson`](meru-ke.corridor.geojson) | GIS corridor and stations |
| [`meru-ke.design-quality.yaml`](meru-ke.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh meru-ke
```
