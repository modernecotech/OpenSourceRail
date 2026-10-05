# East-London-Za — Urban Rail Network

**Country:** ZA · **Population:** 800,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only East-London-Za-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.54 bn (88.0%) of external capital** and **$1.90 bn of external interest**. Capital plus saved interest totals **$3.44 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **51.306 km to 43.775 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **22 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **185 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **185 light-metro-3car trainsets / 555 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![East-London-Za rail network on OpenStreetMap](east-london-za-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 22 / 3 |
| Route length | 59.2 km double track |
| Direct transfers / reachable line pairs | 100.0% / 100.0% |
| Residents within 800 m radial station catchments | 89,863 (2020 raster; 23.4% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 185 × 3-car `light-metro-3car` trainsets (167 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 17.5 km | 7 | 53 | E Outer ↔ S Outer |
| line-2 | 20.7 km | 7 | 65 | SE Mid ↔ NW Outer |
| line-3 | 21.0 km | 8 | 67 | W Outer ↔ E Outer |
| **Total** | **59.2 km** | **22 unique** | **185** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 27,515 train-km/day |
| Annual traction demand | 130.2 GWh |
| Station/depot PV / storage | 20.7 MW / 129.5 MWh |
| Aggregate charging power | 11.0 MW |
| Dedicated solar plant | 73.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 5.4 km / 39 kWh |
| Lowest traversal charging margin | line-1: 62 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $505 M |
| Stations | $116 M |
| Depots | $62 M |
| Rolling stock | $166 M |
| Dedicated solar plant | $59 M |
| Residual train control | $3.0 M |
| Charging microgrids | $2.4 M |
| EPC / project services | $60 M |
| **Total city programme** | **$974 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $211 M (21.6%) |
| Domestic / local capital | $763 M (78.4%) |
| Annual public construction commitment | $104 M / yr for 5 years |
| Annual post-grace debt service | $78 M / yr |
| External capital saved vs default turnkey sensitivity | $1.54 bn |
| Capital + lifetime external interest saved | $3.44 bn |
| Annual OPEX | $30 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 8 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 330 assets / 2,080 tasks | [`east-london-za-operations-manifest.json`](operations/east-london-za-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`east-london-za.toml`](east-london-za.toml) | Expanded simulator scenario |
| [`east-london-za.corridor.geojson`](east-london-za.corridor.geojson) | GIS corridor and stations |
| [`east-london-za.design-quality.yaml`](east-london-za.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh east-london-za
```
