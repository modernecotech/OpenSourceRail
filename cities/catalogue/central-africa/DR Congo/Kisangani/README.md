# Kisangani — Urban Rail Network

**Country:** CD · **Population:** 1,300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kisangani-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$882 M (88.9%) of external capital** and **$1.14 bn of external interest**. Capital plus saved interest totals **$2.02 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **43.121 km to 30.817 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **12 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**2 line-local depots** provide **43 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **43 metro-4car trainsets / 172 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Kisangani rail network on OpenStreetMap](kisangani-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 2 / 12 / 2 |
| Route length | 36.0 km double track |
| Coverage / transfer reachability | 49.0% / 100% |
| Estimated station catchment | 637,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 43 × 4-car `metro-4car` trainsets (37 peak revenue) |
| Peak network throughput | 38,400 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 21.7 km | 6 | 35 | W Outer ↔ SE Outer |
| line-2 | 14.3 km | 6 | 8 | W Inner ↔ SW Inner |
| **Total** | **36.0 km** | **12 unique** | **43** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 698 one-way journeys / 13,430 train-km/day |
| Annual traction demand | 84.7 GWh |
| Station/depot PV / storage | 13.0 MW / 95.0 MWh |
| Aggregate charging power | 18.0 MW |
| Dedicated solar plant | 40.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 6.8 km / 68 kWh |
| Lowest traversal charging margin | line-2: 137 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $338 M |
| Stations | $60 M |
| Depots | $32 M |
| Rolling stock | $48 M |
| Dedicated solar plant | $33 M |
| Residual train control | $1.8 M |
| Charging microgrids | $4.0 M |
| EPC / project services | $34 M |
| **Total city programme** | **$551 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $110 M (19.9%) |
| Domestic / local capital | $441 M (80.1%) |
| Annual public construction commitment | $60 M / yr for 10 years |
| Annual post-grace debt service | $54 M / yr |
| External capital saved vs default turnkey sensitivity | $882 M |
| Capital + lifetime external interest saved | $2.02 bn |
| Annual OPEX | $12 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 4 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 113 assets / 602 tasks | [`kisangani-operations-manifest.json`](operations/kisangani-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kisangani.toml`](kisangani.toml) | Expanded simulator scenario |
| [`kisangani.corridor.geojson`](kisangani.corridor.geojson) | GIS corridor and stations |
| [`kisangani.design-quality.yaml`](kisangani.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kisangani
```
