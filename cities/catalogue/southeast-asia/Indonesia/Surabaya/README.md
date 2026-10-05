# Surabaya — Urban Rail Network

**Country:** ID · **Population:** 3,009,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Surabaya-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$9.19 bn (87.5%) of external capital** and **$11.30 bn of external interest**. Capital plus saved interest totals **$20.49 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **234.615 km to 221.242 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **157 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**9 line-local depots** provide **544 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **544 metro-6car trainsets / 3264 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Surabaya rail network on OpenStreetMap](surabaya-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 157 / 21 |
| Route length | 291.9 km double track |
| Direct transfers / reachable line pairs | 91.7% / 100.0% |
| Residents within 800 m radial station catchments | unavailable — native population evidence required |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 544 × 6-car `metro-6car` trainsets (490 peak revenue) |
| Peak network throughput | 259,200 passengers/hour |
| Practical service capacity | 2,276,640 passenger-trips/day |
| Annual paid-trip planning range | 415.5–664.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 45.4 km | 23 | 95 | N Outer ↔ SE Mid |
| line-2 | 36.1 km | 19 | 78 | NE Outer ↔ S Mid |
| line-3 | 31.4 km | 14 | 62 | NE Mid ↔ SW Outer |
| line-4 | 28.1 km | 15 | 63 | N Inner ↔ S Outer |
| line-5 | 35.2 km | 18 | 74 | SE Mid ↔ NW Outer |
| line-6 | 19.8 km | 11 | 46 | SW Mid ↔ E Mid |
| line-7 | 19.7 km | 14 | 52 | W Mid ↔ E Inner |
| line-8 | 18.1 km | 9 | 39 | E Inner ↔ W Mid |
| line-9 | 58.3 km | 34 | 35 | W Mid ↔ SW Mid |
| **Total** | **291.9 km** | **157 unique** | **544** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,952 one-way journeys / 122,206 train-km/day |
| Annual traction demand | 1,156.2 GWh |
| Station/depot PV / storage | 86.7 MW / 638.0 MWh |
| Aggregate charging power | 296.0 MW |
| Dedicated solar plant | 659.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-5: 17.7 km / 265 kWh |
| Lowest traversal charging margin | line-8: 356 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.70 bn |
| Stations | $1.02 bn |
| Depots | $247 M |
| Rolling stock | $914 M |
| Dedicated solar plant | $527 M |
| Residual train control | $15 M |
| Charging microgrids | $60 M |
| EPC / project services | $347 M |
| **Total city programme** | **$5.84 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.31 bn (22.5%) |
| Domestic / local capital | $4.52 bn (77.5%) |
| Annual public construction commitment | $482 M / yr for 5 years |
| Annual post-grace debt service | $346 M / yr |
| External capital saved vs default turnkey sensitivity | $9.19 bn |
| Capital + lifetime external interest saved | $20.49 bn |
| Annual OPEX | $151 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 19 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,419 assets / 7,739 tasks | [`surabaya-operations-manifest.json`](operations/surabaya-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`surabaya.toml`](surabaya.toml) | Expanded simulator scenario |
| [`surabaya.corridor.geojson`](surabaya.corridor.geojson) | GIS corridor and stations |
| [`surabaya.design-quality.yaml`](surabaya.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh surabaya
```
