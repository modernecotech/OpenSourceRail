# Dammam — Urban Rail Network

**Country:** SA · **Population:** 1,500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Dammam-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$17.78 bn (90.6%) of external capital** and **$21.86 bn of external interest**. Capital plus saved interest totals **$39.64 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **178.222 km to 168.471 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **107 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **346 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **346 metro-4car trainsets / 1384 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Dammam rail network on OpenStreetMap](dammam-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 107 / 19 |
| Route length | 267.8 km double track |
| Direct transfers / reachable line pairs | 93.3% / 100.0% |
| Residents within 800 m radial station catchments | 620,387 (2020 raster; 27.3% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 346 × 4-car `metro-4car` trainsets (311 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 45.2 km | 20 | 80 | SE Outer ↔ NW Outer |
| line-2 | 34.5 km | 14 | 58 | NW Outer ↔ E Mid |
| line-3 | 25.7 km | 11 | 46 | E Mid ↔ SW Mid |
| line-4 | 28.3 km | 13 | 52 | SW Outer ↔ E Mid |
| line-5 | 43.7 km | 18 | 74 | N Outer ↔ S Outer |
| line-6 | 90.4 km | 31 | 36 | NW Mid ↔ NW Mid |
| **Total** | **267.8 km** | **107 unique** | **346** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 103,504 train-km/day |
| Annual traction demand | 652.8 GWh |
| Station/depot PV / storage | 58.8 MW / 384.0 MWh |
| Aggregate charging power | 153.0 MW |
| Dedicated solar plant | 275.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 9.3 km / 100 kWh |
| Lowest traversal charging margin | line-2: 229 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $8.79 bn |
| Stations | $618 M |
| Depots | $136 M |
| Rolling stock | $388 M |
| Dedicated solar plant | $220 M |
| Residual train control | $13 M |
| Charging microgrids | $32 M |
| EPC / project services | $699 M |
| **Total city programme** | **$10.90 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.84 bn (16.8%) |
| Domestic / local capital | $9.06 bn (83.2%) |
| Annual public construction commitment | $771 M / yr for 5 years |
| Annual post-grace debt service | $520 M / yr |
| External capital saved vs default turnkey sensitivity | $17.78 bn |
| Capital + lifetime external interest saved | $39.64 bn |
| Annual OPEX | $306 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 38 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 939 assets / 5,052 tasks | [`dammam-operations-manifest.json`](operations/dammam-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`dammam.toml`](dammam.toml) | Expanded simulator scenario |
| [`dammam.corridor.geojson`](dammam.corridor.geojson) | GIS corridor and stations |
| [`dammam.design-quality.yaml`](dammam.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh dammam
```
