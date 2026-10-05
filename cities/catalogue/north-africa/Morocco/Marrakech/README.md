# Marrakech — Urban Rail Network

**Country:** MA · **Population:** 1,200,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Marrakech-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.43 bn (89.2%) of external capital** and **$5.45 bn of external interest**. Capital plus saved interest totals **$9.88 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **162.306 km to 141.171 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 1 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **52 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **228 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **228 metro-4car trainsets / 912 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Marrakech rail network on OpenStreetMap](marrakech-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 52 / 7 |
| Route length | 175.2 km double track |
| Coverage / transfer reachability | 50.9% / 53% |
| Estimated station catchment | 610,800 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 228 × 4-car `metro-4car` trainsets (204 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 27.1 km | 9 | 46 | W Inner ↔ SE Outer |
| line-2 | 24.3 km | 6 | 38 | NE Outer ↔ SW Inner |
| line-3 | 21.7 km | 7 | 34 | W Inner ↔ E Outer |
| line-4 | 25.7 km | 7 | 42 | SW Outer ↔ NE Mid |
| line-5 | 29.5 km | 9 | 48 | S Mid ↔ NW Outer |
| line-6 | 46.9 km | 14 | 20 | W Inner ↔ W Inner |
| **Total** | **175.2 km** | **52 unique** | **228** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 70,568 train-km/day |
| Annual traction demand | 445.1 GWh |
| Station/depot PV / storage | 40.8 MW / 294.0 MWh |
| Aggregate charging power | 63.0 MW |
| Dedicated solar plant | 186.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-4: 13.0 km / 140 kWh |
| Lowest traversal charging margin | line-2: 80 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.84 bn |
| Stations | $210 M |
| Depots | $114 M |
| Rolling stock | $255 M |
| Dedicated solar plant | $149 M |
| Residual train control | $8.8 M |
| Charging microgrids | $13 M |
| EPC / project services | $171 M |
| **Total city programme** | **$2.76 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $538 M (19.5%) |
| Domestic / local capital | $2.22 bn (80.5%) |
| Annual public construction commitment | $193 M / yr for 5 years |
| Annual post-grace debt service | $133 M / yr |
| External capital saved vs default turnkey sensitivity | $4.43 bn |
| Capital + lifetime external interest saved | $9.88 bn |
| Annual OPEX | $70 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 17 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 524 assets / 2,963 tasks | [`marrakech-operations-manifest.json`](operations/marrakech-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`marrakech.toml`](marrakech.toml) | Expanded simulator scenario |
| [`marrakech.corridor.geojson`](marrakech.corridor.geojson) | GIS corridor and stations |
| [`marrakech.design-quality.yaml`](marrakech.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh marrakech
```
