# Mandalay — Urban Rail Network

**Country:** MM · **Population:** 1,726,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Mandalay-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$23.40 bn (91.1%) of external capital** and **$30.22 bn of external interest**. Capital plus saved interest totals **$53.62 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **153.094 km to 164.721 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **78 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **283 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **283 metro-4car trainsets / 1132 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Mandalay rail network on OpenStreetMap](mandalay-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 78 / 15 |
| Route length | 233.0 km double track |
| Coverage / transfer reachability | 53.6% / 80% |
| Estimated station catchment | 925,136 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 283 × 4-car `metro-4car` trainsets (254 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 38.3 km | 14 | 65 | N Outer ↔ S Outer |
| line-2 | 30.8 km | 12 | 51 | NW Mid ↔ SE Outer |
| line-3 | 33.8 km | 11 | 56 | SW Outer ↔ NE Mid |
| line-4 | 21.8 km | 9 | 37 | NW Inner ↔ NE Outer |
| line-5 | 23.4 km | 8 | 39 | E Mid ↔ S Outer |
| line-6 | 85.0 km | 24 | 35 | NW Mid ↔ W Mid |
| **Total** | **233.0 km** | **78 unique** | **283** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 88,595 train-km/day |
| Annual traction demand | 558.8 GWh |
| Station/depot PV / storage | 46.5 MW / 322.5 MWh |
| Aggregate charging power | 91.5 MW |
| Dedicated solar plant | 217.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 20.7 km / 231 kWh |
| Lowest traversal charging margin | line-3: 101 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $12.32 bn |
| Stations | $382 M |
| Depots | $125 M |
| Rolling stock | $317 M |
| Dedicated solar plant | $174 M |
| Residual train control | $12 M |
| Charging microgrids | $19 M |
| EPC / project services | $922 M |
| **Total city programme** | **$14.27 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.30 bn (16.1%) |
| Domestic / local capital | $11.98 bn (83.9%) |
| Annual public construction commitment | $1.59 bn / yr for 10 years |
| Annual post-grace debt service | $1.42 bn / yr |
| External capital saved vs default turnkey sensitivity | $23.40 bn |
| Capital + lifetime external interest saved | $53.62 bn |
| Annual OPEX | $278 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 15 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 710 assets / 3,906 tasks | [`mandalay-operations-manifest.json`](operations/mandalay-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`mandalay.toml`](mandalay.toml) | Expanded simulator scenario |
| [`mandalay.corridor.geojson`](mandalay.corridor.geojson) | GIS corridor and stations |
| [`mandalay.design-quality.yaml`](mandalay.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh mandalay
```
