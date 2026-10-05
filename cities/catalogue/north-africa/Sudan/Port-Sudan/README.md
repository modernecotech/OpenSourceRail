# Port-Sudan — Urban Rail Network

**Country:** SD · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Port-Sudan-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$727 M (88.7%) of external capital** and **$939 M of external interest**. Capital plus saved interest totals **$1.67 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **33.307 km to 24.681 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **11 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **82 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **82 light-metro-3car trainsets / 246 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Port-Sudan rail network on OpenStreetMap](port-sudan-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 11 / 0 |
| Route length | 25.3 km double track |
| Coverage / transfer reachability | 37.2% / 0% |
| Estimated station catchment | 186,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 82 × 3-car `light-metro-3car` trainsets (73 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 11.2 km | 5 | 37 | N Outer ↔ S Outer |
| line-2 |  7.5 km | 3 | 24 | NW Outer ↔ S Mid |
| line-3 |  6.5 km | 3 | 21 | NE Mid ↔ S Mid |
| **Total** | **25.3 km** | **11 unique** | **82** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 11,744 train-km/day |
| Annual traction demand | 55.6 GWh |
| Station/depot PV / storage | 17.4 MW / 124.0 MWh |
| Aggregate charging power | 5.5 MW |
| Dedicated solar plant | 9.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 4.5 km / 37 kWh |
| Lowest traversal charging margin | line-3: 16 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $254 M |
| Stations | $42 M |
| Depots | $47 M |
| Rolling stock | $74 M |
| Dedicated solar plant | $7.3 M |
| Residual train control | $1.3 M |
| Charging microgrids | $1.2 M |
| EPC / project services | $29 M |
| **Total city programme** | **$456 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $93 M (20.4%) |
| Domestic / local capital | $363 M (79.6%) |
| Annual public construction commitment | $55 M / yr for 10 years |
| Annual post-grace debt service | $50 M / yr |
| External capital saved vs default turnkey sensitivity | $727 M |
| Capital + lifetime external interest saved | $1.67 bn |
| Annual OPEX | $11 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 4 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 157 assets / 940 tasks | [`port-sudan-operations-manifest.json`](operations/port-sudan-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`port-sudan.toml`](port-sudan.toml) | Expanded simulator scenario |
| [`port-sudan.corridor.geojson`](port-sudan.corridor.geojson) | GIS corridor and stations |
| [`port-sudan.design-quality.yaml`](port-sudan.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh port-sudan
```
