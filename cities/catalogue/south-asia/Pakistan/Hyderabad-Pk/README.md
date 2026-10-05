# Hyderabad-Pk — Urban Rail Network

**Country:** PK · **Population:** 1,900,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Hyderabad-Pk-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.83 bn (89.6%) of external capital** and **$6.06 bn of external interest**. Capital plus saved interest totals **$10.90 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **157.380 km to 126.296 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 1 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **53 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **200 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **200 metro-4car trainsets / 800 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Hyderabad-Pk rail network on OpenStreetMap](hyderabad-pk-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 53 / 12 |
| Route length | 159.1 km double track |
| Coverage / transfer reachability | 49.3% / 80% |
| Estimated station catchment | 936,700 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 200 × 4-car `metro-4car` trainsets (179 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 14.5 km | 6 | 26 | NE Mid ↔ SW Mid |
| line-2 | 17.6 km | 7 | 31 | W Mid ↔ SE Mid |
| line-3 | 15.9 km | 7 | 29 | S Mid ↔ N Mid |
| line-4 | 27.8 km | 9 | 46 | SE Mid ↔ N Outer |
| line-5 | 28.6 km | 9 | 47 | W Mid ↔ E Outer |
| line-6 | 54.6 km | 15 | 21 | W Mid ↔ W Mid |
| **Total** | **159.1 km** | **53 unique** | **200** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 61,263 train-km/day |
| Annual traction demand | 386.4 GWh |
| Station/depot PV / storage | 43.2 MW / 306.0 MWh |
| Aggregate charging power | 75.0 MW |
| Dedicated solar plant | 153.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-5: 10.2 km / 110 kWh |
| Lowest traversal charging margin | line-1: 171 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.07 bn |
| Stations | $265 M |
| Depots | $108 M |
| Rolling stock | $224 M |
| Dedicated solar plant | $123 M |
| Residual train control | $8.0 M |
| Charging microgrids | $16 M |
| EPC / project services | $188 M |
| **Total city programme** | **$3.00 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $562 M (18.7%) |
| Domestic / local capital | $2.44 bn (81.3%) |
| Annual public construction commitment | $416 M / yr for 7 years |
| Annual post-grace debt service | $357 M / yr |
| External capital saved vs default turnkey sensitivity | $4.83 bn |
| Capital + lifetime external interest saved | $10.90 bn |
| Annual OPEX | $66 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 18 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 503 assets / 2,752 tasks | [`hyderabad-pk-operations-manifest.json`](operations/hyderabad-pk-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`hyderabad-pk.toml`](hyderabad-pk.toml) | Expanded simulator scenario |
| [`hyderabad-pk.corridor.geojson`](hyderabad-pk.corridor.geojson) | GIS corridor and stations |
| [`hyderabad-pk.design-quality.yaml`](hyderabad-pk.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh hyderabad-pk
```
