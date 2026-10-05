# Jos — Urban Rail Network

**Country:** NG · **Population:** 900,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Jos-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.03 bn (88.7%) of external capital** and **$1.30 bn of external interest**. Capital plus saved interest totals **$2.33 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **42.443 km to 33.595 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **15 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **117 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **117 light-metro-3car trainsets / 351 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Jos rail network on OpenStreetMap](jos-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 15 / 0 |
| Route length | 36.4 km double track |
| Direct transfers / reachable line pairs | 0.0% / 0.0% |
| Residents within 800 m radial station catchments | 103,555 (2020 raster; 14.0% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 117 × 3-car `light-metro-3car` trainsets (105 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 17.1 km | 7 | 53 | N Outer ↔ S Outer |
| line-2 | 11.4 km | 5 | 38 | NW Outer ↔ S Outer |
| line-3 |  7.9 km | 3 | 26 | NE Mid ↔ SE Mid |
| **Total** | **36.4 km** | **15 unique** | **117** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 16,936 train-km/day |
| Annual traction demand | 80.1 GWh |
| Station/depot PV / storage | 18.6 MW / 126.0 MWh |
| Aggregate charging power | 7.5 MW |
| Dedicated solar plant | 17.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 4.9 km / 41 kWh |
| Lowest traversal charging margin | line-3: 25 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $380 M |
| Stations | $52 M |
| Depots | $52 M |
| Rolling stock | $105 M |
| Dedicated solar plant | $14 M |
| Residual train control | $1.8 M |
| Charging microgrids | $1.6 M |
| EPC / project services | $41 M |
| **Total city programme** | **$648 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $131 M (20.3%) |
| Domestic / local capital | $517 M (79.7%) |
| Annual public construction commitment | $76 M / yr for 7 years |
| Annual post-grace debt service | $64 M / yr |
| External capital saved vs default turnkey sensitivity | $1.03 bn |
| Capital + lifetime external interest saved | $2.33 bn |
| Annual OPEX | $16 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 8 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 217 assets / 1,332 tasks | [`jos-operations-manifest.json`](operations/jos-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`jos.toml`](jos.toml) | Expanded simulator scenario |
| [`jos.corridor.geojson`](jos.corridor.geojson) | GIS corridor and stations |
| [`jos.design-quality.yaml`](jos.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh jos
```
