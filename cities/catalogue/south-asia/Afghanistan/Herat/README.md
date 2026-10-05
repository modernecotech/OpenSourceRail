# Herat — Urban Rail Network

**Country:** AF · **Population:** 800,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Herat-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.05 bn (88.5%) of external capital** and **$1.36 bn of external interest**. Capital plus saved interest totals **$2.41 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **43.191 km to 33.947 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **17 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **124 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **124 light-metro-3car trainsets / 372 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Herat rail network on OpenStreetMap](herat-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 17 / 2 |
| Route length | 40.2 km double track |
| Direct transfers / reachable line pairs | 66.7% / 100.0% |
| Residents within 800 m radial station catchments | 93,264 (2020 raster; 13.3% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 124 × 3-car `light-metro-3car` trainsets (111 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  9.2 km | 5 | 29 | NE Mid ↔ SW Mid |
| line-2 | 10.3 km | 5 | 34 | S Mid ↔ W Mid |
| line-3 | 20.7 km | 7 | 61 | NW Outer ↔ E Outer |
| **Total** | **40.2 km** | **17 unique** | **124** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 18,681 train-km/day |
| Annual traction demand | 88.4 GWh |
| Station/depot PV / storage | 19.2 MW / 127.0 MWh |
| Aggregate charging power | 8.5 MW |
| Dedicated solar plant | 22.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 4.3 km / 31 kWh |
| Lowest traversal charging margin | line-1: 37 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $354 M |
| Stations | $79 M |
| Depots | $53 M |
| Rolling stock | $112 M |
| Dedicated solar plant | $18 M |
| Residual train control | $2.0 M |
| Charging microgrids | $1.9 M |
| EPC / project services | $42 M |
| **Total city programme** | **$661 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $137 M (20.8%) |
| Domestic / local capital | $524 M (79.2%) |
| Annual public construction commitment | $92 M / yr for 10 years |
| Annual post-grace debt service | $84 M / yr |
| External capital saved vs default turnkey sensitivity | $1.05 bn |
| Capital + lifetime external interest saved | $2.41 bn |
| Annual OPEX | $16 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 6 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 235 assets / 1,432 tasks | [`herat-operations-manifest.json`](operations/herat-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`herat.toml`](herat.toml) | Expanded simulator scenario |
| [`herat.corridor.geojson`](herat.corridor.geojson) | GIS corridor and stations |
| [`herat.design-quality.yaml`](herat.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh herat
```
