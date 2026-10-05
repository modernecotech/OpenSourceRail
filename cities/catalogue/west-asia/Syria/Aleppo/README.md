# Aleppo — Urban Rail Network

**Country:** SY · **Population:** 1,639,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Aleppo-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.03 bn (88.9%) of external capital** and **$5.21 bn of external interest**. Capital plus saved interest totals **$9.24 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **160.184 km to 141.361 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **64 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **211 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **211 metro-4car trainsets / 844 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Aleppo rail network on OpenStreetMap](aleppo-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 64 / 12 |
| Route length | 160.2 km double track |
| Direct transfers / reachable line pairs | 93.3% / 100.0% |
| Residents within 800 m radial station catchments | 1,077,489 (2020 raster; 32.1% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 211 × 4-car `metro-4car` trainsets (190 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 23.8 km | 11 | 43 | SW Outer ↔ NE Mid |
| line-2 | 24.2 km | 10 | 42 | SE Outer ↔ NW Outer |
| line-3 | 13.3 km | 7 | 27 | NE Mid ↔ SW Mid |
| line-4 | 20.7 km | 9 | 38 | W Outer ↔ E Mid |
| line-5 | 23.9 km | 9 | 40 | N Outer ↔ S Outer |
| line-6 | 54.4 km | 18 | 21 | W Mid ↔ W Mid |
| **Total** | **160.2 km** | **64 unique** | **211** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 61,855 train-km/day |
| Annual traction demand | 390.1 GWh |
| Station/depot PV / storage | 46.8 MW / 324.0 MWh |
| Aggregate charging power | 93.0 MW |
| Dedicated solar plant | 169.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 8.7 km / 84 kWh |
| Lowest traversal charging margin | line-5: 238 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.49 bn |
| Stations | $360 M |
| Depots | $110 M |
| Rolling stock | $236 M |
| Dedicated solar plant | $136 M |
| Residual train control | $8.0 M |
| Charging microgrids | $19 M |
| EPC / project services | $156 M |
| **Total city programme** | **$2.52 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $502 M (19.9%) |
| Domestic / local capital | $2.02 bn (80.1%) |
| Annual public construction commitment | $385 M / yr for 10 years |
| Annual post-grace debt service | $355 M / yr |
| External capital saved vs default turnkey sensitivity | $4.03 bn |
| Capital + lifetime external interest saved | $9.24 bn |
| Annual OPEX | $54 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 17 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 572 assets / 3,055 tasks | [`aleppo-operations-manifest.json`](operations/aleppo-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`aleppo.toml`](aleppo.toml) | Expanded simulator scenario |
| [`aleppo.corridor.geojson`](aleppo.corridor.geojson) | GIS corridor and stations |
| [`aleppo.design-quality.yaml`](aleppo.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh aleppo
```
