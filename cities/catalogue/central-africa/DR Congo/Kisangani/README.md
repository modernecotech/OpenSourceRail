# Kisangani — Urban Rail Network

**Country:** CD · **Population:** 1,300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kisangani-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.19 bn (90.9%) of external capital** and **$5.41 bn of external interest**. Capital plus saved interest totals **$9.60 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **43.121 km to 33.375 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **25 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**2 line-local depots** provide **58 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **58 metro-4car trainsets / 232 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Kisangani rail network on OpenStreetMap](kisangani-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 2 / 25 / 2 |
| Route length | 36.0 km double track |
| Coverage / transfer reachability | 48.2% / 100% |
| Estimated station catchment | 626,600 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 58 × 4-car `metro-4car` trainsets (51 peak revenue) |
| Peak network throughput | 38,400 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 22.2 km | 13 | 47 | W Outer ↔ SE Mid |
| line-2 | 13.8 km | 12 | 11 | NW Inner ↔ SW Inner |
| **Total** | **36.0 km** | **25 unique** | **58** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 698 one-way journeys / 13,535 train-km/day |
| Annual traction demand | 85.4 GWh |
| Station/depot PV / storage | 16.6 MW / 113.0 MWh |
| Aggregate charging power | 36.0 MW |
| Dedicated solar plant | 36.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 7.0 km / 70 kWh |
| Lowest traversal charging margin | line-1: 418 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.10 bn |
| Stations | $157 M |
| Depots | $34 M |
| Rolling stock | $65 M |
| Dedicated solar plant | $30 M |
| Residual train control | $1.8 M |
| Charging microgrids | $7.7 M |
| EPC / project services | $166 M |
| **Total city programme** | **$2.56 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $420 M (16.4%) |
| Domestic / local capital | $2.14 bn (83.6%) |
| Annual public construction commitment | $284 M / yr for 10 years |
| Annual post-grace debt service | $254 M / yr |
| External capital saved vs default turnkey sensitivity | $4.19 bn |
| Capital + lifetime external interest saved | $9.60 bn |
| Annual OPEX | $50 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 4 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 194 assets / 969 tasks | [`kisangani-operations-manifest.json`](operations/kisangani-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kisangani.toml`](kisangani.toml) | Expanded simulator scenario |
| [`kisangani.corridor.geojson`](kisangani.corridor.geojson) | GIS corridor and stations |
| [`kisangani.design-quality.yaml`](kisangani.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kisangani
```
