# Conakry — Urban Rail Network

**Country:** GN · **Population:** 2,010,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Conakry-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.83 bn (88.9%) of external capital** and **$2.36 bn of external interest**. Capital plus saved interest totals **$4.18 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **60.568 km to 61.102 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **28 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **87 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **87 metro-4car trainsets / 348 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Conakry rail network on OpenStreetMap](conakry-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 28 / 4 |
| Route length | 81.7 km double track |
| Direct transfers / reachable line pairs | 100.0% / 100.0% |
| Residents within 800 m radial station catchments | 189,980 (2020 raster; 17.9% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 87 × 4-car `metro-4car` trainsets (78 peak revenue) |
| Peak network throughput | 57,600 passengers/hour |
| Practical service capacity | 446,400 passenger-trips/day |
| Annual paid-trip planning range | 81.5–130.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 26.3 km | 8 | 40 | NE Outer ↔ SW Mid |
| line-2 | 18.0 km | 7 | 31 | SW Inner ↔ NE Outer |
| line-3 | 37.4 km | 13 | 16 | N Inner ↔ N Inner |
| **Total** | **81.7 km** | **28 unique** | **87** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,162 one-way journeys / 29,279 train-km/day |
| Annual traction demand | 184.7 GWh |
| Station/depot PV / storage | 22.2 MW / 156.0 MWh |
| Aggregate charging power | 40.5 MW |
| Dedicated solar plant | 95.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 7.8 km / 78 kWh |
| Lowest traversal charging margin | line-3: 177 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $707 M |
| Stations | $126 M |
| Depots | $52 M |
| Rolling stock | $97 M |
| Dedicated solar plant | $77 M |
| Residual train control | $4.1 M |
| Charging microgrids | $8.6 M |
| EPC / project services | $70 M |
| **Total city programme** | **$1.14 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $229 M (20.0%) |
| Domestic / local capital | $913 M (80.0%) |
| Annual public construction commitment | $102 M / yr for 10 years |
| Annual post-grace debt service | $91 M / yr |
| External capital saved vs default turnkey sensitivity | $1.83 bn |
| Capital + lifetime external interest saved | $4.18 bn |
| Annual OPEX | $25 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 13 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 245 assets / 1,286 tasks | [`conakry-operations-manifest.json`](operations/conakry-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`conakry.toml`](conakry.toml) | Expanded simulator scenario |
| [`conakry.corridor.geojson`](conakry.corridor.geojson) | GIS corridor and stations |
| [`conakry.design-quality.yaml`](conakry.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh conakry
```
