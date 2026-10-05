# Omdurman — Urban Rail Network

**Country:** SD · **Population:** 2,800,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Omdurman-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$5.00 bn (88.9%) of external capital** and **$6.46 bn of external interest**. Capital plus saved interest totals **$11.45 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **193.147 km to 158.400 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **75 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **271 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **271 metro-4car trainsets / 1084 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Omdurman rail network on OpenStreetMap](omdurman-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 75 / 12 |
| Route length | 223.0 km double track |
| Coverage / transfer reachability | 48.7% / 73% |
| Estimated station catchment | 1,363,600 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 271 × 4-car `metro-4car` trainsets (244 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 32.2 km | 12 | 53 | SE Outer ↔ NW Mid |
| line-2 | 32.4 km | 11 | 50 | NE Mid ↔ SW Outer |
| line-3 | 32.5 km | 11 | 51 | N Outer ↔ S Outer |
| line-4 | 29.9 km | 10 | 47 | W Mid ↔ E Outer |
| line-5 | 23.2 km | 9 | 40 | SE Outer ↔ W Mid |
| line-6 | 72.8 km | 22 | 30 | W Mid ↔ W Mid |
| **Total** | **223.0 km** | **75 unique** | **271** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 86,774 train-km/day |
| Annual traction demand | 547.3 GWh |
| Station/depot PV / storage | 50.1 MW / 340.5 MWh |
| Aggregate charging power | 109.5 MW |
| Dedicated solar plant | 229.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 10.2 km / 110 kWh |
| Lowest traversal charging margin | line-2: 155 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.93 bn |
| Stations | $353 M |
| Depots | $123 M |
| Rolling stock | $304 M |
| Dedicated solar plant | $184 M |
| Residual train control | $11 M |
| Charging microgrids | $23 M |
| EPC / project services | $192 M |
| **Total city programme** | **$3.12 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $624 M (20.0%) |
| Domestic / local capital | $2.50 bn (80.0%) |
| Annual public construction commitment | $378 M / yr for 10 years |
| Annual post-grace debt service | $343 M / yr |
| External capital saved vs default turnkey sensitivity | $5.00 bn |
| Capital + lifetime external interest saved | $11.45 bn |
| Annual OPEX | $68 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 34 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 696 assets / 3,802 tasks | [`omdurman-operations-manifest.json`](operations/omdurman-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`omdurman.toml`](omdurman.toml) | Expanded simulator scenario |
| [`omdurman.corridor.geojson`](omdurman.corridor.geojson) | GIS corridor and stations |
| [`omdurman.design-quality.yaml`](omdurman.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh omdurman
```
