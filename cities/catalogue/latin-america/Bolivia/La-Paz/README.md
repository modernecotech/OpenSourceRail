# La-Paz — Urban Rail Network

**Country:** BO · **Population:** 1,815,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only La-Paz-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$5.04 bn (88.8%) of external capital** and **$6.19 bn of external interest**. Capital plus saved interest totals **$11.23 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **177.182 km to 156.397 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **72 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **262 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **262 metro-4car trainsets / 1048 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![La-Paz rail network on OpenStreetMap](la-paz-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 72 / 13 |
| Route length | 195.3 km double track |
| Direct transfers / reachable line pairs | 93.3% / 100.0% |
| Residents within 800 m radial station catchments | 499,505 (2020 raster; 26.6% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 262 × 4-car `metro-4car` trainsets (236 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 30.5 km | 12 | 50 | NE Outer ↔ SW Mid |
| line-2 | 30.4 km | 11 | 50 | W Outer ↔ E Outer |
| line-3 | 27.9 km | 11 | 47 | NE Mid ↔ SW Outer |
| line-4 | 30.3 km | 11 | 52 | SE Outer ↔ NW Mid |
| line-5 | 23.1 km | 11 | 43 | S Mid ↔ N Mid |
| line-6 | 53.1 km | 16 | 20 | W Mid ↔ W Mid |
| **Total** | **195.3 km** | **72 unique** | **262** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 78,477 train-km/day |
| Annual traction demand | 495.0 GWh |
| Station/depot PV / storage | 48.3 MW / 331.5 MWh |
| Aggregate charging power | 100.5 MW |
| Dedicated solar plant | 256.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-4: 13.9 km / 134 kWh |
| Lowest traversal charging margin | line-6: 223 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.90 bn |
| Stations | $415 M |
| Depots | $120 M |
| Rolling stock | $293 M |
| Dedicated solar plant | $205 M |
| Residual train control | $9.8 M |
| Charging microgrids | $21 M |
| EPC / project services | $193 M |
| **Total city programme** | **$3.15 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $634 M (20.1%) |
| Domestic / local capital | $2.52 bn (79.9%) |
| Annual public construction commitment | $341 M / yr for 5 years |
| Annual post-grace debt service | $254 M / yr |
| External capital saved vs default turnkey sensitivity | $5.04 bn |
| Capital + lifetime external interest saved | $11.23 bn |
| Annual OPEX | $76 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 15 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 668 assets / 3,654 tasks | [`la-paz-operations-manifest.json`](operations/la-paz-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`la-paz.toml`](la-paz.toml) | Expanded simulator scenario |
| [`la-paz.corridor.geojson`](la-paz.corridor.geojson) | GIS corridor and stations |
| [`la-paz.design-quality.yaml`](la-paz.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh la-paz
```
