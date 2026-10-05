# Safi — Urban Rail Network

**Country:** MA · **Population:** 350,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Safi-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$910 M (88.3%) of external capital** and **$1.12 bn of external interest**. Capital plus saved interest totals **$2.03 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **34.491 km to 26.834 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **16 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **111 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **111 light-metro-3car trainsets / 333 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Safi rail network on OpenStreetMap](safi-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 16 / 1 |
| Route length | 33.9 km double track |
| Coverage / transfer reachability | 62.0% / 33% |
| Estimated station catchment | 217,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 111 × 3-car `light-metro-3car` trainsets (99 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 18.0 km | 7 | 57 | SE Outer ↔ NW Mid |
| line-2 |  8.3 km | 5 | 28 | N Mid ↔ SW Mid |
| line-3 |  7.6 km | 4 | 26 | N Inner ↔ SW Mid |
| **Total** | **33.9 km** | **16 unique** | **111** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 15,755 train-km/day |
| Annual traction demand | 74.5 GWh |
| Station/depot PV / storage | 18.3 MW / 125.5 MWh |
| Aggregate charging power | 7.0 MW |
| Dedicated solar plant | 21.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 10.0 km / 72 kWh |
| Lowest traversal charging margin | line-3: 38 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $301 M |
| Stations | $64 M |
| Depots | $50 M |
| Rolling stock | $100 M |
| Dedicated solar plant | $17 M |
| Residual train control | $1.7 M |
| Charging microgrids | $1.6 M |
| EPC / project services | $36 M |
| **Total city programme** | **$572 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $120 M (21.0%) |
| Domestic / local capital | $452 M (79.0%) |
| Annual public construction commitment | $40 M / yr for 5 years |
| Annual post-grace debt service | $28 M / yr |
| External capital saved vs default turnkey sensitivity | $910 M |
| Capital + lifetime external interest saved | $2.03 bn |
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
| Operations, QA and maintenance | 213 assets / 1,287 tasks | [`safi-operations-manifest.json`](operations/safi-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`safi.toml`](safi.toml) | Expanded simulator scenario |
| [`safi.corridor.geojson`](safi.corridor.geojson) | GIS corridor and stations |
| [`safi.design-quality.yaml`](safi.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh safi
```
