# Hurghada — Urban Rail Network

**Country:** EG · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Hurghada-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$5.50 bn (91.4%) of external capital** and **$6.77 bn of external interest**. Capital plus saved interest totals **$12.27 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **33.000 km to 26.721 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **17 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **72 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **72 tram-2car trainsets / 144 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Hurghada rail network on OpenStreetMap](hurghada-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 17 / 3 |
| Route length | 32.6 km double track |
| Coverage / transfer reachability | 42.4% / 100% |
| Estimated station catchment | 127,200 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 72 × 2-car `tram-2car` trainsets (64 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 14.2 km | 6 | 30 | NW Outer ↔ SE Mid |
| line-2 | 13.1 km | 6 | 26 | SE Outer ↔ NW Outer |
| line-3 |  5.3 km | 5 | 16 | E Mid ↔ S Inner |
| **Total** | **32.6 km** | **17 unique** | **72** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 15,174 train-km/day |
| Annual traction demand | 47.9 GWh |
| Station/depot PV / storage | 19.2 MW / 127.0 MWh |
| Aggregate charging power | 8.5 MW |
| Dedicated solar plant | 3.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 4.0 km / 22 kWh |
| Lowest traversal charging margin | line-2: 37 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.95 bn |
| Stations | $84 M |
| Depots | $44 M |
| Rolling stock | $40 M |
| Dedicated solar plant | $2.4 M |
| Residual train control | $1.6 M |
| Charging microgrids | $1.9 M |
| EPC / project services | $219 M |
| **Total city programme** | **$3.35 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $521 M (15.6%) |
| Domestic / local capital | $2.83 bn (84.4%) |
| Annual public construction commitment | $374 M / yr for 5 years |
| Annual post-grace debt service | $275 M / yr |
| External capital saved vs default turnkey sensitivity | $5.50 bn |
| Capital + lifetime external interest saved | $12.27 bn |
| Annual OPEX | $66 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 5 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 175 assets / 956 tasks | [`hurghada-operations-manifest.json`](operations/hurghada-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`hurghada.toml`](hurghada.toml) | Expanded simulator scenario |
| [`hurghada.corridor.geojson`](hurghada.corridor.geojson) | GIS corridor and stations |
| [`hurghada.design-quality.yaml`](hurghada.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh hurghada
```
