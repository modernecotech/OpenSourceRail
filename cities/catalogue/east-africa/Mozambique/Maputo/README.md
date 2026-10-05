# Maputo — Urban Rail Network

**Country:** MZ · **Population:** 1,530,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Maputo-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.70 bn (88.6%) of external capital** and **$4.78 bn of external interest**. Capital plus saved interest totals **$8.48 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **114.490 km to 93.864 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **56 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **203 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **203 metro-4car trainsets / 812 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Maputo rail network on OpenStreetMap](maputo-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 56 / 10 |
| Route length | 158.2 km double track |
| Coverage / transfer reachability | 60.2% / 40% |
| Estimated station catchment | 921,060 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 203 × 4-car `metro-4car` trainsets (182 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 21.5 km | 8 | 36 | SW Mid ↔ NE Outer |
| line-2 | 20.4 km | 9 | 38 | SE Mid ↔ NW Mid |
| line-3 | 19.5 km | 8 | 35 | NE Outer ↔ SW Mid |
| line-4 | 27.4 km | 7 | 43 | S Mid ↔ NW Outer |
| line-5 | 17.9 km | 7 | 31 | E Mid ↔ W Mid |
| line-6 | 51.5 km | 17 | 20 | NW Mid ↔ W Mid |
| **Total** | **158.2 km** | **56 unique** | **203** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 61,569 train-km/day |
| Annual traction demand | 388.3 GWh |
| Station/depot PV / storage | 44.7 MW / 313.5 MWh |
| Aggregate charging power | 82.5 MW |
| Dedicated solar plant | 203.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-4: 9.0 km / 89 kWh |
| Lowest traversal charging margin | line-4: 165 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.37 bn |
| Stations | $287 M |
| Depots | $108 M |
| Rolling stock | $227 M |
| Dedicated solar plant | $163 M |
| Residual train control | $7.9 M |
| Charging microgrids | $17 M |
| EPC / project services | $141 M |
| **Total city programme** | **$2.32 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $475 M (20.5%) |
| Domestic / local capital | $1.84 bn (79.5%) |
| Annual public construction commitment | $258 M / yr for 10 years |
| Annual post-grace debt service | $233 M / yr |
| External capital saved vs default turnkey sensitivity | $3.70 bn |
| Capital + lifetime external interest saved | $8.48 bn |
| Annual OPEX | $52 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 26 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 524 assets / 2,842 tasks | [`maputo-operations-manifest.json`](operations/maputo-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`maputo.toml`](maputo.toml) | Expanded simulator scenario |
| [`maputo.corridor.geojson`](maputo.corridor.geojson) | GIS corridor and stations |
| [`maputo.design-quality.yaml`](maputo.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh maputo
```
