# Mbuji-Mayi — Urban Rail Network

**Country:** CD · **Population:** 2,500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Mbuji-Mayi-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.47 bn (88.8%) of external capital** and **$3.19 bn of external interest**. Capital plus saved interest totals **$5.65 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **102.734 km to 91.047 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **36 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**4 line-local depots** provide **131 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **131 metro-4car trainsets / 524 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Mbuji-Mayi rail network on OpenStreetMap](mbuji-mayi-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 4 / 36 / 4 |
| Route length | 105.3 km double track |
| Coverage / transfer reachability | 54.7% / 67% |
| Estimated station catchment | 1,367,500 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 131 × 4-car `metro-4car` trainsets (117 peak revenue) |
| Peak network throughput | 76,800 passengers/hour |
| Practical service capacity | 624,960 passenger-trips/day |
| Annual paid-trip planning range | 114.1–182.5 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 25.1 km | 9 | 40 | W Outer ↔ E Outer |
| line-2 | 15.6 km | 6 | 27 | SW Mid ↔ SE Mid |
| line-3 | 29.3 km | 10 | 50 | NE Outer ↔ SW Mid |
| line-4 | 35.3 km | 11 | 14 | NW Mid ↔ W Mid |
| **Total** | **105.3 km** | **36 unique** | **131** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,628 one-way journeys / 40,761 train-km/day |
| Annual traction demand | 257.1 GWh |
| Station/depot PV / storage | 28.4 MW / 202.0 MWh |
| Aggregate charging power | 48.0 MW |
| Dedicated solar plant | 136.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 14.0 km / 140 kWh |
| Lowest traversal charging margin | line-4: 152 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $960 M |
| Stations | $148 M |
| Depots | $71 M |
| Rolling stock | $147 M |
| Dedicated solar plant | $109 M |
| Residual train control | $5.3 M |
| Charging microgrids | $10 M |
| EPC / project services | $94 M |
| **Total city programme** | **$1.54 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $312 M (20.2%) |
| Domestic / local capital | $1.23 bn (79.8%) |
| Annual public construction commitment | $167 M / yr for 10 years |
| Annual post-grace debt service | $151 M / yr |
| External capital saved vs default turnkey sensitivity | $2.47 bn |
| Capital + lifetime external interest saved | $5.65 bn |
| Annual OPEX | $34 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 14 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 334 assets / 1,817 tasks | [`mbuji-mayi-operations-manifest.json`](operations/mbuji-mayi-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`mbuji-mayi.toml`](mbuji-mayi.toml) | Expanded simulator scenario |
| [`mbuji-mayi.corridor.geojson`](mbuji-mayi.corridor.geojson) | GIS corridor and stations |
| [`mbuji-mayi.design-quality.yaml`](mbuji-mayi.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh mbuji-mayi
```
