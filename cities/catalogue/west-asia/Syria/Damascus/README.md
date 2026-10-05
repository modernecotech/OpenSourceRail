# Damascus — Urban Rail Network

**Country:** SY · **Population:** 2,503,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Damascus-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$8.00 bn (90.2%) of external capital** and **$10.33 bn of external interest**. Capital plus saved interest totals **$18.33 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **165.310 km to 141.874 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **65 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **222 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **222 metro-4car trainsets / 888 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Damascus rail network on OpenStreetMap](damascus-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 65 / 13 |
| Route length | 169.0 km double track |
| Direct transfers / reachable line pairs | 93.3% / 100.0% |
| Residents within 800 m radial station catchments | 1,106,168 (2020 raster; 25.9% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 222 × 4-car `metro-4car` trainsets (199 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 25.1 km | 13 | 50 | NE Outer ↔ SW Mid |
| line-2 | 24.1 km | 8 | 38 | SE Mid ↔ W Outer |
| line-3 | 22.4 km | 10 | 40 | S Mid ↔ N Outer |
| line-4 | 18.9 km | 7 | 31 | NW Outer ↔ SE Mid |
| line-5 | 22.5 km | 9 | 39 | NE Mid ↔ SW Outer |
| line-6 | 56.0 km | 18 | 24 | NW Mid ↔ W Mid |
| **Total** | **169.0 km** | **65 unique** | **222** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 65,574 train-km/day |
| Annual traction demand | 413.6 GWh |
| Station/depot PV / storage | 46.8 MW / 324.0 MWh |
| Aggregate charging power | 93.0 MW |
| Dedicated solar plant | 163.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 11.8 km / 127 kWh |
| Lowest traversal charging margin | line-2: 156 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $3.71 bn |
| Stations | $377 M |
| Depots | $113 M |
| Rolling stock | $249 M |
| Dedicated solar plant | $131 M |
| Residual train control | $8.5 M |
| Charging microgrids | $19 M |
| EPC / project services | $314 M |
| **Total city programme** | **$4.92 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $866 M (17.6%) |
| Domestic / local capital | $4.06 bn (82.4%) |
| Annual public construction commitment | $770 M / yr for 10 years |
| Annual post-grace debt service | $705 M / yr |
| External capital saved vs default turnkey sensitivity | $8.00 bn |
| Capital + lifetime external interest saved | $18.33 bn |
| Annual OPEX | $99 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 15 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 589 assets / 3,170 tasks | [`damascus-operations-manifest.json`](operations/damascus-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`damascus.toml`](damascus.toml) | Expanded simulator scenario |
| [`damascus.corridor.geojson`](damascus.corridor.geojson) | GIS corridor and stations |
| [`damascus.design-quality.yaml`](damascus.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh damascus
```
