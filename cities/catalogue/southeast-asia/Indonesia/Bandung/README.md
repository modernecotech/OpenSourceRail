# Bandung — Urban Rail Network

**Country:** ID · **Population:** 2,615,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Bandung-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$6.06 bn (88.4%) of external capital** and **$7.45 bn of external interest**. Capital plus saved interest totals **$13.50 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **159.882 km to 140.667 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 1 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **126 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **345 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **345 metro-4car trainsets / 1380 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Bandung rail network on OpenStreetMap](bandung-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 126 / 13 |
| Route length | 218.7 km double track |
| Direct transfers / reachable line pairs | 100.0% / 100.0% |
| Residents within 800 m radial station catchments | unavailable — native population evidence required |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 345 × 4-car `metro-4car` trainsets (311 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 34.6 km | 15 | 61 | E Mid ↔ W Outer |
| line-2 | 39.0 km | 15 | 63 | SE Mid ↔ NW Outer |
| line-3 | 17.8 km | 27 | 75 | SW Inner ↔ NE Mid |
| line-4 | 29.7 km | 14 | 56 | S Mid ↔ N Outer |
| line-5 | 28.7 km | 14 | 54 | SE Mid ↔ N Outer |
| line-6 | 68.9 km | 41 | 36 | NW Mid ↔ W Mid |
| **Total** | **218.7 km** | **126 unique** | **345** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 85,661 train-km/day |
| Annual traction demand | 540.3 GWh |
| Station/depot PV / storage | 63.6 MW / 408.0 MWh |
| Aggregate charging power | 177.0 MW |
| Dedicated solar plant | 281.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 14.2 km / 142 kWh |
| Lowest traversal charging margin | line-2: 283 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.78 bn |
| Stations | $993 M |
| Depots | $136 M |
| Rolling stock | $386 M |
| Dedicated solar plant | $225 M |
| Residual train control | $11 M |
| Charging microgrids | $40 M |
| EPC / project services | $234 M |
| **Total city programme** | **$3.80 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $793 M (20.8%) |
| Domestic / local capital | $3.01 bn (79.2%) |
| Annual public construction commitment | $318 M / yr for 5 years |
| Annual post-grace debt service | $225 M / yr |
| External capital saved vs default turnkey sensitivity | $6.06 bn |
| Capital + lifetime external interest saved | $13.50 bn |
| Annual OPEX | $96 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 23 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,030 assets / 5,373 tasks | [`bandung-operations-manifest.json`](operations/bandung-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`bandung.toml`](bandung.toml) | Expanded simulator scenario |
| [`bandung.corridor.geojson`](bandung.corridor.geojson) | GIS corridor and stations |
| [`bandung.design-quality.yaml`](bandung.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh bandung
```
