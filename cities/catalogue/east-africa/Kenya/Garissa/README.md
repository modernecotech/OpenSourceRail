# Garissa — Urban Rail Network

**Country:** KE · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Garissa-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$477 M (89.4%) of external capital** and **$598 M of external interest**. Capital plus saved interest totals **$1.08 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **24.175 km to 16.307 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **10 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **44 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **44 tram-2car trainsets / 88 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Garissa rail network on OpenStreetMap](garissa-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 10 / 1 |
| Route length | 17.5 km double track |
| Coverage / transfer reachability | 13.4% / 33% |
| Estimated station catchment | 40,200 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 44 × 2-car `tram-2car` trainsets (38 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  5.0 km | 3 | 13 | S Mid ↔ NW Mid |
| line-2 |  9.2 km | 4 | 20 | SE Outer ↔ NE Outer |
| line-3 |  3.3 km | 3 | 11 | N Inner ↔ SW Mid |
| **Total** | **17.5 km** | **10 unique** | **44** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 8,154 train-km/day |
| Annual traction demand | 25.7 GWh |
| Station/depot PV / storage | 17.1 MW / 123.5 MWh |
| Aggregate charging power | 5.0 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 4.6 km / 26 kWh |
| Lowest traversal charging margin | line-1: 35 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $162 M |
| Stations | $48 M |
| Depots | $40 M |
| Rolling stock | $25 M |
| Residual train control | $877 k |
| Charging microgrids | $1.1 M |
| EPC / project services | $19 M |
| **Total city programme** | **$296 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $56 M (19.0%) |
| Domestic / local capital | $240 M (81.0%) |
| Annual public construction commitment | $31 M / yr for 7 years |
| Annual post-grace debt service | $26 M / yr |
| External capital saved vs default turnkey sensitivity | $477 M |
| Capital + lifetime external interest saved | $1.08 bn |
| Annual OPEX | $8.0 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 2 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 108 assets / 574 tasks | [`garissa-operations-manifest.json`](operations/garissa-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`garissa.toml`](garissa.toml) | Expanded simulator scenario |
| [`garissa.corridor.geojson`](garissa.corridor.geojson) | GIS corridor and stations |
| [`garissa.design-quality.yaml`](garissa.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh garissa
```
