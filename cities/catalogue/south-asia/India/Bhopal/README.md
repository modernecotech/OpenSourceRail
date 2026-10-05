# Bhopal — Urban Rail Network

**Country:** IN · **Population:** 2,400,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Bhopal-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.95 bn (89.0%) of external capital** and **$4.86 bn of external interest**. Capital plus saved interest totals **$8.82 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **172.859 km to 136.922 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **56 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **207 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **207 metro-4car trainsets / 828 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Bhopal rail network on OpenStreetMap](bhopal-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 56 / 11 |
| Route length | 163.1 km double track |
| Coverage / transfer reachability | 36.1% / 80% |
| Estimated station catchment | 866,400 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 207 × 4-car `metro-4car` trainsets (185 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 20.6 km | 8 | 36 | E Mid ↔ W Mid |
| line-2 | 18.0 km | 8 | 34 | S Mid ↔ N Mid |
| line-3 | 17.5 km | 7 | 30 | S Mid ↔ N Mid |
| line-4 | 30.6 km | 10 | 50 | SW Mid ↔ NE Outer |
| line-5 | 23.1 km | 7 | 36 | NW Mid ↔ SE Outer |
| line-6 | 53.2 km | 16 | 21 | NW Mid ↔ W Mid |
| **Total** | **163.1 km** | **56 unique** | **207** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 63,475 train-km/day |
| Annual traction demand | 400.4 GWh |
| Station/depot PV / storage | 44.1 MW / 310.5 MWh |
| Aggregate charging power | 79.5 MW |
| Dedicated solar plant | 159.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-4: 16.1 km / 173 kWh |
| Lowest traversal charging margin | line-5: 118 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.53 bn |
| Stations | $291 M |
| Depots | $108 M |
| Rolling stock | $232 M |
| Dedicated solar plant | $128 M |
| Residual train control | $8.2 M |
| Charging microgrids | $16 M |
| EPC / project services | $153 M |
| **Total city programme** | **$2.47 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $487 M (19.7%) |
| Domestic / local capital | $1.98 bn (80.3%) |
| Annual public construction commitment | $215 M / yr for 5 years |
| Annual post-grace debt service | $153 M / yr |
| External capital saved vs default turnkey sensitivity | $3.95 bn |
| Capital + lifetime external interest saved | $8.82 bn |
| Annual OPEX | $58 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 16 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 527 assets / 2,871 tasks | [`bhopal-operations-manifest.json`](operations/bhopal-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`bhopal.toml`](bhopal.toml) | Expanded simulator scenario |
| [`bhopal.corridor.geojson`](bhopal.corridor.geojson) | GIS corridor and stations |
| [`bhopal.design-quality.yaml`](bhopal.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh bhopal
```
