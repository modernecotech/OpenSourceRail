# Raipur — Urban Rail Network

**Country:** IN · **Population:** 1,500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Raipur-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.33 bn (88.6%) of external capital** and **$4.09 bn of external interest**. Capital plus saved interest totals **$7.41 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **127.024 km to 107.147 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **48 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **196 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **196 metro-4car trainsets / 784 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Raipur rail network on OpenStreetMap](raipur-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 48 / 7 |
| Route length | 138.0 km double track |
| Coverage / transfer reachability | 37.6% / 40% |
| Estimated station catchment | 564,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 196 × 4-car `metro-4car` trainsets (174 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 28.7 km | 12 | 49 | E Outer ↔ W Outer |
| line-2 | 25.9 km | 9 | 41 | S Mid ↔ N Outer |
| line-3 | 12.7 km | 5 | 23 | NE Mid ↔ W Mid |
| line-4 | 19.8 km | 8 | 34 | SE Outer ↔ W Mid |
| line-5 | 21.5 km | 6 | 36 | NE Outer ↔ S Mid |
| line-6 | 29.5 km | 8 | 13 | E Inner ↔ E Inner |
| **Total** | **138.0 km** | **48 unique** | **196** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 57,329 train-km/day |
| Annual traction demand | 361.6 GWh |
| Station/depot PV / storage | 40.8 MW / 294.0 MWh |
| Aggregate charging power | 63.0 MW |
| Dedicated solar plant | 190.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 10.6 km / 105 kWh |
| Lowest traversal charging margin | line-5: 132 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.25 bn |
| Stations | $211 M |
| Depots | $107 M |
| Rolling stock | $220 M |
| Dedicated solar plant | $152 M |
| Residual train control | $6.9 M |
| Charging microgrids | $13 M |
| EPC / project services | $127 M |
| **Total city programme** | **$2.09 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $429 M (20.6%) |
| Domestic / local capital | $1.66 bn (79.4%) |
| Annual public construction commitment | $181 M / yr for 5 years |
| Annual post-grace debt service | $129 M / yr |
| External capital saved vs default turnkey sensitivity | $3.33 bn |
| Capital + lifetime external interest saved | $7.41 bn |
| Annual OPEX | $50 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 14 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 471 assets / 2,614 tasks | [`raipur-operations-manifest.json`](operations/raipur-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`raipur.toml`](raipur.toml) | Expanded simulator scenario |
| [`raipur.corridor.geojson`](raipur.corridor.geojson) | GIS corridor and stations |
| [`raipur.design-quality.yaml`](raipur.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh raipur
```
