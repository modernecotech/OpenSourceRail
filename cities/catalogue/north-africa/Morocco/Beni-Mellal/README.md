# Beni-Mellal — Urban Rail Network

**Country:** MA · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Beni-Mellal-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$612 M (89.5%) of external capital** and **$753 M of external interest**. Capital plus saved interest totals **$1.37 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **24.468 km to 19.178 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **10 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **55 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **55 tram-2car trainsets / 110 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Beni-Mellal rail network on OpenStreetMap](beni-mellal-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 10 / 1 |
| Route length | 27.0 km double track |
| Coverage / transfer reachability | 77.7% / 100% |
| Estimated station catchment | 233,100 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 55 × 2-car `tram-2car` trainsets (49 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  8.5 km | 4 | 18 | NE Mid ↔ SW Outer |
| line-2 |  9.7 km | 3 | 19 | SW Mid ↔ NE Outer |
| line-3 |  8.8 km | 3 | 18 | S Mid ↔ N Outer |
| **Total** | **27.0 km** | **10 unique** | **55** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 12,566 train-km/day |
| Annual traction demand | 39.6 GWh |
| Station/depot PV / storage | 17.1 MW / 123.5 MWh |
| Aggregate charging power | 5.0 MW |
| Dedicated solar plant | 3.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 6.7 km / 32 kWh |
| Lowest traversal charging margin | line-3: 27 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $222 M |
| Stations | $56 M |
| Depots | $41 M |
| Rolling stock | $31 M |
| Dedicated solar plant | $2.4 M |
| Residual train control | $1.4 M |
| Charging microgrids | $1.1 M |
| EPC / project services | $25 M |
| **Total city programme** | **$380 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $72 M (18.8%) |
| Domestic / local capital | $308 M (81.2%) |
| Annual public construction commitment | $27 M / yr for 5 years |
| Annual post-grace debt service | $18 M / yr |
| External capital saved vs default turnkey sensitivity | $612 M |
| Capital + lifetime external interest saved | $1.37 bn |
| Annual OPEX | $12 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 0 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 121 assets / 675 tasks | [`beni-mellal-operations-manifest.json`](operations/beni-mellal-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`beni-mellal.toml`](beni-mellal.toml) | Expanded simulator scenario |
| [`beni-mellal.corridor.geojson`](beni-mellal.corridor.geojson) | GIS corridor and stations |
| [`beni-mellal.design-quality.yaml`](beni-mellal.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh beni-mellal
```
