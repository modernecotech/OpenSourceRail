# Idlib — Urban Rail Network

**Country:** SY · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Idlib-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$631 M (89.4%) of external capital** and **$815 M of external interest**. Capital plus saved interest totals **$1.45 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **24.422 km to 20.741 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **11 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **59 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **59 tram-2car trainsets / 118 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Idlib rail network on OpenStreetMap](idlib-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 11 / 2 |
| Route length | 28.3 km double track |
| Coverage / transfer reachability | 59.6% / 67% |
| Estimated station catchment | 178,800 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 59 × 2-car `tram-2car` trainsets (52 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 11.7 km | 5 | 25 | NE Outer ↔ SW Mid |
| line-2 |  8.0 km | 3 | 16 | W Mid ↔ S Outer |
| line-3 |  8.6 km | 3 | 18 | NE Outer ↔ NW Inner |
| **Total** | **28.3 km** | **11 unique** | **59** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 13,152 train-km/day |
| Annual traction demand | 41.5 GWh |
| Station/depot PV / storage | 17.4 MW / 124.0 MWh |
| Aggregate charging power | 5.5 MW |
| Dedicated solar plant | 3.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 6.2 km / 30 kWh |
| Lowest traversal charging margin | line-2: 27 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $222 M |
| Stations | $64 M |
| Depots | $42 M |
| Rolling stock | $33 M |
| Dedicated solar plant | $3.0 M |
| Residual train control | $1.4 M |
| Charging microgrids | $1.2 M |
| EPC / project services | $25 M |
| **Total city programme** | **$392 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $75 M (19.0%) |
| Domestic / local capital | $317 M (81.0%) |
| Annual public construction commitment | $60 M / yr for 10 years |
| Annual post-grace debt service | $56 M / yr |
| External capital saved vs default turnkey sensitivity | $631 M |
| Capital + lifetime external interest saved | $1.45 bn |
| Annual OPEX | $8.7 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 0 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 130 assets / 729 tasks | [`idlib-operations-manifest.json`](operations/idlib-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`idlib.toml`](idlib.toml) | Expanded simulator scenario |
| [`idlib.corridor.geojson`](idlib.corridor.geojson) | GIS corridor and stations |
| [`idlib.design-quality.yaml`](idlib.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh idlib
```
