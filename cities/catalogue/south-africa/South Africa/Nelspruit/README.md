# Nelspruit — Urban Rail Network

**Country:** ZA · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Nelspruit-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$796 M (89.7%) of external capital** and **$979 M of external interest**. Capital plus saved interest totals **$1.78 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **35.523 km to 26.864 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **12 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **62 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **62 tram-2car trainsets / 124 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Nelspruit rail network on OpenStreetMap](nelspruit-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 12 / 2 |
| Route length | 30.1 km double track |
| Coverage / transfer reachability | 37.4% / 67% |
| Estimated station catchment | 112,200 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 62 × 2-car `tram-2car` trainsets (55 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  8.4 km | 4 | 17 | W Mid ↔ NE Mid |
| line-2 | 12.0 km | 4 | 25 | N Mid ↔ S Outer |
| line-3 |  9.7 km | 4 | 20 | W Mid ↔ SE Mid |
| **Total** | **30.1 km** | **12 unique** | **62** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 13,975 train-km/day |
| Annual traction demand | 44.1 GWh |
| Station/depot PV / storage | 17.7 MW / 124.5 MWh |
| Aggregate charging power | 6.0 MW |
| Dedicated solar plant | 8.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 6.7 km / 33 kWh |
| Lowest traversal charging margin | line-1: 36 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $310 M |
| Stations | $64 M |
| Depots | $42 M |
| Rolling stock | $35 M |
| Dedicated solar plant | $6.9 M |
| Residual train control | $1.5 M |
| Charging microgrids | $1.4 M |
| EPC / project services | $32 M |
| **Total city programme** | **$493 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $91 M (18.5%) |
| Domestic / local capital | $402 M (81.5%) |
| Annual public construction commitment | $54 M / yr for 5 years |
| Annual post-grace debt service | $40 M / yr |
| External capital saved vs default turnkey sensitivity | $796 M |
| Capital + lifetime external interest saved | $1.78 bn |
| Annual OPEX | $15 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 2 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 139 assets / 775 tasks | [`nelspruit-operations-manifest.json`](operations/nelspruit-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`nelspruit.toml`](nelspruit.toml) | Expanded simulator scenario |
| [`nelspruit.corridor.geojson`](nelspruit.corridor.geojson) | GIS corridor and stations |
| [`nelspruit.design-quality.yaml`](nelspruit.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh nelspruit
```
