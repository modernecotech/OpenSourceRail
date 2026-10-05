# Lichinga — Urban Rail Network

**Country:** MZ · **Population:** 250,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Lichinga-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$230 M (89.2%) of external capital** and **$297 M of external interest**. Capital plus saved interest totals **$526 M**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **14.939 km to 7.142 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **5 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**2 line-local depots** provide **21 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **21 tram-2car trainsets / 42 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Lichinga rail network on OpenStreetMap](lichinga-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 2 / 5 / 0 |
| Route length | 7.1 km double track |
| Direct transfers / reachable line pairs | 0.0% / 0.0% |
| Residents within 800 m radial station catchments | 30,103 (2020 raster; 12.4% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 21 × 2-car `tram-2car` trainsets (17 peak revenue) |
| Peak network throughput | 19,200 passengers/hour |
| Practical service capacity | 178,560 passenger-trips/day |
| Annual paid-trip planning range | 32.6–52.1 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  4.3 km | 3 | 12 | N Outer ↔ S Outer |
| line-2 |  2.8 km | 2 | 9 | NW Outer ↔ S Mid |
| **Total** | **7.1 km** | **5 unique** | **21** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 930 one-way journeys / 3,321 train-km/day |
| Annual traction demand | 10.5 GWh |
| Station/depot PV / storage | 10.9 MW / 81.5 MWh |
| Aggregate charging power | 2.5 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 2.8 km / 14 kWh |
| Lowest traversal charging margin | line-2: 33 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $74 M |
| Stations | $21 M |
| Depots | $26 M |
| Rolling stock | $12 M |
| Residual train control | $357 k |
| Charging microgrids | $650 k |
| EPC / project services | $9.3 M |
| **Total city programme** | **$143 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $28 M (19.4%) |
| Domestic / local capital | $115 M (80.6%) |
| Annual public construction commitment | $16 M / yr for 10 years |
| Annual post-grace debt service | $14 M / yr |
| External capital saved vs default turnkey sensitivity | $230 M |
| Capital + lifetime external interest saved | $526 M |
| Annual OPEX | $3.6 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 1 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 55 assets / 277 tasks | [`lichinga-operations-manifest.json`](operations/lichinga-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`lichinga.toml`](lichinga.toml) | Expanded simulator scenario |
| [`lichinga.corridor.geojson`](lichinga.corridor.geojson) | GIS corridor and stations |
| [`lichinga.design-quality.yaml`](lichinga.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh lichinga
```
