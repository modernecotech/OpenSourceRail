# Gaza-City — Urban Rail Network

**Country:** PS · **Population:** 600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Gaza-City-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$696 M (88.2%) of external capital** and **$873 M of external interest**. Capital plus saved interest totals **$1.57 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **31.953 km to 19.561 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **11 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **90 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **90 light-metro-3car trainsets / 270 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Gaza-City rail network on OpenStreetMap](gaza-city-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 11 / 0 |
| Route length | 28.2 km double track |
| Coverage / transfer reachability | 43.8% / 0% |
| Estimated station catchment | 262,800 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 90 × 3-car `light-metro-3car` trainsets (81 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  8.6 km | 4 | 27 | NE Mid ↔ W Mid |
| line-2 | 13.9 km | 4 | 43 | NE Mid ↔ SW Outer |
| line-3 |  5.7 km | 3 | 20 | SE Inner ↔ N Mid |
| **Total** | **28.2 km** | **11 unique** | **90** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 13,123 train-km/day |
| Annual traction demand | 62.1 GWh |
| Station/depot PV / storage | 17.1 MW / 123.5 MWh |
| Aggregate charging power | 5.0 MW |
| Dedicated solar plant | 15.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 10.9 km / 79 kWh |
| Lowest traversal charging margin | line-3: 28 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $227 M |
| Stations | $40 M |
| Depots | $47 M |
| Rolling stock | $81 M |
| Dedicated solar plant | $13 M |
| Residual train control | $1.4 M |
| Charging microgrids | $1.1 M |
| EPC / project services | $28 M |
| **Total city programme** | **$439 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $93 M (21.3%) |
| Domestic / local capital | $345 M (78.7%) |
| Annual public construction commitment | $38 M / yr for 7 years |
| Annual post-grace debt service | $31 M / yr |
| External capital saved vs default turnkey sensitivity | $696 M |
| Capital + lifetime external interest saved | $1.57 bn |
| Annual OPEX | $14 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 3 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 165 assets / 1,009 tasks | [`gaza-city-operations-manifest.json`](operations/gaza-city-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`gaza-city.toml`](gaza-city.toml) | Expanded simulator scenario |
| [`gaza-city.corridor.geojson`](gaza-city.corridor.geojson) | GIS corridor and stations |
| [`gaza-city.design-quality.yaml`](gaza-city.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh gaza-city
```
