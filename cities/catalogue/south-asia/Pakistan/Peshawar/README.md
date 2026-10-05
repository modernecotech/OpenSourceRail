# Peshawar — Urban Rail Network

**Country:** PK · **Population:** 2,300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Peshawar-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.07 bn (89.1%) of external capital** and **$5.10 bn of external interest**. Capital plus saved interest totals **$9.18 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **147.594 km to 126.317 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **55 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**5 line-local depots** provide **205 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **205 metro-4car trainsets / 820 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Peshawar rail network on OpenStreetMap](peshawar-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 5 / 55 / 8 |
| Route length | 171.3 km double track |
| Coverage / transfer reachability | 50.8% / 50% |
| Estimated station catchment | 1,168,400 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 205 × 4-car `metro-4car` trainsets (183 peak revenue) |
| Peak network throughput | 96,000 passengers/hour |
| Practical service capacity | 803,520 passenger-trips/day |
| Annual paid-trip planning range | 146.6–234.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 28.7 km | 10 | 47 | W Mid ↔ E Outer |
| line-2 | 27.9 km | 9 | 45 | SW Outer ↔ NE Mid |
| line-3 | 30.8 km | 10 | 51 | NW Outer ↔ SE Mid |
| line-4 | 22.2 km | 8 | 37 | NE Mid ↔ S Mid |
| line-5 | 61.7 km | 18 | 25 | W Mid ↔ W Mid |
| **Total** | **171.3 km** | **55 unique** | **205** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,092 one-way journeys / 65,320 train-km/day |
| Annual traction demand | 412.0 GWh |
| Station/depot PV / storage | 37.6 MW / 263.0 MWh |
| Aggregate charging power | 70.5 MW |
| Dedicated solar plant | 173.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-5: 14.5 km / 156 kWh |
| Lowest traversal charging margin | line-2: 123 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.67 bn |
| Stations | $222 M |
| Depots | $99 M |
| Rolling stock | $230 M |
| Dedicated solar plant | $138 M |
| Residual train control | $8.6 M |
| Charging microgrids | $15 M |
| EPC / project services | $157 M |
| **Total city programme** | **$2.54 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $496 M (19.5%) |
| Domestic / local capital | $2.04 bn (80.5%) |
| Annual public construction commitment | $350 M / yr for 7 years |
| Annual post-grace debt service | $300 M / yr |
| External capital saved vs default turnkey sensitivity | $4.07 bn |
| Capital + lifetime external interest saved | $9.18 bn |
| Annual OPEX | $57 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 21 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 512 assets / 2,817 tasks | [`peshawar-operations-manifest.json`](operations/peshawar-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`peshawar.toml`](peshawar.toml) | Expanded simulator scenario |
| [`peshawar.corridor.geojson`](peshawar.corridor.geojson) | GIS corridor and stations |
| [`peshawar.design-quality.yaml`](peshawar.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh peshawar
```
