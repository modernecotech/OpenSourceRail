# Gujranwala — Urban Rail Network

**Country:** PK · **Population:** 2,300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Gujranwala-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.74 bn (88.9%) of external capital** and **$4.69 bn of external interest**. Capital plus saved interest totals **$8.44 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **149.144 km to 128.595 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **50 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**5 line-local depots** provide **207 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **207 metro-4car trainsets / 828 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Gujranwala rail network on OpenStreetMap](gujranwala-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 5 / 50 / 8 |
| Route length | 173.3 km double track |
| Coverage / transfer reachability | 47.0% / 50% |
| Estimated station catchment | 1,081,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 207 × 4-car `metro-4car` trainsets (185 peak revenue) |
| Peak network throughput | 96,000 passengers/hour |
| Practical service capacity | 803,520 passenger-trips/day |
| Annual paid-trip planning range | 146.6–234.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 35.1 km | 10 | 57 | NW Mid ↔ S Outer |
| line-2 | 31.3 km | 9 | 51 | NE Outer ↔ SW Inner |
| line-3 | 18.1 km | 6 | 29 | NW Mid ↔ S Mid |
| line-4 | 29.0 km | 8 | 46 | W Mid ↔ SE Outer |
| line-5 | 59.8 km | 17 | 24 | NW Mid ↔ NW Mid |
| **Total** | **173.3 km** | **50 unique** | **207** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,092 one-way journeys / 66,669 train-km/day |
| Annual traction demand | 420.5 GWh |
| Station/depot PV / storage | 36.4 MW / 257.0 MWh |
| Aggregate charging power | 64.5 MW |
| Dedicated solar plant | 178.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 13.9 km / 149 kWh |
| Lowest traversal charging margin | line-4: 98 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.49 bn |
| Stations | $208 M |
| Depots | $98 M |
| Rolling stock | $232 M |
| Dedicated solar plant | $143 M |
| Residual train control | $8.7 M |
| Charging microgrids | $13 M |
| EPC / project services | $144 M |
| **Total city programme** | **$2.34 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $467 M (20.0%) |
| Domestic / local capital | $1.87 bn (80.0%) |
| Annual public construction commitment | $322 M / yr for 7 years |
| Annual post-grace debt service | $276 M / yr |
| External capital saved vs default turnkey sensitivity | $3.74 bn |
| Capital + lifetime external interest saved | $8.44 bn |
| Annual OPEX | $53 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 19 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 491 assets / 2,750 tasks | [`gujranwala-operations-manifest.json`](operations/gujranwala-operations-manifest.json) |

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
