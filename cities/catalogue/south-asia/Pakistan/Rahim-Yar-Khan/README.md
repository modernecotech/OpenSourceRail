# Rahim-Yar-Khan — Urban Rail Network

**Country:** PK · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Rahim-Yar-Khan-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.35 bn (88.3%) of external capital** and **$1.69 bn of external interest**. Capital plus saved interest totals **$3.04 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **43.071 km to 40.500 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **21 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **165 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **165 light-metro-3car trainsets / 495 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Rahim-Yar-Khan rail network on OpenStreetMap](rahim-yar-khan-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 21 / 3 |
| Route length | 51.0 km double track |
| Direct transfers / reachable line pairs | 100.0% / 100.0% |
| Residents within 800 m radial station catchments | 175,914 (2020 raster; 15.2% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 165 × 3-car `light-metro-3car` trainsets (148 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  7.7 km | 4 | 26 | NW Inner ↔ SE Mid |
| line-2 | 18.0 km | 7 | 59 | SW Mid ↔ NE Outer |
| line-3 | 25.3 km | 10 | 80 | NE Outer ↔ SW Outer |
| **Total** | **51.0 km** | **21 unique** | **165** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 23,702 train-km/day |
| Annual traction demand | 112.1 GWh |
| Station/depot PV / storage | 19.2 MW / 134.0 MWh |
| Aggregate charging power | 17.0 MW |
| Dedicated solar plant | 36.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 12.0 km / 96 kWh |
| Lowest traversal charging margin | line-1: 128 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $434 M |
| Stations | $118 M |
| Depots | $59 M |
| Rolling stock | $148 M |
| Dedicated solar plant | $29 M |
| Residual train control | $2.5 M |
| Charging microgrids | $3.7 M |
| EPC / project services | $54 M |
| **Total city programme** | **$849 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $179 M (21.1%) |
| Domestic / local capital | $669 M (78.9%) |
| Annual public construction commitment | $116 M / yr for 7 years |
| Annual post-grace debt service | $99 M / yr |
| External capital saved vs default turnkey sensitivity | $1.35 bn |
| Capital + lifetime external interest saved | $3.04 bn |
| Annual OPEX | $21 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 0 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 298 assets / 1,863 tasks | [`rahim-yar-khan-operations-manifest.json`](operations/rahim-yar-khan-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`rahim-yar-khan.toml`](rahim-yar-khan.toml) | Expanded simulator scenario |
| [`rahim-yar-khan.corridor.geojson`](rahim-yar-khan.corridor.geojson) | GIS corridor and stations |
| [`rahim-yar-khan.design-quality.yaml`](rahim-yar-khan.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh rahim-yar-khan
```
