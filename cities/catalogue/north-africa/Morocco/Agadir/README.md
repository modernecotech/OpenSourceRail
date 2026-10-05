# Agadir — Urban Rail Network

**Country:** MA · **Population:** 900,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Agadir-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.61 bn (88.1%) of external capital** and **$1.98 bn of external interest**. Capital plus saved interest totals **$3.58 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **57.669 km to 44.734 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **25 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **215 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **215 light-metro-3car trainsets / 645 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Agadir rail network on OpenStreetMap](agadir-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 25 / 1 |
| Route length | 70.5 km double track |
| Coverage / transfer reachability | 43.7% / 33% |
| Estimated station catchment | 393,300 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 215 × 3-car `light-metro-3car` trainsets (194 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 23.2 km | 8 | 70 | SE Outer ↔ NW Mid |
| line-2 | 23.7 km | 8 | 70 | NW Outer ↔ SE Mid |
| line-3 | 23.7 km | 9 | 75 | SE Outer ↔ N Outer |
| **Total** | **70.5 km** | **25 unique** | **215** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 32,805 train-km/day |
| Annual traction demand | 155.2 GWh |
| Station/depot PV / storage | 21.6 MW / 131.0 MWh |
| Aggregate charging power | 12.5 MW |
| Dedicated solar plant | 56.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 5.7 km / 46 kWh |
| Lowest traversal charging margin | line-2: 51 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $549 M |
| Stations | $90 M |
| Depots | $67 M |
| Rolling stock | $194 M |
| Dedicated solar plant | $45 M |
| Residual train control | $3.5 M |
| Charging microgrids | $2.6 M |
| EPC / project services | $63 M |
| **Total city programme** | **$1.01 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $217 M (21.4%) |
| Domestic / local capital | $796 M (78.6%) |
| Annual public construction commitment | $70 M / yr for 5 years |
| Annual post-grace debt service | $49 M / yr |
| External capital saved vs default turnkey sensitivity | $1.61 bn |
| Capital + lifetime external interest saved | $3.58 bn |
| Annual OPEX | $31 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 15 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 380 assets / 2,409 tasks | [`agadir-operations-manifest.json`](operations/agadir-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`agadir.toml`](agadir.toml) | Expanded simulator scenario |
| [`agadir.corridor.geojson`](agadir.corridor.geojson) | GIS corridor and stations |
| [`agadir.design-quality.yaml`](agadir.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh agadir
```
