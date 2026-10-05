# Mymensingh — Urban Rail Network

**Country:** BD · **Population:** 700,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Mymensingh-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.13 bn (88.7%) of external capital** and **$1.41 bn of external interest**. Capital plus saved interest totals **$2.54 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **35.893 km to 27.485 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **15 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **115 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **115 light-metro-3car trainsets / 345 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Mymensingh rail network on OpenStreetMap](mymensingh-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 15 / 2 |
| Route length | 36.4 km double track |
| Coverage / transfer reachability | 55.8% / 67% |
| Estimated station catchment | 390,600 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 115 × 3-car `light-metro-3car` trainsets (103 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  9.2 km | 5 | 29 | W Mid ↔ S Mid |
| line-2 |  8.7 km | 4 | 27 | W Mid ↔ NE Inner |
| line-3 | 18.5 km | 6 | 59 | NE Outer ↔ SW Mid |
| **Total** | **36.4 km** | **15 unique** | **115** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 16,904 train-km/day |
| Annual traction demand | 80.0 GWh |
| Station/depot PV / storage | 18.0 MW / 125.0 MWh |
| Aggregate charging power | 6.5 MW |
| Dedicated solar plant | 31.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 12.8 km / 96 kWh |
| Lowest traversal charging margin | line-2: 27 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $407 M |
| Stations | $70 M |
| Depots | $51 M |
| Rolling stock | $104 M |
| Dedicated solar plant | $25 M |
| Residual train control | $1.8 M |
| Charging microgrids | $1.4 M |
| EPC / project services | $44 M |
| **Total city programme** | **$705 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $144 M (20.4%) |
| Domestic / local capital | $561 M (79.6%) |
| Annual public construction commitment | $61 M / yr for 7 years |
| Annual post-grace debt service | $49 M / yr |
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
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 2 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 213 assets / 1,306 tasks | [`mymensingh-operations-manifest.json`](operations/mymensingh-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`mymensingh.toml`](mymensingh.toml) | Expanded simulator scenario |
| [`mymensingh.corridor.geojson`](mymensingh.corridor.geojson) | GIS corridor and stations |
| [`mymensingh.design-quality.yaml`](mymensingh.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh mymensingh
```
