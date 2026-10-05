# Mwanza — Urban Rail Network

**Country:** TZ · **Population:** 1,100,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Mwanza-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$5.10 bn (88.5%) of external capital** and **$6.40 bn of external interest**. Capital plus saved interest totals **$11.50 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **153.851 km to 158.820 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **101 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **314 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **314 metro-4car trainsets / 1256 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Mwanza rail network on OpenStreetMap](mwanza-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 101 / 8 |
| Route length | 177.3 km double track |
| Direct transfers / reachable line pairs | 100.0% / 100.0% |
| Residents within 800 m radial station catchments | 412,070 (2020 raster; 39.1% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 314 × 4-car `metro-4car` trainsets (283 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 18.0 km | 11 | 40 | S Mid ↔ N Mid |
| line-2 | 35.1 km | 21 | 75 | NW Mid ↔ E Mid |
| line-3 | 37.2 km | 24 | 83 | SW Mid ↔ NW Mid |
| line-4 | 19.0 km | 13 | 45 | NE Outer ↔ W Inner |
| line-5 | 26.0 km | 14 | 52 | NW Inner ↔ SE Outer |
| line-6 | 42.1 km | 18 | 19 | N Mid ↔ N Mid |
| **Total** | **177.3 km** | **101 unique** | **314** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 72,665 train-km/day |
| Annual traction demand | 458.3 GWh |
| Station/depot PV / storage | 57.3 MW / 376.5 MWh |
| Aggregate charging power | 145.5 MW |
| Dedicated solar plant | 234.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-5: 12.2 km / 122 kWh |
| Lowest traversal charging margin | line-6: 371 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.61 bn |
| Stations | $683 M |
| Depots | $131 M |
| Rolling stock | $352 M |
| Dedicated solar plant | $188 M |
| Residual train control | $8.9 M |
| Charging microgrids | $30 M |
| EPC / project services | $197 M |
| **Total city programme** | **$3.20 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $665 M (20.8%) |
| Domestic / local capital | $2.54 bn (79.2%) |
| Annual public construction commitment | $295 M / yr for 7 years |
| Annual post-grace debt service | $242 M / yr |
| External capital saved vs default turnkey sensitivity | $5.10 bn |
| Capital + lifetime external interest saved | $11.50 bn |
| Annual OPEX | $74 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 10 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 874 assets / 4,656 tasks | [`mwanza-operations-manifest.json`](operations/mwanza-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`mwanza.toml`](mwanza.toml) | Expanded simulator scenario |
| [`mwanza.corridor.geojson`](mwanza.corridor.geojson) | GIS corridor and stations |
| [`mwanza.design-quality.yaml`](mwanza.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh mwanza
```
