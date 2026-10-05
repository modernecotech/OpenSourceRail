# Khulna — Urban Rail Network

**Country:** BD · **Population:** 1,500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Khulna-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$11.69 bn (90.3%) of external capital** and **$14.65 bn of external interest**. Capital plus saved interest totals **$26.33 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **163.275 km to 165.803 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **91 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **280 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **280 metro-4car trainsets / 1120 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Khulna rail network on OpenStreetMap](khulna-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 91 / 11 |
| Route length | 193.4 km double track |
| Coverage / transfer reachability | 58.9% / 73% |
| Estimated station catchment | 883,500 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 280 × 4-car `metro-4car` trainsets (252 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 28.7 km | 13 | 53 | NW Outer ↔ S Mid |
| line-2 | 32.5 km | 16 | 61 | SW Mid ↔ NE Outer |
| line-3 | 31.6 km | 17 | 62 | SE Outer ↔ N Mid |
| line-4 | 16.6 km | 6 | 28 | NW Mid ↔ S Mid |
| line-5 | 24.8 km | 14 | 50 | SE Outer ↔ NW Mid |
| line-6 | 59.2 km | 25 | 26 | NW Mid ↔ W Mid |
| **Total** | **193.4 km** | **91 unique** | **280** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 76,183 train-km/day |
| Annual traction demand | 480.5 GWh |
| Station/depot PV / storage | 53.4 MW / 357.0 MWh |
| Aggregate charging power | 126.0 MW |
| Dedicated solar plant | 254.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 15.3 km / 153 kWh |
| Lowest traversal charging margin | line-4: 161 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $5.53 bn |
| Stations | $527 M |
| Depots | $124 M |
| Rolling stock | $314 M |
| Dedicated solar plant | $203 M |
| Residual train control | $9.7 M |
| Charging microgrids | $26 M |
| EPC / project services | $457 M |
| **Total city programme** | **$7.19 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.25 bn (17.4%) |
| Domestic / local capital | $5.94 bn (82.6%) |
| Annual public construction commitment | $630 M / yr for 7 years |
| Annual post-grace debt service | $506 M / yr |
| External capital saved vs default turnkey sensitivity | $11.69 bn |
| Capital + lifetime external interest saved | $26.33 bn |
| Annual OPEX | $149 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 16 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 781 assets / 4,152 tasks | [`khulna-operations-manifest.json`](operations/khulna-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`khulna.toml`](khulna.toml) | Expanded simulator scenario |
| [`khulna.corridor.geojson`](khulna.corridor.geojson) | GIS corridor and stations |
| [`khulna.design-quality.yaml`](khulna.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh khulna
```
