# Bukavu — Urban Rail Network

**Country:** CD · **Population:** 1,000,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Bukavu-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.00 bn (90.4%) of external capital** and **$5.16 bn of external interest**. Capital plus saved interest totals **$9.16 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **50.522 km to 42.030 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **21 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **166 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **166 light-metro-3car trainsets / 498 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Bukavu rail network on OpenStreetMap](bukavu-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 21 / 3 |
| Route length | 53.0 km double track |
| Direct transfers / reachable line pairs | 100.0% / 100.0% |
| Residents within 800 m radial station catchments | 252,796 (2020 raster; 23.6% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 166 × 3-car `light-metro-3car` trainsets (149 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 13.6 km | 7 | 45 | NE Mid ↔ SW Mid |
| line-2 | 22.0 km | 8 | 69 | NW Outer ↔ SE Outer |
| line-3 | 17.4 km | 6 | 52 | SW Mid ↔ NE Outer |
| **Total** | **53.0 km** | **21 unique** | **166** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 24,664 train-km/day |
| Annual traction demand | 116.7 GWh |
| Station/depot PV / storage | 20.1 MW / 128.5 MWh |
| Aggregate charging power | 10.0 MW |
| Dedicated solar plant | 53.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 9.5 km / 71 kWh |
| Lowest traversal charging margin | line-3: 52 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.93 bn |
| Stations | $113 M |
| Depots | $60 M |
| Rolling stock | $149 M |
| Dedicated solar plant | $43 M |
| Residual train control | $2.7 M |
| Charging microgrids | $2.1 M |
| EPC / project services | $158 M |
| **Total city programme** | **$2.46 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $424 M (17.3%) |
| Domestic / local capital | $2.03 bn (82.7%) |
| Annual public construction commitment | $271 M / yr for 10 years |
| Annual post-grace debt service | $243 M / yr |
| External capital saved vs default turnkey sensitivity | $4.00 bn |
| Capital + lifetime external interest saved | $9.16 bn |
| Annual OPEX | $51 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 3 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 302 assets / 1,884 tasks | [`bukavu-operations-manifest.json`](operations/bukavu-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`bukavu.toml`](bukavu.toml) | Expanded simulator scenario |
| [`bukavu.corridor.geojson`](bukavu.corridor.geojson) | GIS corridor and stations |
| [`bukavu.design-quality.yaml`](bukavu.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh bukavu
```
