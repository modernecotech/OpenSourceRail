# San-Salvador — Urban Rail Network

**Country:** SV · **Population:** 1,800,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only San-Salvador-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$5.28 bn (88.6%) of external capital** and **$6.49 bn of external interest**. Capital plus saved interest totals **$11.77 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **188.033 km to 158.225 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **76 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **294 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **294 metro-4car trainsets / 1176 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![San-Salvador rail network on OpenStreetMap](san-salvador-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 76 / 13 |
| Route length | 232.1 km double track |
| Coverage / transfer reachability | 47.6% / 73% |
| Estimated station catchment | 856,800 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 294 × 4-car `metro-4car` trainsets (264 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 27.3 km | 11 | 47 | W Mid ↔ E Mid |
| line-2 | 32.1 km | 12 | 52 | N Mid ↔ SW Outer |
| line-3 | 34.3 km | 10 | 57 | SE Outer ↔ NW Mid |
| line-4 | 36.2 km | 12 | 60 | SW Mid ↔ NE Outer |
| line-5 | 29.7 km | 9 | 48 | S Mid ↔ NW Outer |
| line-6 | 72.4 km | 22 | 30 | NW Mid ↔ NW Mid |
| **Total** | **232.1 km** | **76 unique** | **294** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 91,095 train-km/day |
| Annual traction demand | 574.6 GWh |
| Station/depot PV / storage | 48.0 MW / 330.0 MWh |
| Aggregate charging power | 97.5 MW |
| Dedicated solar plant | 321.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-4: 12.6 km / 126 kWh |
| Lowest traversal charging margin | line-5: 188 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.01 bn |
| Stations | $352 M |
| Depots | $127 M |
| Rolling stock | $329 M |
| Dedicated solar plant | $258 M |
| Residual train control | $12 M |
| Charging microgrids | $20 M |
| EPC / project services | $200 M |
| **Total city programme** | **$3.31 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $679 M (20.5%) |
| Domestic / local capital | $2.63 bn (79.5%) |
| Annual public construction commitment | $378 M / yr for 5 years |
| Annual post-grace debt service | $286 M / yr |
| External capital saved vs default turnkey sensitivity | $5.28 bn |
| Capital + lifetime external interest saved | $11.77 bn |
| Annual OPEX | $81 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 22 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 720 assets / 3,999 tasks | [`san-salvador-operations-manifest.json`](operations/san-salvador-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`san-salvador.toml`](san-salvador.toml) | Expanded simulator scenario |
| [`san-salvador.corridor.geojson`](san-salvador.corridor.geojson) | GIS corridor and stations |
| [`san-salvador.design-quality.yaml`](san-salvador.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh san-salvador
```
