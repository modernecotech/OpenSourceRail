# Soroti — Urban Rail Network

**Country:** UG · **Population:** 200,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Soroti-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$176 M (88.8%) of external capital** and **$220 M of external interest**. Capital plus saved interest totals **$396 M**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **7.900 km to 4.423 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **4 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**2 line-local depots** provide **17 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **17 tram-2car trainsets / 34 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Soroti rail network on OpenStreetMap](soroti-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 2 / 4 / 0 |
| Route length | 5.0 km double track |
| Coverage / transfer reachability | 49.4% / 0% |
| Estimated station catchment | 98,800 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 17 × 2-car `tram-2car` trainsets (13 peak revenue) |
| Peak network throughput | 19,200 passengers/hour |
| Practical service capacity | 178,560 passenger-trips/day |
| Annual paid-trip planning range | 32.6–52.1 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  2.8 km | 2 | 9 | N Outer ↔ SW Mid |
| line-2 |  2.2 km | 2 | 8 | S Outer ↔ E Mid |
| **Total** | **5.0 km** | **4 unique** | **17** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 930 one-way journeys / 2,314 train-km/day |
| Annual traction demand | 7.3 GWh |
| Station/depot PV / storage | 10.6 MW / 81.0 MWh |
| Aggregate charging power | 2.0 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 2.8 km / 14 kWh |
| Lowest traversal charging margin | line-2: 37 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $48 M |
| Stations | $18 M |
| Depots | $25 M |
| Rolling stock | $9.5 M |
| Residual train control | $249 k |
| Charging microgrids | $550 k |
| EPC / project services | $7.2 M |
| **Total city programme** | **$110 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $22 M (20.1%) |
| Domestic / local capital | $88 M (79.9%) |
| Annual public construction commitment | $13 M / yr for 7 years |
| Annual post-grace debt service | $11 M / yr |
| External capital saved vs default turnkey sensitivity | $176 M |
| Capital + lifetime external interest saved | $396 M |
| Annual OPEX | $2.9 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 0 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 46 assets / 223 tasks | [`soroti-operations-manifest.json`](operations/soroti-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`soroti.toml`](soroti.toml) | Expanded simulator scenario |
| [`soroti.corridor.geojson`](soroti.corridor.geojson) | GIS corridor and stations |
| [`soroti.design-quality.yaml`](soroti.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh soroti
```
