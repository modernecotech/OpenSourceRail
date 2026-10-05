# Kigoma — Urban Rail Network

**Country:** TZ · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kigoma-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$685 M (89.5%) of external capital** and **$859 M of external interest**. Capital plus saved interest totals **$1.54 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **32.263 km to 23.165 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **14 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **60 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **60 tram-2car trainsets / 120 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Kigoma rail network on OpenStreetMap](kigoma-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 14 / 3 |
| Route length | 26.8 km double track |
| Coverage / transfer reachability | 36.1% / 100% |
| Estimated station catchment | 108,300 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 60 × 2-car `tram-2car` trainsets (53 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  9.2 km | 5 | 20 | SW Outer ↔ E Mid |
| line-2 | 11.5 km | 5 | 25 | SE Outer ↔ NW Outer |
| line-3 |  6.1 km | 4 | 15 | N Mid ↔ S Mid |
| **Total** | **26.8 km** | **14 unique** | **60** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 12,468 train-km/day |
| Annual traction demand | 39.3 GWh |
| Station/depot PV / storage | 18.3 MW / 125.5 MWh |
| Aggregate charging power | 7.0 MW |
| Dedicated solar plant | 4.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 5.4 km / 27 kWh |
| Lowest traversal charging margin | line-1: 48 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $235 M |
| Stations | $80 M |
| Depots | $42 M |
| Rolling stock | $34 M |
| Dedicated solar plant | $3.8 M |
| Residual train control | $1.3 M |
| Charging microgrids | $1.6 M |
| EPC / project services | $28 M |
| **Total city programme** | **$426 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $81 M (19.0%) |
| Domestic / local capital | $345 M (81.0%) |
| Annual public construction commitment | $40 M / yr for 7 years |
| Annual post-grace debt service | $32 M / yr |
| External capital saved vs default turnkey sensitivity | $685 M |
| Capital + lifetime external interest saved | $1.54 bn |
| Annual OPEX | $10 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 2 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 146 assets / 792 tasks | [`kigoma-operations-manifest.json`](operations/kigoma-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kigoma.toml`](kigoma.toml) | Expanded simulator scenario |
| [`kigoma.corridor.geojson`](kigoma.corridor.geojson) | GIS corridor and stations |
| [`kigoma.design-quality.yaml`](kigoma.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kigoma
```
