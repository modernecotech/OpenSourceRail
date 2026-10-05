# Hyderabad-Pk — Urban Rail Network

**Country:** PK · **Population:** 1,900,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Hyderabad-Pk-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$5.00 bn (89.5%) of external capital** and **$6.27 bn of external interest**. Capital plus saved interest totals **$11.27 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **157.380 km to 138.034 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 1 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **62 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **210 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **210 metro-4car trainsets / 840 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Hyderabad-Pk rail network on OpenStreetMap](hyderabad-pk-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 62 / 10 |
| Route length | 157.5 km double track |
| Direct transfers / reachable line pairs | 100.0% / 100.0% |
| Residents within 800 m radial station catchments | 1,002,245 (2020 raster; 36.5% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 210 × 4-car `metro-4car` trainsets (189 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 14.5 km | 9 | 32 | NE Mid ↔ SW Mid |
| line-2 | 16.2 km | 8 | 32 | W Mid ↔ SE Inner |
| line-3 | 15.7 km | 8 | 31 | S Mid ↔ N Mid |
| line-4 | 27.9 km | 12 | 49 | SE Mid ↔ N Outer |
| line-5 | 28.1 km | 10 | 45 | W Mid ↔ E Outer |
| line-6 | 55.0 km | 15 | 21 | W Mid ↔ W Mid |
| **Total** | **157.5 km** | **62 unique** | **210** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 60,434 train-km/day |
| Annual traction demand | 381.2 GWh |
| Station/depot PV / storage | 45.9 MW / 319.5 MWh |
| Aggregate charging power | 88.5 MW |
| Dedicated solar plant | 147.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-5: 10.5 km / 113 kWh |
| Lowest traversal charging margin | line-5: 182 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.06 bn |
| Stations | $359 M |
| Depots | $110 M |
| Rolling stock | $235 M |
| Dedicated solar plant | $118 M |
| Residual train control | $7.9 M |
| Charging microgrids | $18 M |
| EPC / project services | $195 M |
| **Total city programme** | **$3.10 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $584 M (18.8%) |
| Domestic / local capital | $2.52 bn (81.2%) |
| Annual public construction commitment | $431 M / yr for 7 years |
| Annual post-grace debt service | $369 M / yr |
| External capital saved vs default turnkey sensitivity | $5.00 bn |
| Capital + lifetime external interest saved | $11.27 bn |
| Annual OPEX | $68 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 14 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 560 assets / 3,006 tasks | [`hyderabad-pk-operations-manifest.json`](operations/hyderabad-pk-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`hyderabad-pk.toml`](hyderabad-pk.toml) | Expanded simulator scenario |
| [`hyderabad-pk.corridor.geojson`](hyderabad-pk.corridor.geojson) | GIS corridor and stations |
| [`hyderabad-pk.design-quality.yaml`](hyderabad-pk.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh hyderabad-pk
```
