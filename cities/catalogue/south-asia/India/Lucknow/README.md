# Lucknow — Urban Rail Network

**Country:** IN · **Population:** 3,500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Lucknow-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$8.50 bn (88.0%) of external capital** and **$10.45 bn of external interest**. Capital plus saved interest totals **$18.95 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **304.094 km to 252.188 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **99 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**8 line-local depots** provide **478 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **478 metro-6car trainsets / 2868 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Lucknow rail network on OpenStreetMap](lucknow-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 8 / 99 / 18 |
| Route length | 322.1 km double track |
| Coverage / transfer reachability | 38.3% / 54% |
| Estimated station catchment | 1,340,500 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 478 × 6-car `metro-6car` trainsets (431 peak revenue) |
| Peak network throughput | 230,400 passengers/hour |
| Practical service capacity | 2,008,800 passenger-trips/day |
| Annual paid-trip planning range | 366.6–586.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 43.1 km | 12 | 78 | W Mid ↔ E Outer |
| line-2 | 27.2 km | 11 | 52 | S Mid ↔ N Mid |
| line-3 | 22.4 km | 7 | 42 | SW Mid ↔ E Mid |
| line-4 | 17.3 km | 6 | 31 | S Inner ↔ N Inner |
| line-5 | 49.5 km | 16 | 93 | SW Mid ↔ NE Outer |
| line-6 | 42.1 km | 12 | 76 | SE Outer ↔ W Mid |
| line-7 | 34.5 km | 11 | 67 | SE Inner ↔ W Outer |
| line-8 | 86.1 km | 24 | 39 | W Mid ↔ W Mid |
| **Total** | **322.1 km** | **99 unique** | **478** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,488 one-way journeys / 129,774 train-km/day |
| Annual traction demand | 1,227.8 GWh |
| Station/depot PV / storage | 63.4 MW / 476.0 MWh |
| Aggregate charging power | 170.0 MW |
| Dedicated solar plant | 571.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-5: 21.8 km / 352 kWh |
| Lowest traversal charging margin | line-4: 150 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $3.08 bn |
| Stations | $441 M |
| Depots | $218 M |
| Rolling stock | $803 M |
| Dedicated solar plant | $457 M |
| Residual train control | $16 M |
| Charging microgrids | $35 M |
| EPC / project services | $321 M |
| **Total city programme** | **$5.37 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.16 bn (21.6%) |
| Domestic / local capital | $4.21 bn (78.4%) |
| Annual public construction commitment | $463 M / yr for 5 years |
| Annual post-grace debt service | $332 M / yr |
| External capital saved vs default turnkey sensitivity | $8.50 bn |
| Capital + lifetime external interest saved | $18.95 bn |
| Annual OPEX | $129 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 31 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,047 assets / 6,078 tasks | [`lucknow-operations-manifest.json`](operations/lucknow-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`lucknow.toml`](lucknow.toml) | Expanded simulator scenario |
| [`lucknow.corridor.geojson`](lucknow.corridor.geojson) | GIS corridor and stations |
| [`lucknow.design-quality.yaml`](lucknow.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh lucknow
```
