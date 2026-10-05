# Damascus — Urban Rail Network

**Country:** SY · **Population:** 2,503,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Damascus-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.90 bn (89.0%) of external capital** and **$5.04 bn of external interest**. Capital plus saved interest totals **$8.94 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **165.310 km to 131.587 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **54 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **209 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **209 metro-4car trainsets / 836 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Damascus rail network on OpenStreetMap](damascus-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 54 / 11 |
| Route length | 168.6 km double track |
| Coverage / transfer reachability | 61.2% / 60% |
| Estimated station catchment | 1,531,836 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 209 × 4-car `metro-4car` trainsets (187 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 24.1 km | 9 | 40 | NE Outer ↔ SW Mid |
| line-2 | 24.6 km | 8 | 39 | SE Mid ↔ W Outer |
| line-3 | 21.9 km | 8 | 37 | S Mid ↔ N Outer |
| line-4 | 18.8 km | 7 | 31 | NW Outer ↔ SE Mid |
| line-5 | 23.4 km | 7 | 39 | NE Mid ↔ SW Outer |
| line-6 | 55.9 km | 15 | 23 | NW Mid ↔ W Mid |
| **Total** | **168.6 km** | **54 unique** | **209** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 65,396 train-km/day |
| Annual traction demand | 412.5 GWh |
| Station/depot PV / storage | 43.5 MW / 307.5 MWh |
| Aggregate charging power | 76.5 MW |
| Dedicated solar plant | 166.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 12.4 km / 133 kWh |
| Lowest traversal charging margin | line-4: 121 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.52 bn |
| Stations | $262 M |
| Depots | $111 M |
| Rolling stock | $234 M |
| Dedicated solar plant | $133 M |
| Residual train control | $8.4 M |
| Charging microgrids | $16 M |
| EPC / project services | $151 M |
| **Total city programme** | **$2.43 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $483 M (19.8%) |
| Domestic / local capital | $1.95 bn (80.2%) |
| Annual public construction commitment | $373 M / yr for 10 years |
| Annual post-grace debt service | $343 M / yr |
| External capital saved vs default turnkey sensitivity | $3.90 bn |
| Capital + lifetime external interest saved | $8.94 bn |
| Annual OPEX | $52 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 18 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 519 assets / 2,853 tasks | [`damascus-operations-manifest.json`](operations/damascus-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`damascus.toml`](damascus.toml) | Expanded simulator scenario |
| [`damascus.corridor.geojson`](damascus.corridor.geojson) | GIS corridor and stations |
| [`damascus.design-quality.yaml`](damascus.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh damascus
```
