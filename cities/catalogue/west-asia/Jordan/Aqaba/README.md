# Aqaba — Urban Rail Network

**Country:** JO · **Population:** 250,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Aqaba-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.11 bn (91.3%) of external capital** and **$5.06 bn of external interest**. Capital plus saved interest totals **$9.17 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **28.364 km to 25.774 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **17 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **71 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **71 tram-2car trainsets / 142 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Aqaba rail network on OpenStreetMap](aqaba-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 17 / 3 |
| Route length | 32.4 km double track |
| Coverage / transfer reachability | 54.8% / 100% |
| Estimated station catchment | 137,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 71 × 2-car `tram-2car` trainsets (63 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 11.6 km | 5 | 25 | W Outer ↔ E Outer |
| line-2 |  7.5 km | 5 | 18 | S Mid ↔ NE Outer |
| line-3 | 13.3 km | 7 | 28 | SE Mid ↔ W Outer |
| **Total** | **32.4 km** | **17 unique** | **71** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 15,087 train-km/day |
| Annual traction demand | 47.6 GWh |
| Station/depot PV / storage | 19.2 MW / 127.0 MWh |
| Aggregate charging power | 8.5 MW |
| Dedicated solar plant | 2.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 3.5 km / 19 kWh |
| Lowest traversal charging margin | line-1: 42 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.16 bn |
| Stations | $92 M |
| Depots | $43 M |
| Rolling stock | $40 M |
| Dedicated solar plant | $2.3 M |
| Residual train control | $1.6 M |
| Charging microgrids | $1.9 M |
| EPC / project services | $164 M |
| **Total city programme** | **$2.50 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $394 M (15.7%) |
| Domestic / local capital | $2.11 bn (84.3%) |
| Annual public construction commitment | $229 M / yr for 5 years |
| Annual post-grace debt service | $160 M / yr |
| External capital saved vs default turnkey sensitivity | $4.11 bn |
| Capital + lifetime external interest saved | $9.17 bn |
| Annual OPEX | $54 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 3 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 174 assets / 947 tasks | [`aqaba-operations-manifest.json`](operations/aqaba-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`aqaba.toml`](aqaba.toml) | Expanded simulator scenario |
| [`aqaba.corridor.geojson`](aqaba.corridor.geojson) | GIS corridor and stations |
| [`aqaba.design-quality.yaml`](aqaba.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh aqaba
```
