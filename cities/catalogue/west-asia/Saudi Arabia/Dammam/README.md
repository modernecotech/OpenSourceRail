# Dammam — Urban Rail Network

**Country:** SA · **Population:** 1,500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Dammam-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$5.23 bn (88.8%) of external capital** and **$6.43 bn of external interest**. Capital plus saved interest totals **$11.67 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **178.222 km to 147.832 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **83 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **300 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **300 metro-4car trainsets / 1200 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Dammam rail network on OpenStreetMap](dammam-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 83 / 13 |
| Route length | 243.2 km double track |
| Coverage / transfer reachability | 39.5% / 47% |
| Estimated station catchment | 592,500 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 300 × 4-car `metro-4car` trainsets (270 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 42.3 km | 17 | 72 | SE Outer ↔ NW Outer |
| line-2 | 34.1 km | 13 | 57 | NW Outer ↔ E Mid |
| line-3 | 25.7 km | 9 | 41 | E Mid ↔ SW Mid |
| line-4 | 28.4 km | 10 | 46 | SW Outer ↔ E Mid |
| line-5 | 33.0 km | 12 | 53 | N Outer ↔ S Outer |
| line-6 | 79.7 km | 22 | 31 | NW Mid ↔ W Mid |
| **Total** | **243.2 km** | **83 unique** | **300** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 94,546 train-km/day |
| Annual traction demand | 596.3 GWh |
| Station/depot PV / storage | 52.2 MW / 351.0 MWh |
| Aggregate charging power | 120.0 MW |
| Dedicated solar plant | 253.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 7.3 km / 79 kWh |
| Lowest traversal charging margin | line-3: 186 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.98 bn |
| Stations | $392 M |
| Depots | $128 M |
| Rolling stock | $336 M |
| Dedicated solar plant | $202 M |
| Residual train control | $12 M |
| Charging microgrids | $25 M |
| EPC / project services | $201 M |
| **Total city programme** | **$3.27 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $662 M (20.2%) |
| Domestic / local capital | $2.61 bn (79.8%) |
| Annual public construction commitment | $228 M / yr for 5 years |
| Annual post-grace debt service | $158 M / yr |
| External capital saved vs default turnkey sensitivity | $5.23 bn |
| Capital + lifetime external interest saved | $11.67 bn |
| Annual OPEX | $148 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 39 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 768 assets / 4,207 tasks | [`dammam-operations-manifest.json`](operations/dammam-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`dammam.toml`](dammam.toml) | Expanded simulator scenario |
| [`dammam.corridor.geojson`](dammam.corridor.geojson) | GIS corridor and stations |
| [`dammam.design-quality.yaml`](dammam.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh dammam
```
