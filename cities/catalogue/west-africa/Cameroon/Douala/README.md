# Douala — Urban Rail Network

**Country:** CM · **Population:** 3,900,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Douala-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$12.32 bn (89.9%) of external capital** and **$15.45 bn of external interest**. Capital plus saved interest totals **$27.77 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **170.992 km to 174.482 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **69 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**5 line-local depots** provide **296 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **296 metro-6car trainsets / 1776 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Douala rail network on OpenStreetMap](douala-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 5 / 69 / 10 |
| Route length | 193.4 km double track |
| Direct transfers / reachable line pairs | 80.0% / 100.0% |
| Residents within 800 m radial station catchments | 755,127 (2020 raster; 20.3% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 296 × 6-car `metro-6car` trainsets (267 peak revenue) |
| Peak network throughput | 144,000 passengers/hour |
| Practical service capacity | 1,205,280 passenger-trips/day |
| Annual paid-trip planning range | 220.0–351.9 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 35.7 km | 13 | 65 | SE Outer ↔ W Mid |
| line-2 | 39.9 km | 15 | 75 | NW Outer ↔ SE Mid |
| line-3 | 25.4 km | 9 | 46 | NE Mid ↔ S Mid |
| line-4 | 48.5 km | 15 | 89 | SE Inner ↔ NW Outer |
| line-5 | 43.9 km | 17 | 21 | E Inner ↔ N Inner |
| **Total** | **193.4 km** | **69 unique** | **296** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,092 one-way journeys / 79,743 train-km/day |
| Annual traction demand | 754.4 GWh |
| Station/depot PV / storage | 41.8 MW / 312.0 MWh |
| Aggregate charging power | 122.0 MW |
| Dedicated solar plant | 447.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 17.1 km / 257 kWh |
| Lowest traversal charging margin | line-3: 234 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $5.81 bn |
| Stations | $312 M |
| Depots | $135 M |
| Rolling stock | $497 M |
| Dedicated solar plant | $358 M |
| Residual train control | $9.7 M |
| Charging microgrids | $25 M |
| EPC / project services | $475 M |
| **Total city programme** | **$7.62 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.39 bn (18.2%) |
| Domestic / local capital | $6.23 bn (81.8%) |
| Annual public construction commitment | $664 M / yr for 7 years |
| Annual post-grace debt service | $536 M / yr |
| External capital saved vs default turnkey sensitivity | $12.32 bn |
| Capital + lifetime external interest saved | $27.77 bn |
| Annual OPEX | $158 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 24 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 687 assets / 3,902 tasks | [`douala-operations-manifest.json`](operations/douala-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`douala.toml`](douala.toml) | Expanded simulator scenario |
| [`douala.corridor.geojson`](douala.corridor.geojson) | GIS corridor and stations |
| [`douala.design-quality.yaml`](douala.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh douala
```
