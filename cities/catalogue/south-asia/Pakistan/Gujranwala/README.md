# Gujranwala — Urban Rail Network

**Country:** PK · **Population:** 2,300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Gujranwala-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.03 bn (89.0%) of external capital** and **$5.05 bn of external interest**. Capital plus saved interest totals **$9.07 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **149.144 km to 140.455 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **56 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**5 line-local depots** provide **213 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **213 metro-4car trainsets / 852 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Gujranwala rail network on OpenStreetMap](gujranwala-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 5 / 56 / 12 |
| Route length | 175.1 km double track |
| Coverage / transfer reachability | 47.0% / 90% |
| Estimated station catchment | 1,081,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 213 × 4-car `metro-4car` trainsets (191 peak revenue) |
| Peak network throughput | 96,000 passengers/hour |
| Practical service capacity | 803,520 passenger-trips/day |
| Annual paid-trip planning range | 146.6–234.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 37.3 km | 12 | 59 | NW Mid ↔ S Outer |
| line-2 | 31.4 km | 10 | 52 | NE Outer ↔ SW Inner |
| line-3 | 17.6 km | 7 | 31 | NW Mid ↔ S Mid |
| line-4 | 28.7 km | 9 | 46 | W Mid ↔ SE Outer |
| line-5 | 60.0 km | 18 | 25 | NW Mid ↔ NW Mid |
| **Total** | **175.1 km** | **56 unique** | **213** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,092 one-way journeys / 67,454 train-km/day |
| Annual traction demand | 425.4 GWh |
| Station/depot PV / storage | 37.6 MW / 263.0 MWh |
| Aggregate charging power | 70.5 MW |
| Dedicated solar plant | 180.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 14.8 km / 159 kWh |
| Lowest traversal charging margin | line-4: 114 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.56 bn |
| Stations | $287 M |
| Depots | $101 M |
| Rolling stock | $239 M |
| Dedicated solar plant | $144 M |
| Residual train control | $8.8 M |
| Charging microgrids | $15 M |
| EPC / project services | $155 M |
| **Total city programme** | **$2.51 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $499 M (19.9%) |
| Domestic / local capital | $2.01 bn (80.1%) |
| Annual public construction commitment | $346 M / yr for 7 years |
| Annual post-grace debt service | $297 M / yr |
| External capital saved vs default turnkey sensitivity | $4.03 bn |
| Capital + lifetime external interest saved | $9.07 bn |
| Annual OPEX | $57 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 14 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 525 assets / 2,904 tasks | [`gujranwala-operations-manifest.json`](operations/gujranwala-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`gujranwala.toml`](gujranwala.toml) | Expanded simulator scenario |
| [`gujranwala.corridor.geojson`](gujranwala.corridor.geojson) | GIS corridor and stations |
| [`gujranwala.design-quality.yaml`](gujranwala.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh gujranwala
```
