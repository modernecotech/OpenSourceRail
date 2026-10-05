# Ranchi — Urban Rail Network

**Country:** IN · **Population:** 1,400,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Ranchi-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.84 bn (88.8%) of external capital** and **$5.95 bn of external interest**. Capital plus saved interest totals **$10.78 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **179.054 km to 151.885 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **69 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **246 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **246 metro-4car trainsets / 984 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Ranchi rail network on OpenStreetMap](ranchi-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 69 / 13 |
| Route length | 201.8 km double track |
| Coverage / transfer reachability | 45.8% / 53% |
| Estimated station catchment | 641,200 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 246 × 4-car `metro-4car` trainsets (221 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 31.7 km | 12 | 51 | NE Outer ↔ SW Mid |
| line-2 | 23.2 km | 9 | 40 | N Mid ↔ S Outer |
| line-3 | 21.4 km | 8 | 36 | SE Mid ↔ W Mid |
| line-4 | 26.9 km | 9 | 46 | E Outer ↔ SW Mid |
| line-5 | 25.0 km | 10 | 43 | NW Outer ↔ SE Mid |
| line-6 | 73.5 km | 21 | 30 | NW Mid ↔ W Mid |
| **Total** | **201.8 km** | **69 unique** | **246** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 76,738 train-km/day |
| Annual traction demand | 484.0 GWh |
| Station/depot PV / storage | 46.8 MW / 324.0 MWh |
| Aggregate charging power | 93.0 MW |
| Dedicated solar plant | 263.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 12.9 km / 129 kWh |
| Lowest traversal charging margin | line-3: 206 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.88 bn |
| Stations | $332 M |
| Depots | $118 M |
| Rolling stock | $276 M |
| Dedicated solar plant | $211 M |
| Residual train control | $10 M |
| Charging microgrids | $19 M |
| EPC / project services | $184 M |
| **Total city programme** | **$3.02 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $609 M (20.1%) |
| Domestic / local capital | $2.42 bn (79.9%) |
| Annual public construction commitment | $263 M / yr for 5 years |
| Annual post-grace debt service | $187 M / yr |
| External capital saved vs default turnkey sensitivity | $4.84 bn |
| Capital + lifetime external interest saved | $10.78 bn |
| Annual OPEX | $71 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 26 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 632 assets / 3,445 tasks | [`ranchi-operations-manifest.json`](operations/ranchi-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`ranchi.toml`](ranchi.toml) | Expanded simulator scenario |
| [`ranchi.corridor.geojson`](ranchi.corridor.geojson) | GIS corridor and stations |
| [`ranchi.design-quality.yaml`](ranchi.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh ranchi
```
