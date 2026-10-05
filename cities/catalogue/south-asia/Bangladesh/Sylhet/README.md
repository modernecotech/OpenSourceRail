# Sylhet — Urban Rail Network

**Country:** BD · **Population:** 900,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Sylhet-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.13 bn (88.3%) of external capital** and **$1.41 bn of external interest**. Capital plus saved interest totals **$2.54 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **42.948 km to 34.438 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **17 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **131 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **131 light-metro-3car trainsets / 393 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Sylhet rail network on OpenStreetMap](sylhet-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 17 / 2 |
| Route length | 41.0 km double track |
| Coverage / transfer reachability | 37.6% / 67% |
| Estimated station catchment | 338,400 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 131 × 3-car `light-metro-3car` trainsets (118 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 10.2 km | 4 | 31 | E Mid ↔ NW Mid |
| line-2 | 21.2 km | 8 | 68 | SW Outer ↔ N Mid |
| line-3 |  9.7 km | 5 | 32 | E Mid ↔ NW Inner |
| **Total** | **41.0 km** | **17 unique** | **131** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 19,087 train-km/day |
| Annual traction demand | 90.3 GWh |
| Station/depot PV / storage | 18.6 MW / 126.0 MWh |
| Aggregate charging power | 7.5 MW |
| Dedicated solar plant | 37.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 10.5 km / 79 kWh |
| Lowest traversal charging margin | line-1: 30 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $384 M |
| Stations | $75 M |
| Depots | $54 M |
| Rolling stock | $118 M |
| Dedicated solar plant | $30 M |
| Residual train control | $2.1 M |
| Charging microgrids | $1.6 M |
| EPC / project services | $44 M |
| **Total city programme** | **$710 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $149 M (21.1%) |
| Domestic / local capital | $560 M (78.9%) |
| Annual public construction commitment | $61 M / yr for 7 years |
| Annual post-grace debt service | $50 M / yr |
| External capital saved vs default turnkey sensitivity | $1.13 bn |
| Capital + lifetime external interest saved | $2.54 bn |
| Annual OPEX | $18 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 4 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 241 assets / 1,488 tasks | [`sylhet-operations-manifest.json`](operations/sylhet-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`sylhet.toml`](sylhet.toml) | Expanded simulator scenario |
| [`sylhet.corridor.geojson`](sylhet.corridor.geojson) | GIS corridor and stations |
| [`sylhet.design-quality.yaml`](sylhet.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh sylhet
```
