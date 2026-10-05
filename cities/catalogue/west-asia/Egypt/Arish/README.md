# Arish — Urban Rail Network

**Country:** EG · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Arish-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$262 M (89.3%) of external capital** and **$322 M of external interest**. Capital plus saved interest totals **$583 M**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **15.034 km to 8.194 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **5 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**2 line-local depots** provide **26 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **26 tram-2car trainsets / 52 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Arish rail network on OpenStreetMap](arish-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 2 / 5 / 0 |
| Route length | 10.4 km double track |
| Direct transfers / reachable line pairs | 0.0% / 0.0% |
| Residents within 800 m radial station catchments | 23,716 (2020 raster; 20.1% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 26 × 2-car `tram-2car` trainsets (22 peak revenue) |
| Peak network throughput | 19,200 passengers/hour |
| Practical service capacity | 178,560 passenger-trips/day |
| Annual paid-trip planning range | 32.6–52.1 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  8.5 km | 3 | 18 | S Outer ↔ N Mid |
| line-2 |  2.0 km | 2 | 8 | N Inner ↔ NW Mid |
| **Total** | **10.4 km** | **5 unique** | **26** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 930 one-way journeys / 4,845 train-km/day |
| Annual traction demand | 15.3 GWh |
| Station/depot PV / storage | 10.9 MW / 81.5 MWh |
| Aggregate charging power | 2.5 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 5.9 km / 32 kWh |
| Lowest traversal charging margin | line-1: 32 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $89 M |
| Stations | $21 M |
| Depots | $26 M |
| Rolling stock | $15 M |
| Residual train control | $521 k |
| Charging microgrids | $650 k |
| EPC / project services | $11 M |
| **Total city programme** | **$163 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $31 M (19.3%) |
| Domestic / local capital | $131 M (80.7%) |
| Annual public construction commitment | $18 M / yr for 5 years |
| Annual post-grace debt service | $13 M / yr |
| External capital saved vs default turnkey sensitivity | $262 M |
| Capital + lifetime external interest saved | $583 M |
| Annual OPEX | $4.7 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 1 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 60 assets / 322 tasks | [`arish-operations-manifest.json`](operations/arish-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`arish.toml`](arish.toml) | Expanded simulator scenario |
| [`arish.corridor.geojson`](arish.corridor.geojson) | GIS corridor and stations |
| [`arish.design-quality.yaml`](arish.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh arish
```
