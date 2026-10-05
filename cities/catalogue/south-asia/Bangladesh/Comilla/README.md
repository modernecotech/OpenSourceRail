# Comilla — Urban Rail Network

**Country:** BD · **Population:** 600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Comilla-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.22 bn (88.4%) of external capital** and **$1.53 bn of external interest**. Capital plus saved interest totals **$2.76 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **51.039 km to 41.108 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **17 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **139 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **139 light-metro-3car trainsets / 417 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Comilla rail network on OpenStreetMap](comilla-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 17 / 1 |
| Route length | 44.0 km double track |
| Coverage / transfer reachability | 66.8% / 33% |
| Estimated station catchment | 400,800 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 139 × 3-car `light-metro-3car` trainsets (125 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 15.6 km | 5 | 48 | NW Outer ↔ E Outer |
| line-2 | 16.8 km | 7 | 53 | SW Outer ↔ NE Mid |
| line-3 | 11.6 km | 5 | 38 | NE Outer ↔ SW Mid |
| **Total** | **44.0 km** | **17 unique** | **139** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 20,479 train-km/day |
| Annual traction demand | 96.9 GWh |
| Station/depot PV / storage | 18.9 MW / 126.5 MWh |
| Aggregate charging power | 8.0 MW |
| Dedicated solar plant | 41.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 7.0 km / 52 kWh |
| Lowest traversal charging margin | line-3: 47 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $433 M |
| Stations | $70 M |
| Depots | $55 M |
| Rolling stock | $125 M |
| Dedicated solar plant | $33 M |
| Residual train control | $2.2 M |
| Charging microgrids | $1.8 M |
| EPC / project services | $48 M |
| **Total city programme** | **$769 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $161 M (20.9%) |
| Domestic / local capital | $609 M (79.1%) |
| Annual public construction commitment | $66 M / yr for 7 years |
| Annual post-grace debt service | $54 M / yr |
| External capital saved vs default turnkey sensitivity | $1.22 bn |
| Capital + lifetime external interest saved | $2.76 bn |
| Annual OPEX | $20 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 5 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 251 assets / 1,565 tasks | [`comilla-operations-manifest.json`](operations/comilla-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`comilla.toml`](comilla.toml) | Expanded simulator scenario |
| [`comilla.corridor.geojson`](comilla.corridor.geojson) | GIS corridor and stations |
| [`comilla.design-quality.yaml`](comilla.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh comilla
```
