# Port-Said — Urban Rail Network

**Country:** EG · **Population:** 800,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Port-Said-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$856 M (89.5%) of external capital** and **$1.05 bn of external interest**. Capital plus saved interest totals **$1.91 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **29.276 km to 19.622 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **11 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **65 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **65 light-metro-3car trainsets / 195 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Port-Said rail network on OpenStreetMap](port-said-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 11 / 2 |
| Route length | 19.6 km double track |
| Coverage / transfer reachability | 42.7% / 67% |
| Estimated station catchment | 341,600 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 65 × 3-car `light-metro-3car` trainsets (58 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  8.6 km | 4 | 27 | SE Outer ↔ NW Outer |
| line-2 |  6.0 km | 4 | 21 | NE Outer ↔ W Mid |
| line-3 |  5.0 km | 3 | 17 | E Outer ↔ SW Mid |
| **Total** | **19.6 km** | **11 unique** | **65** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 9,124 train-km/day |
| Annual traction demand | 43.2 GWh |
| Station/depot PV / storage | 17.4 MW / 124.0 MWh |
| Aggregate charging power | 5.5 MW |
| Dedicated solar plant | 2.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 3.4 km / 27 kWh |
| Lowest traversal charging margin | line-3: 25 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $326 M |
| Stations | $64 M |
| Depots | $44 M |
| Rolling stock | $58 M |
| Dedicated solar plant | $2.1 M |
| Residual train control | $981 k |
| Charging microgrids | $1.2 M |
| EPC / project services | $35 M |
| **Total city programme** | **$531 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $100 M (18.9%) |
| Domestic / local capital | $431 M (81.1%) |
| Annual public construction commitment | $58 M / yr for 5 years |
| Annual post-grace debt service | $43 M / yr |
| External capital saved vs default turnkey sensitivity | $856 M |
| Capital + lifetime external interest saved | $1.91 bn |
| Annual OPEX | $14 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 0 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 137 assets / 784 tasks | [`port-said-operations-manifest.json`](operations/port-said-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`port-said.toml`](port-said.toml) | Expanded simulator scenario |
| [`port-said.corridor.geojson`](port-said.corridor.geojson) | GIS corridor and stations |
| [`port-said.design-quality.yaml`](port-said.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh port-said
```
