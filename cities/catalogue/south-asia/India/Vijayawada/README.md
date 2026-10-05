# Vijayawada — Urban Rail Network

**Country:** IN · **Population:** 1,500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Vijayawada-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$7.09 bn (89.7%) of external capital** and **$8.72 bn of external interest**. Capital plus saved interest totals **$15.82 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **178.684 km to 156.174 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **64 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **245 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **245 metro-4car trainsets / 980 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Vijayawada rail network on OpenStreetMap](vijayawada-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 64 / 13 |
| Route length | 198.0 km double track |
| Coverage / transfer reachability | 72.6% / 87% |
| Estimated station catchment | 1,089,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 245 × 4-car `metro-4car` trainsets (219 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 27.4 km | 11 | 46 | NW Outer ↔ SE Mid |
| line-2 | 22.8 km | 8 | 37 | NE Mid ↔ SW Outer |
| line-3 | 35.4 km | 12 | 59 | E Outer ↔ W Outer |
| line-4 | 23.6 km | 9 | 41 | SE Inner ↔ NW Outer |
| line-5 | 21.1 km | 7 | 34 | E Inner ↔ S Outer |
| line-6 | 67.8 km | 17 | 28 | NW Mid ↔ W Mid |
| **Total** | **198.0 km** | **64 unique** | **245** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 76,302 train-km/day |
| Annual traction demand | 481.3 GWh |
| Station/depot PV / storage | 44.4 MW / 312.0 MWh |
| Aggregate charging power | 81.0 MW |
| Dedicated solar plant | 264.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 12.9 km / 129 kWh |
| Lowest traversal charging margin | line-5: 161 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $3.10 bn |
| Stations | $392 M |
| Depots | $118 M |
| Rolling stock | $274 M |
| Dedicated solar plant | $212 M |
| Residual train control | $9.9 M |
| Charging microgrids | $17 M |
| EPC / project services | $274 M |
| **Total city programme** | **$4.40 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $817 M (18.6%) |
| Domestic / local capital | $3.58 bn (81.4%) |
| Annual public construction commitment | $386 M / yr for 5 years |
| Annual post-grace debt service | $273 M / yr |
| External capital saved vs default turnkey sensitivity | $7.09 bn |
| Capital + lifetime external interest saved | $15.82 bn |
| Annual OPEX | $96 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 8 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 603 assets / 3,334 tasks | [`vijayawada-operations-manifest.json`](operations/vijayawada-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`vijayawada.toml`](vijayawada.toml) | Expanded simulator scenario |
| [`vijayawada.corridor.geojson`](vijayawada.corridor.geojson) | GIS corridor and stations |
| [`vijayawada.design-quality.yaml`](vijayawada.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh vijayawada
```
