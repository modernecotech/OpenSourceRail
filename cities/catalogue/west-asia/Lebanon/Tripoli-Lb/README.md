# Tripoli-Lb — Urban Rail Network

**Country:** LB · **Population:** 730,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Tripoli-Lb-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.10 bn (88.5%) of external capital** and **$1.39 bn of external interest**. Capital plus saved interest totals **$2.49 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **42.354 km to 33.812 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **17 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **129 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **129 light-metro-3car trainsets / 387 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Tripoli-Lb rail network on OpenStreetMap](tripoli-lb-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 17 / 0 |
| Route length | 41.2 km double track |
| Coverage / transfer reachability | 40.5% / 0% |
| Estimated station catchment | 295,650 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 129 × 3-car `light-metro-3car` trainsets (116 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 12.0 km | 5 | 38 | NW Mid ↔ SE Mid |
| line-2 | 17.0 km | 7 | 53 | NE Outer ↔ SW Mid |
| line-3 | 12.2 km | 5 | 38 | W Mid ↔ SE Outer |
| **Total** | **41.2 km** | **17 unique** | **129** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 19,162 train-km/day |
| Annual traction demand | 90.6 GWh |
| Station/depot PV / storage | 19.2 MW / 127.0 MWh |
| Aggregate charging power | 8.5 MW |
| Dedicated solar plant | 29.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 4.6 km / 33 kWh |
| Lowest traversal charging margin | line-3: 46 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $390 M |
| Stations | $59 M |
| Depots | $54 M |
| Rolling stock | $116 M |
| Dedicated solar plant | $24 M |
| Residual train control | $2.1 M |
| Charging microgrids | $1.9 M |
| EPC / project services | $44 M |
| **Total city programme** | **$691 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $144 M (20.8%) |
| Domestic / local capital | $547 M (79.2%) |
| Annual public construction commitment | $130 M / yr for 8 years |
| Annual post-grace debt service | $118 M / yr |
| External capital saved vs default turnkey sensitivity | $1.10 bn |
| Capital + lifetime external interest saved | $2.49 bn |
| Annual OPEX | $19 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 9 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 241 assets / 1,478 tasks | [`tripoli-lb-operations-manifest.json`](operations/tripoli-lb-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`tripoli-lb.toml`](tripoli-lb.toml) | Expanded simulator scenario |
| [`tripoli-lb.corridor.geojson`](tripoli-lb.corridor.geojson) | GIS corridor and stations |
| [`tripoli-lb.design-quality.yaml`](tripoli-lb.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh tripoli-lb
```
