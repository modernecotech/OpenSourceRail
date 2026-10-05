# Jizan — Urban Rail Network

**Country:** SA · **Population:** 400,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Jizan-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.43 bn (88.7%) of external capital** and **$1.76 bn of external interest**. Capital plus saved interest totals **$3.18 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **38.866 km to 36.505 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **25 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **151 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **151 light-metro-3car trainsets / 453 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Jizan rail network on OpenStreetMap](jizan-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 25 / 3 |
| Route length | 45.3 km double track |
| Direct transfers / reachable line pairs | 100.0% / 100.0% |
| Residents within 800 m radial station catchments | 21,927 (2020 raster; 24.1% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 151 × 3-car `light-metro-3car` trainsets (135 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 20.4 km | 11 | 69 | SE Mid ↔ N Outer |
| line-2 |  7.4 km | 5 | 24 | W Mid ↔ NE Inner |
| line-3 | 17.5 km | 9 | 58 | SE Outer ↔ NW Inner |
| **Total** | **45.3 km** | **25 unique** | **151** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 21,058 train-km/day |
| Annual traction demand | 99.6 GWh |
| Station/depot PV / storage | 21.6 MW / 131.0 MWh |
| Aggregate charging power | 12.5 MW |
| Dedicated solar plant | 27.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 6.6 km / 53 kWh |
| Lowest traversal charging margin | line-2: 33 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $469 M |
| Stations | $148 M |
| Depots | $57 M |
| Rolling stock | $136 M |
| Dedicated solar plant | $22 M |
| Residual train control | $2.3 M |
| Charging microgrids | $2.6 M |
| EPC / project services | $57 M |
| **Total city programme** | **$895 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $183 M (20.4%) |
| Domestic / local capital | $712 M (79.6%) |
| Annual public construction commitment | $62 M / yr for 5 years |
| Annual post-grace debt service | $43 M / yr |
| External capital saved vs default turnkey sensitivity | $1.43 bn |
| Capital + lifetime external interest saved | $3.18 bn |
| Annual OPEX | $48 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 5 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 306 assets / 1,823 tasks | [`jizan-operations-manifest.json`](operations/jizan-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`jizan.toml`](jizan.toml) | Expanded simulator scenario |
| [`jizan.corridor.geojson`](jizan.corridor.geojson) | GIS corridor and stations |
| [`jizan.design-quality.yaml`](jizan.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh jizan
```
