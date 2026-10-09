# Port-Sudan — Urban Rail Network

**Country:** SD · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Port-Sudan-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.51 bn (88.6%) of external capital** and **$1.96 bn of external interest**. Capital plus saved interest totals **$3.47 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **7 lines**, including **4 additional residential lines**. **43.4%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **33.307 km to 46.322 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **33 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**7 line-local depots** provide **175 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **175 light-metro-3car trainsets / 525 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Port-Sudan rail network on OpenStreetMap](port-sudan-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 7 / 33 / 5 |
| Route length | 48.8 km double track |
| Direct transfers / reachable line pairs | 23.8% / 52.4% |
| Residents within 800 m radial station catchments | 150,268 (2020 raster; 31.3% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 175 × 3-car `light-metro-3car` trainsets (154 peak revenue) |
| Peak network throughput | 100,800 passengers/hour |
| Practical service capacity | 937,440 passenger-trips/day |
| Annual paid-trip planning range | 171.1–273.7 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 11.2 km | 7 | 38 | N Outer ↔ S Outer |
| line-2 |  7.5 km | 5 | 27 | NW Mid ↔ S Mid |
| line-3 |  6.5 km | 5 | 23 | NE Mid ↔ S Mid |
| line-4 |  5.0 km | 4 | 18 | SW Inner ↔ SW Mid |
| line-5 |  6.1 km | 4 | 23 | NW Inner ↔ NW Outer |
| line-6 |  6.3 km | 4 | 23 | SE Mid ↔ S Outer |
| line-7 |  6.2 km | 4 | 23 | NW Mid ↔ N Outer |
| **Total** | **48.8 km** | **33 unique** | **175** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,255 one-way journeys / 22,683 train-km/day |
| Annual traction demand | 107.3 GWh |
| Station/depot PV / storage | 42.5 MW / 292.5 MWh |
| Aggregate charging power | 16.0 MW |
| Dedicated solar plant | 7.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 4.9 km / 39 kWh |
| Lowest traversal charging margin | line-6: 18 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $471 M |
| Stations | $141 M |
| Depots | $107 M |
| Rolling stock | $158 M |
| Dedicated solar plant | $6.0 M |
| Residual train control | $2.4 M |
| Charging microgrids | $3.4 M |
| EPC / project services | $62 M |
| **Total city programme** | **$950 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $195 M (20.6%) |
| Domestic / local capital | $754 M (79.4%) |
| Annual public construction commitment | $114 M / yr for 10 years |
| Annual post-grace debt service | $104 M / yr |
| External capital saved vs default turnkey sensitivity | $1.51 bn |
| Capital + lifetime external interest saved | $3.47 bn |
| Annual OPEX | $24 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 11 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 381 assets / 2,171 tasks | [`port-sudan-operations-manifest.json`](operations/port-sudan-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`port-sudan.toml`](port-sudan.toml) | Expanded simulator scenario |
| [`port-sudan.corridor.geojson`](port-sudan.corridor.geojson) | GIS corridor and stations |
| [`port-sudan.design-quality.yaml`](port-sudan.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh port-sudan
```
