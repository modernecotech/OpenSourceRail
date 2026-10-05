# Fort-Portal — Urban Rail Network

**Country:** UG · **Population:** 200,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Fort-Portal-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$718 M (89.4%) of external capital** and **$900 M of external interest**. Capital plus saved interest totals **$1.62 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **32.031 km to 24.517 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **14 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **64 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **64 tram-2car trainsets / 128 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Fort-Portal rail network on OpenStreetMap](fort-portal-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 14 / 1 |
| Route length | 28.7 km double track |
| Coverage / transfer reachability | 66.0% / 100% |
| Estimated station catchment | 132,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 64 × 2-car `tram-2car` trainsets (57 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  9.3 km | 4 | 20 | SE Mid ↔ NW Outer |
| line-2 |  6.7 km | 5 | 18 | NE Inner ↔ SW Mid |
| line-3 | 12.8 km | 5 | 26 | E Outer ↔ W Mid |
| **Total** | **28.7 km** | **14 unique** | **64** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 13,367 train-km/day |
| Annual traction demand | 42.2 GWh |
| Station/depot PV / storage | 18.3 MW / 125.5 MWh |
| Aggregate charging power | 7.0 MW |
| Dedicated solar plant | 6.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 6.3 km / 31 kWh |
| Lowest traversal charging margin | line-1: 39 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $250 M |
| Stations | $80 M |
| Depots | $42 M |
| Rolling stock | $36 M |
| Dedicated solar plant | $5.3 M |
| Residual train control | $1.4 M |
| Charging microgrids | $1.6 M |
| EPC / project services | $29 M |
| **Total city programme** | **$446 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $85 M (19.0%) |
| Domestic / local capital | $361 M (81.0%) |
| Annual public construction commitment | $55 M / yr for 7 years |
| Annual post-grace debt service | $46 M / yr |
| External capital saved vs default turnkey sensitivity | $718 M |
| Capital + lifetime external interest saved | $1.62 bn |
| Annual OPEX | $11 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 2 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 151 assets / 829 tasks | [`fort-portal-operations-manifest.json`](operations/fort-portal-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`fort-portal.toml`](fort-portal.toml) | Expanded simulator scenario |
| [`fort-portal.corridor.geojson`](fort-portal.corridor.geojson) | GIS corridor and stations |
| [`fort-portal.design-quality.yaml`](fort-portal.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh fort-portal
```
