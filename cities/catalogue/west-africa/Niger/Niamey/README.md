# Niamey — Urban Rail Network

**Country:** NE · **Population:** 1,407,635 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Niamey-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$13.54 bn (90.9%) of external capital** and **$17.49 bn of external interest**. Capital plus saved interest totals **$31.03 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **145.326 km to 131.664 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **64 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **197 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **197 metro-4car trainsets / 788 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Niamey rail network on OpenStreetMap](niamey-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 64 / 12 |
| Route length | 141.8 km double track |
| Coverage / transfer reachability | 49.5% / 87% |
| Estimated station catchment | 696,779 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 197 × 4-car `metro-4car` trainsets (177 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 22.7 km | 10 | 40 | SE Outer ↔ N Mid |
| line-2 | 15.7 km | 8 | 31 | NW Mid ↔ E Mid |
| line-3 | 14.2 km | 8 | 30 | NE Mid ↔ SW Mid |
| line-4 | 19.3 km | 10 | 39 | W Mid ↔ SE Outer |
| line-5 | 18.8 km | 9 | 36 | NW Outer ↔ S Mid |
| line-6 | 51.1 km | 19 | 21 | NW Mid ↔ NW Mid |
| **Total** | **141.8 km** | **64 unique** | **197** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 54,046 train-km/day |
| Annual traction demand | 340.9 GWh |
| Station/depot PV / storage | 46.8 MW / 324.0 MWh |
| Aggregate charging power | 93.0 MW |
| Dedicated solar plant | 111.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 7.5 km / 83 kWh |
| Lowest traversal charging margin | line-1: 237 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $6.93 bn |
| Stations | $359 M |
| Depots | $108 M |
| Rolling stock | $221 M |
| Dedicated solar plant | $89 M |
| Residual train control | $7.1 M |
| Charging microgrids | $19 M |
| EPC / project services | $535 M |
| **Total city programme** | **$8.27 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.35 bn (16.3%) |
| Domestic / local capital | $6.92 bn (83.7%) |
| Annual public construction commitment | $697 M / yr for 10 years |
| Annual post-grace debt service | $622 M / yr |
| External capital saved vs default turnkey sensitivity | $13.54 bn |
| Capital + lifetime external interest saved | $31.03 bn |
| Annual OPEX | $162 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 17 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 556 assets / 2,927 tasks | [`niamey-operations-manifest.json`](operations/niamey-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`niamey.toml`](niamey.toml) | Expanded simulator scenario |
| [`niamey.corridor.geojson`](niamey.corridor.geojson) | GIS corridor and stations |
| [`niamey.design-quality.yaml`](niamey.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh niamey
```
