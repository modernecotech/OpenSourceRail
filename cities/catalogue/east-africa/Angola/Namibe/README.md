# Namibe — Urban Rail Network

**Country:** AO · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Namibe-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$5.64 bn (91.4%) of external capital** and **$6.93 bn of external interest**. Capital plus saved interest totals **$12.57 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **34.461 km to 30.373 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **17 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **76 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **76 tram-2car trainsets / 152 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Namibe rail network on OpenStreetMap](namibe-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 17 / 2 |
| Route length | 36.7 km double track |
| Coverage / transfer reachability | 59.0% / 67% |
| Estimated station catchment | 177,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 76 × 2-car `tram-2car` trainsets (68 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 12.8 km | 6 | 26 | SW Outer ↔ E Outer |
| line-2 | 10.0 km | 5 | 21 | NE Outer ↔ S Mid |
| line-3 | 13.9 km | 6 | 29 | NE Outer ↔ SW Outer |
| **Total** | **36.7 km** | **17 unique** | **76** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 17,052 train-km/day |
| Annual traction demand | 53.8 GWh |
| Station/depot PV / storage | 19.2 MW / 127.0 MWh |
| Aggregate charging power | 8.5 MW |
| Dedicated solar plant | 4.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 4.2 km / 23 kWh |
| Lowest traversal charging margin | line-1: 36 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $3.03 bn |
| Stations | $85 M |
| Depots | $44 M |
| Rolling stock | $43 M |
| Dedicated solar plant | $3.2 M |
| Residual train control | $1.8 M |
| Charging microgrids | $1.9 M |
| EPC / project services | $224 M |
| **Total city programme** | **$3.43 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $533 M (15.6%) |
| Domestic / local capital | $2.89 bn (84.4%) |
| Annual public construction commitment | $406 M / yr for 5 years |
| Annual post-grace debt service | $303 M / yr |
| External capital saved vs default turnkey sensitivity | $5.64 bn |
| Capital + lifetime external interest saved | $12.57 bn |
| Annual OPEX | $68 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 3 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 180 assets / 993 tasks | [`namibe-operations-manifest.json`](operations/namibe-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`namibe.toml`](namibe.toml) | Expanded simulator scenario |
| [`namibe.corridor.geojson`](namibe.corridor.geojson) | GIS corridor and stations |
| [`namibe.design-quality.yaml`](namibe.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh namibe
```
