# Mwanza — Urban Rail Network

**Country:** TZ · **Population:** 1,100,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Mwanza-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.53 bn (88.7%) of external capital** and **$4.43 bn of external interest**. Capital plus saved interest totals **$7.96 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **153.851 km to 120.162 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **53 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **191 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **191 metro-4car trainsets / 764 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Mwanza rail network on OpenStreetMap](mwanza-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 53 / 8 |
| Route length | 145.7 km double track |
| Coverage / transfer reachability | 67.9% / 53% |
| Estimated station catchment | 746,900 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 191 × 4-car `metro-4car` trainsets (171 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 18.4 km | 7 | 31 | S Mid ↔ N Mid |
| line-2 | 19.9 km | 8 | 35 | W Mid ↔ E Mid |
| line-3 | 16.1 km | 6 | 27 | SW Mid ↔ NW Mid |
| line-4 | 23.8 km | 9 | 39 | NE Outer ↔ W Mid |
| line-5 | 25.4 km | 9 | 42 | NW Mid ↔ SE Outer |
| line-6 | 42.1 km | 14 | 17 | N Mid ↔ N Mid |
| **Total** | **145.7 km** | **53 unique** | **191** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 57,974 train-km/day |
| Annual traction demand | 365.7 GWh |
| Station/depot PV / storage | 42.6 MW / 303.0 MWh |
| Aggregate charging power | 72.0 MW |
| Dedicated solar plant | 191.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-5: 12.4 km / 124 kWh |
| Lowest traversal charging margin | line-3: 118 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.32 bn |
| Stations | $261 M |
| Depots | $106 M |
| Rolling stock | $214 M |
| Dedicated solar plant | $153 M |
| Residual train control | $7.3 M |
| Charging microgrids | $15 M |
| EPC / project services | $135 M |
| **Total city programme** | **$2.21 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $450 M (20.4%) |
| Domestic / local capital | $1.76 bn (79.6%) |
| Annual public construction commitment | $204 M / yr for 7 years |
| Annual post-grace debt service | $167 M / yr |
| External capital saved vs default turnkey sensitivity | $3.53 bn |
| Capital + lifetime external interest saved | $7.96 bn |
| Annual OPEX | $50 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 15 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 491 assets / 2,662 tasks | [`mwanza-operations-manifest.json`](operations/mwanza-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`mwanza.toml`](mwanza.toml) | Expanded simulator scenario |
| [`mwanza.corridor.geojson`](mwanza.corridor.geojson) | GIS corridor and stations |
| [`mwanza.design-quality.yaml`](mwanza.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh mwanza
```
