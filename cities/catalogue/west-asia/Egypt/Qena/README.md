# Qena — Urban Rail Network

**Country:** EG · **Population:** 350,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Qena-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.30 bn (88.9%) of external capital** and **$1.60 bn of external interest**. Capital plus saved interest totals **$2.91 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **41.769 km to 34.680 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **14 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **131 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **131 light-metro-3car trainsets / 393 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Qena rail network on OpenStreetMap](qena-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 14 / 2 |
| Route length | 41.8 km double track |
| Direct transfers / reachable line pairs | 66.7% / 100.0% |
| Residents within 800 m radial station catchments | 70,460 (2020 raster; 22.7% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 131 × 3-car `light-metro-3car` trainsets (117 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 10.3 km | 5 | 34 | NE Mid ↔ SW Mid |
| line-2 | 18.4 km | 5 | 57 | W Mid ↔ SE Outer |
| line-3 | 13.2 km | 4 | 40 | SW Inner ↔ N Outer |
| **Total** | **41.8 km** | **14 unique** | **131** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 19,449 train-km/day |
| Annual traction demand | 92.0 GWh |
| Station/depot PV / storage | 18.0 MW / 130.0 MWh |
| Aggregate charging power | 13.0 MW |
| Dedicated solar plant | 27.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 11.4 km / 92 kWh |
| Lowest traversal charging margin | line-1: 154 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $497 M |
| Stations | $68 M |
| Depots | $54 M |
| Rolling stock | $118 M |
| Dedicated solar plant | $22 M |
| Residual train control | $2.1 M |
| Charging microgrids | $2.9 M |
| EPC / project services | $52 M |
| **Total city programme** | **$815 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $163 M (20.0%) |
| Domestic / local capital | $652 M (80.0%) |
| Annual public construction commitment | $88 M / yr for 5 years |
| Annual post-grace debt service | $66 M / yr |
| External capital saved vs default turnkey sensitivity | $1.30 bn |
| Capital + lifetime external interest saved | $2.91 bn |
| Annual OPEX | $21 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 3 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 227 assets / 1,438 tasks | [`qena-operations-manifest.json`](operations/qena-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`qena.toml`](qena.toml) | Expanded simulator scenario |
| [`qena.corridor.geojson`](qena.corridor.geojson) | GIS corridor and stations |
| [`qena.design-quality.yaml`](qena.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh qena
```
