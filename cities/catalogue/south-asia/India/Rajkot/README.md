# Rajkot — Urban Rail Network

**Country:** IN · **Population:** 1,800,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Rajkot-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.03 bn (89.3%) of external capital** and **$3.72 bn of external interest**. Capital plus saved interest totals **$6.75 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **122.630 km to 101.482 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **43 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**5 line-local depots** provide **143 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **143 metro-4car trainsets / 572 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Rajkot rail network on OpenStreetMap](rajkot-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 5 / 43 / 3 |
| Route length | 118.3 km double track |
| Coverage / transfer reachability | 64.4% / 100% |
| Estimated station catchment | 1,159,200 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 143 × 4-car `metro-4car` trainsets (127 peak revenue) |
| Peak network throughput | 96,000 passengers/hour |
| Practical service capacity | 803,520 passenger-trips/day |
| Annual paid-trip planning range | 146.6–234.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 21.1 km | 8 | 36 | NE Outer ↔ S Mid |
| line-2 | 12.1 km | 6 | 25 | E Mid ↔ SW Mid |
| line-3 | 12.7 km | 6 | 25 | SE Mid ↔ NW Inner |
| line-4 | 21.8 km | 8 | 36 | W Mid ↔ SE Outer |
| line-5 | 50.6 km | 15 | 21 | NW Outer ↔ NW Outer |
| **Total** | **118.3 km** | **43 unique** | **143** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,092 one-way journeys / 43,252 train-km/day |
| Annual traction demand | 272.8 GWh |
| Station/depot PV / storage | 34.0 MW / 245.0 MWh |
| Aggregate charging power | 51.0 MW |
| Dedicated solar plant | 104.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-5: 34.0 km / 365 kWh |
| Lowest traversal charging margin | line-4: 159 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.23 bn |
| Stations | $195 M |
| Depots | $85 M |
| Rolling stock | $160 M |
| Dedicated solar plant | $83 M |
| Residual train control | $5.9 M |
| Charging microgrids | $11 M |
| EPC / project services | $118 M |
| **Total city programme** | **$1.88 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $363 M (19.2%) |
| Domestic / local capital | $1.52 bn (80.8%) |
| Annual public construction commitment | $165 M / yr for 5 years |
| Annual post-grace debt service | $117 M / yr |
| External capital saved vs default turnkey sensitivity | $3.03 bn |
| Capital + lifetime external interest saved | $6.75 bn |
| Annual OPEX | $44 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 10 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 381 assets / 2,034 tasks | [`rajkot-operations-manifest.json`](operations/rajkot-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`rajkot.toml`](rajkot.toml) | Expanded simulator scenario |
| [`rajkot.corridor.geojson`](rajkot.corridor.geojson) | GIS corridor and stations |
| [`rajkot.design-quality.yaml`](rajkot.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh rajkot
```
