# Tunis — Urban Rail Network

**Country:** TN · **Population:** 2,900,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Tunis-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$11.44 bn (88.5%) of external capital** and **$14.07 bn of external interest**. Capital plus saved interest totals **$25.51 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **35 lines**, including **30 additional residential lines**. **79.4%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **190.377 km to 317.305 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **260 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**35 line-local depots** provide **793 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **793 metro-4car trainsets / 3172 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Tunis rail network on OpenStreetMap](tunis-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 35 / 260 / 70 |
| Route length | 400.9 km double track |
| Direct transfers / reachable line pairs | 12.3% / 100.0% |
| Residents within 800 m radial station catchments | 1,699,852 (2020 raster; 62.0% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 793 × 4-car `metro-4car` trainsets (700 peak revenue) |
| Peak network throughput | 672,000 passengers/hour |
| Practical service capacity | 6,160,320 passenger-trips/day |
| Annual paid-trip planning range | 1124.3–1798.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 34.9 km | 19 | 68 | SE Mid ↔ W Outer |
| line-2 | 24.5 km | 19 | 62 | S Mid ↔ N Mid |
| line-3 | 39.9 km | 22 | 75 | W Outer ↔ NE Outer |
| line-4 | 28.1 km | 19 | 62 | SE Mid ↔ NW Outer |
| line-5 | 74.3 km | 45 | 40 | W Mid ↔ W Mid |
| line-6 |  4.3 km | 3 | 12 | NW Mid ↔ W Mid |
| line-7 |  8.5 km | 6 | 21 | N Inner ↔ NW Inner |
| line-8 |  6.1 km | 4 | 15 | SE Mid ↔ S Mid |
| line-9 |  6.1 km | 5 | 17 | SE Mid ↔ SE Outer |
| line-10 |  4.2 km | 4 | 14 | SW Mid ↔ SW Mid |
| line-11 |  4.4 km | 3 | 11 | S Mid ↔ S Mid |
| line-12 |  4.6 km | 4 | 14 | E Mid ↔ NE Mid |
| line-13 | 12.1 km | 6 | 24 | NW Mid ↔ NE Mid |
| line-14 |  5.6 km | 5 | 17 | N Mid ↔ N Mid |
| line-15 |  9.4 km | 6 | 21 | NW Inner ↔ W Mid |
| line-16 |  4.5 km | 3 | 12 | SE Inner ↔ S Mid |
| line-17 |  5.8 km | 4 | 14 | NE Mid ↔ NE Outer |
| line-18 |  5.1 km | 4 | 14 | SE Mid ↔ E Mid |
| line-19 |  4.3 km | 3 | 12 | NE Mid ↔ N Inner |
| line-20 |  6.2 km | 4 | 14 | SE Mid ↔ SE Mid |
| line-21 |  8.1 km | 6 | 20 | N Mid ↔ N Outer |
| line-22 |  7.2 km | 5 | 18 | W Inner ↔ SW Mid |
| line-23 |  4.9 km | 3 | 11 | NE Mid ↔ NE Outer |
| line-24 |  7.7 km | 5 | 18 | NW Inner ↔ N Inner |
| line-25 |  6.8 km | 5 | 18 | NE Mid ↔ NE Outer |
| line-26 |  7.3 km | 5 | 16 | W Outer ↔ NW Outer |
| line-27 | 11.1 km | 7 | 24 | SE Mid ↔ S Outer |
| line-28 |  6.0 km | 4 | 13 | SW Mid ↔ SW Mid |
| line-29 |  6.1 km | 4 | 14 | W Mid ↔ W Mid |
| line-30 |  7.5 km | 5 | 17 | NW Inner ↔ N Mid |
| line-31 |  9.7 km | 6 | 23 | SE Inner ↔ SW Inner |
| line-32 |  4.2 km | 3 | 12 | NW Inner ↔ NW Inner |
| line-33 |  6.6 km | 4 | 14 | SE Mid ↔ SE Mid |
| line-34 |  9.5 km | 6 | 21 | SE Mid ↔ SE Outer |
| line-35 |  5.4 km | 4 | 15 | N Inner ↔ NW Inner |
| **Total** | **400.9 km** | **260 unique** | **793** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 16,042 one-way journeys / 169,117 train-km/day |
| Annual traction demand | 1,066.7 GWh |
| Station/depot PV / storage | 231.4 MW / 1,682.0 MWh |
| Aggregate charging power | 334.5 MW |
| Dedicated solar plant | 344.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 12.4 km / 119 kWh |
| Lowest traversal charging margin | line-27: 55 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $3.50 bn |
| Stations | $1.42 bn |
| Depots | $557 M |
| Rolling stock | $888 M |
| Dedicated solar plant | $276 M |
| Residual train control | $20 M |
| Charging microgrids | $68 M |
| EPC / project services | $452 M |
| **Total city programme** | **$7.18 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.49 bn (20.7%) |
| Domestic / local capital | $5.69 bn (79.3%) |
| Annual public construction commitment | $705 M / yr for 5 years |
| Annual post-grace debt service | $516 M / yr |
| External capital saved vs default turnkey sensitivity | $11.44 bn |
| Capital + lifetime external interest saved | $25.51 bn |
| Annual OPEX | $201 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 35 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 2,244 assets / 11,681 tasks | [`tunis-operations-manifest.json`](operations/tunis-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`tunis.toml`](tunis.toml) | Expanded simulator scenario |
| [`tunis.corridor.geojson`](tunis.corridor.geojson) | GIS corridor and stations |
| [`tunis.design-quality.yaml`](tunis.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh tunis
```
