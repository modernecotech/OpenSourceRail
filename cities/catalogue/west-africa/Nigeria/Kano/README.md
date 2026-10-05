# Kano — Urban Rail Network

**Country:** NG · **Population:** 4,200,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kano-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$11.62 bn (88.0%) of external capital** and **$14.57 bn of external interest**. Capital plus saved interest totals **$26.19 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **358.026 km to 340.685 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 1 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **168 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**9 line-local depots** provide **678 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **678 metro-6car trainsets / 4068 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Kano rail network on OpenStreetMap](kano-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 168 / 22 |
| Route length | 404.1 km double track |
| Direct transfers / reachable line pairs | 91.7% / 100.0% |
| Residents within 800 m radial station catchments | 1,639,946 (2020 raster; 26.8% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 678 × 6-car `metro-6car` trainsets (612 peak revenue) |
| Peak network throughput | 259,200 passengers/hour |
| Practical service capacity | 2,276,640 passenger-trips/day |
| Annual paid-trip planning range | 415.5–664.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 39.6 km | 16 | 75 | W Mid ↔ E Mid |
| line-2 | 43.3 km | 20 | 86 | SE Outer ↔ NW Mid |
| line-3 | 40.9 km | 17 | 78 | SW Outer ↔ NE Mid |
| line-4 | 35.4 km | 17 | 73 | SE Outer ↔ W Mid |
| line-5 | 36.7 km | 16 | 71 | NE Outer ↔ SW Inner |
| line-6 | 30.3 km | 15 | 65 | N Inner ↔ S Mid |
| line-7 | 50.1 km | 20 | 100 | NE Outer ↔ S Outer |
| line-8 | 44.7 km | 18 | 89 | SE Inner ↔ NW Outer |
| line-9 | 83.2 km | 29 | 41 | NW Mid ↔ W Mid |
| **Total** | **404.1 km** | **168 unique** | **678** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,952 one-way journeys / 168,588 train-km/day |
| Annual traction demand | 1,595.0 GWh |
| Station/depot PV / storage | 87.9 MW / 646.0 MWh |
| Aggregate charging power | 304.0 MW |
| Dedicated solar plant | 672.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-8: 19.7 km / 330 kWh |
| Lowest traversal charging margin | line-3: 294 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $3.98 bn |
| Stations | $877 M |
| Depots | $280 M |
| Rolling stock | $1.14 bn |
| Dedicated solar plant | $538 M |
| Residual train control | $20 M |
| Charging microgrids | $61 M |
| EPC / project services | $445 M |
| **Total city programme** | **$7.34 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.58 bn (21.6%) |
| Domestic / local capital | $5.75 bn (78.4%) |
| Annual public construction commitment | $857 M / yr for 7 years |
| Annual post-grace debt service | $724 M / yr |
| External capital saved vs default turnkey sensitivity | $11.62 bn |
| Capital + lifetime external interest saved | $26.19 bn |
| Annual OPEX | $174 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 52 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,621 assets / 9,135 tasks | [`kano-operations-manifest.json`](operations/kano-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kano.toml`](kano.toml) | Expanded simulator scenario |
| [`kano.corridor.geojson`](kano.corridor.geojson) | GIS corridor and stations |
| [`kano.design-quality.yaml`](kano.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kano
```
