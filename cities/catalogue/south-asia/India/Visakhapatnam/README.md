# Visakhapatnam — Urban Rail Network

**Country:** IN · **Population:** 2,300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Visakhapatnam-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.91 bn (88.7%) of external capital** and **$6.03 bn of external interest**. Capital plus saved interest totals **$10.94 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **171.319 km to 140.369 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **73 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **265 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **265 metro-4car trainsets / 1060 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Visakhapatnam rail network on OpenStreetMap](visakhapatnam-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 73 / 14 |
| Route length | 209.0 km double track |
| Coverage / transfer reachability | 47.8% / 60% |
| Estimated station catchment | 1,099,400 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 265 × 4-car `metro-4car` trainsets (238 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 36.0 km | 14 | 60 | E Outer ↔ SW Outer |
| line-2 | 38.6 km | 13 | 60 | SW Outer ↔ NE Outer |
| line-3 | 29.9 km | 10 | 51 | NW Outer ↔ SE Mid |
| line-4 | 22.0 km | 9 | 37 | W Outer ↔ NE Inner |
| line-5 | 19.2 km | 7 | 32 | N Mid ↔ S Inner |
| line-6 | 63.2 km | 20 | 25 | N Inner ↔ N Inner |
| **Total** | **209.0 km** | **73 unique** | **265** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 82,470 train-km/day |
| Annual traction demand | 520.2 GWh |
| Station/depot PV / storage | 47.7 MW / 328.5 MWh |
| Aggregate charging power | 97.5 MW |
| Dedicated solar plant | 286.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 14.7 km / 147 kWh |
| Lowest traversal charging margin | line-4: 150 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.86 bn |
| Stations | $348 M |
| Depots | $122 M |
| Rolling stock | $297 M |
| Dedicated solar plant | $229 M |
| Residual train control | $10 M |
| Charging microgrids | $20 M |
| EPC / project services | $186 M |
| **Total city programme** | **$3.08 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $628 M (20.4%) |
| Domestic / local capital | $2.45 bn (79.6%) |
| Annual public construction commitment | $267 M / yr for 5 years |
| Annual post-grace debt service | $191 M / yr |
| External capital saved vs default turnkey sensitivity | $4.91 bn |
| Capital + lifetime external interest saved | $10.94 bn |
| Annual OPEX | $72 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 26 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 673 assets / 3,687 tasks | [`visakhapatnam-operations-manifest.json`](operations/visakhapatnam-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`visakhapatnam.toml`](visakhapatnam.toml) | Expanded simulator scenario |
| [`visakhapatnam.corridor.geojson`](visakhapatnam.corridor.geojson) | GIS corridor and stations |
| [`visakhapatnam.design-quality.yaml`](visakhapatnam.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh visakhapatnam
```
