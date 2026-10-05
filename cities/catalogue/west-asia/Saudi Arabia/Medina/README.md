# Medina — Urban Rail Network

**Country:** SA · **Population:** 1,500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Medina-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.27 bn (89.0%) of external capital** and **$5.24 bn of external interest**. Capital plus saved interest totals **$9.51 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **148.772 km to 143.977 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **63 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **220 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **220 metro-4car trainsets / 880 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Medina rail network on OpenStreetMap](medina-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 63 / 15 |
| Route length | 172.2 km double track |
| Direct transfers / reachable line pairs | 73.3% / 100.0% |
| Residents within 800 m radial station catchments | 213,253 (2020 raster; 17.1% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 220 × 4-car `metro-4car` trainsets (197 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 32.7 km | 12 | 53 | NW Outer ↔ SE Outer |
| line-2 | 19.1 km | 9 | 37 | SW Mid ↔ NE Mid |
| line-3 | 18.6 km | 8 | 34 | NW Mid ↔ S Mid |
| line-4 | 23.8 km | 9 | 40 | NE Mid ↔ W Outer |
| line-5 | 19.4 km | 7 | 32 | N Mid ↔ E Outer |
| line-6 | 58.5 km | 18 | 24 | E Mid ↔ E Mid |
| **Total** | **172.2 km** | **63 unique** | **220** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 66,482 train-km/day |
| Annual traction demand | 419.3 GWh |
| Station/depot PV / storage | 46.2 MW / 321.0 MWh |
| Aggregate charging power | 90.0 MW |
| Dedicated solar plant | 167.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 12.0 km / 129 kWh |
| Lowest traversal charging margin | line-5: 162 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.60 bn |
| Stations | $371 M |
| Depots | $113 M |
| Rolling stock | $246 M |
| Dedicated solar plant | $134 M |
| Residual train control | $8.6 M |
| Charging microgrids | $19 M |
| EPC / project services | $165 M |
| **Total city programme** | **$2.66 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $526 M (19.8%) |
| Domestic / local capital | $2.14 bn (80.2%) |
| Annual public construction commitment | $186 M / yr for 5 years |
| Annual post-grace debt service | $128 M / yr |
| External capital saved vs default turnkey sensitivity | $4.27 bn |
| Capital + lifetime external interest saved | $9.51 bn |
| Annual OPEX | $117 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 14 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 576 assets / 3,115 tasks | [`medina-operations-manifest.json`](operations/medina-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`medina.toml`](medina.toml) | Expanded simulator scenario |
| [`medina.corridor.geojson`](medina.corridor.geojson) | GIS corridor and stations |
| [`medina.design-quality.yaml`](medina.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh medina
```
