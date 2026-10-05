# Tabuk — Urban Rail Network

**Country:** SA · **Population:** 650,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Tabuk-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.48 bn (88.4%) of external capital** and **$1.82 bn of external interest**. Capital plus saved interest totals **$3.30 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **49.687 km to 43.436 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **25 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **181 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **181 light-metro-3car trainsets / 543 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Tabuk rail network on OpenStreetMap](tabuk-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 25 / 2 |
| Route length | 56.8 km double track |
| Coverage / transfer reachability | 27.7% / 67% |
| Estimated station catchment | 180,050 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 181 × 3-car `light-metro-3car` trainsets (163 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 15.8 km | 7 | 51 | NE Mid ↔ W Mid |
| line-2 | 18.2 km | 8 | 59 | N Outer ↔ S Mid |
| line-3 | 22.9 km | 10 | 71 | E Outer ↔ SW Mid |
| **Total** | **56.8 km** | **25 unique** | **181** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 26,429 train-km/day |
| Annual traction demand | 125.0 GWh |
| Station/depot PV / storage | 21.3 MW / 130.5 MWh |
| Aggregate charging power | 12.0 MW |
| Dedicated solar plant | 41.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 7.0 km / 56 kWh |
| Lowest traversal charging margin | line-3: 59 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $509 M |
| Stations | $99 M |
| Depots | $62 M |
| Rolling stock | $163 M |
| Dedicated solar plant | $33 M |
| Residual train control | $2.8 M |
| Charging microgrids | $2.5 M |
| EPC / project services | $59 M |
| **Total city programme** | **$929 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $195 M (20.9%) |
| Domestic / local capital | $735 M (79.1%) |
| Annual public construction commitment | $65 M / yr for 5 years |
| Annual post-grace debt service | $45 M / yr |
| External capital saved vs default turnkey sensitivity | $1.48 bn |
| Capital + lifetime external interest saved | $3.30 bn |
| Annual OPEX | $52 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 12 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 340 assets / 2,094 tasks | [`tabuk-operations-manifest.json`](operations/tabuk-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`tabuk.toml`](tabuk.toml) | Expanded simulator scenario |
| [`tabuk.corridor.geojson`](tabuk.corridor.geojson) | GIS corridor and stations |
| [`tabuk.design-quality.yaml`](tabuk.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh tabuk
```
