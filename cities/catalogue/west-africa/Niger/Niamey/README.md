# Niamey — Urban Rail Network

**Country:** NE · **Population:** 1,407,635 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Niamey-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.49 bn (89.2%) of external capital** and **$4.51 bn of external interest**. Capital plus saved interest totals **$8.00 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **145.326 km to 118.485 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **51 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **178 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **178 metro-4car trainsets / 712 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Niamey rail network on OpenStreetMap](niamey-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 51 / 10 |
| Route length | 142.0 km double track |
| Coverage / transfer reachability | 49.9% / 60% |
| Estimated station catchment | 702,409 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 178 × 4-car `metro-4car` trainsets (160 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 22.3 km | 8 | 36 | SE Outer ↔ N Mid |
| line-2 | 16.6 km | 8 | 32 | NW Mid ↔ E Mid |
| line-3 | 15.2 km | 7 | 29 | NE Mid ↔ SW Mid |
| line-4 | 19.1 km | 7 | 32 | W Mid ↔ SE Outer |
| line-5 | 18.2 km | 6 | 29 | NW Outer ↔ S Mid |
| line-6 | 50.6 km | 15 | 20 | NW Mid ↔ W Mid |
| **Total** | **142.0 km** | **51 unique** | **178** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 54,253 train-km/day |
| Annual traction demand | 342.2 GWh |
| Station/depot PV / storage | 42.9 MW / 304.5 MWh |
| Aggregate charging power | 73.5 MW |
| Dedicated solar plant | 116.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 7.3 km / 82 kWh |
| Lowest traversal charging margin | line-5: 120 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.38 bn |
| Stations | $238 M |
| Depots | $103 M |
| Rolling stock | $199 M |
| Dedicated solar plant | $93 M |
| Residual train control | $7.1 M |
| Charging microgrids | $15 M |
| EPC / project services | $136 M |
| **Total city programme** | **$2.17 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $423 M (19.4%) |
| Domestic / local capital | $1.75 bn (80.6%) |
| Annual public construction commitment | $180 M / yr for 10 years |
| Annual post-grace debt service | $162 M / yr |
| External capital saved vs default turnkey sensitivity | $3.49 bn |
| Capital + lifetime external interest saved | $8.00 bn |
| Annual OPEX | $47 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 20 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 469 assets / 2,519 tasks | [`niamey-operations-manifest.json`](operations/niamey-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`niamey.toml`](niamey.toml) | Expanded simulator scenario |
| [`niamey.corridor.geojson`](niamey.corridor.geojson) | GIS corridor and stations |
| [`niamey.design-quality.yaml`](niamey.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh niamey
```
