# Hofuf — Urban Rail Network

**Country:** SA · **Population:** 800,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Hofuf-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.61 bn (87.9%) of external capital** and **$1.98 bn of external interest**. Capital plus saved interest totals **$3.58 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **53.388 km to 46.747 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **26 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **226 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **226 light-metro-3car trainsets / 678 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Hofuf rail network on OpenStreetMap](hofuf-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 26 / 2 |
| Route length | 72.3 km double track |
| Direct transfers / reachable line pairs | 66.7% / 100.0% |
| Residents within 800 m radial station catchments | 178,055 (2020 raster; 18.9% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 226 × 3-car `light-metro-3car` trainsets (205 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 23.5 km | 9 | 75 | NW Outer ↔ S Outer |
| line-2 | 24.8 km | 8 | 76 | SW Outer ↔ NE Outer |
| line-3 | 24.0 km | 9 | 75 | N Outer ↔ SE Outer |
| **Total** | **72.3 km** | **26 unique** | **226** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 33,610 train-km/day |
| Annual traction demand | 159.0 GWh |
| Station/depot PV / storage | 21.9 MW / 131.5 MWh |
| Aggregate charging power | 13.0 MW |
| Dedicated solar plant | 58.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 6.7 km / 54 kWh |
| Lowest traversal charging margin | line-2: 74 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $522 M |
| Stations | $106 M |
| Depots | $68 M |
| Rolling stock | $203 M |
| Dedicated solar plant | $47 M |
| Residual train control | $3.6 M |
| Charging microgrids | $2.8 M |
| EPC / project services | $63 M |
| **Total city programme** | **$1.02 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $221 M (21.8%) |
| Domestic / local capital | $795 M (78.2%) |
| Annual public construction commitment | $70 M / yr for 5 years |
| Annual post-grace debt service | $49 M / yr |
| External capital saved vs default turnkey sensitivity | $1.61 bn |
| Capital + lifetime external interest saved | $3.58 bn |
| Annual OPEX | $58 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 13 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 397 assets / 2,527 tasks | [`hofuf-operations-manifest.json`](operations/hofuf-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`hofuf.toml`](hofuf.toml) | Expanded simulator scenario |
| [`hofuf.corridor.geojson`](hofuf.corridor.geojson) | GIS corridor and stations |
| [`hofuf.design-quality.yaml`](hofuf.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh hofuf
```
