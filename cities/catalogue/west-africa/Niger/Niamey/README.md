# Niamey — Urban Rail Network

**Country:** NE · **Population:** 1,407,635 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Niamey-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$9.08 bn (88.6%) of external capital** and **$11.73 bn of external interest**. Capital plus saved interest totals **$20.81 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **33 lines**, including **27 additional residential lines**. **78.4%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **145.326 km to 221.733 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **228 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**33 line-local depots** provide **665 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **665 metro-4car trainsets / 2660 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Niamey rail network on OpenStreetMap](niamey-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 33 / 228 / 60 |
| Route length | 286.6 km double track |
| Direct transfers / reachable line pairs | 12.3% / 100.0% |
| Residents within 800 m radial station catchments | 853,054 (2020 raster; 60.9% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 665 × 4-car `metro-4car` trainsets (582 peak revenue) |
| Peak network throughput | 633,600 passengers/hour |
| Practical service capacity | 5,803,200 passenger-trips/day |
| Annual paid-trip planning range | 1059.1–1694.5 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 22.7 km | 19 | 61 | SE Outer ↔ N Mid |
| line-2 | 15.8 km | 11 | 38 | NW Mid ↔ E Mid |
| line-3 | 14.2 km | 15 | 46 | NE Mid ↔ W Mid |
| line-4 | 19.3 km | 11 | 41 | W Mid ↔ E Outer |
| line-5 | 18.7 km | 13 | 45 | NW Outer ↔ S Inner |
| line-6 | 51.1 km | 42 | 35 | NW Mid ↔ NW Mid |
| line-7 |  3.9 km | 4 | 14 | E Mid ↔ NE Inner |
| line-8 |  5.0 km | 4 | 13 | SE Mid ↔ SE Outer |
| line-9 |  4.9 km | 4 | 13 | NW Outer ↔ W Outer |
| line-10 |  8.9 km | 6 | 21 | S Mid ↔ W Mid |
| line-11 |  5.0 km | 6 | 18 | N Mid ↔ NW Mid |
| line-12 |  5.6 km | 4 | 13 | SE Mid ↔ SE Outer |
| line-13 |  3.4 km | 3 | 11 | SW Mid ↔ S Mid |
| line-14 |  3.4 km | 3 | 11 | E Mid ↔ E Outer |
| line-15 |  4.1 km | 6 | 18 | NE Mid ↔ NE Mid |
| line-16 |  8.9 km | 5 | 18 | W Mid ↔ W Outer |
| line-17 |  2.8 km | 2 | 9 | E Inner ↔ E Inner |
| line-18 |  4.0 km | 5 | 16 | SE Outer ↔ S Mid |
| line-19 |  4.4 km | 4 | 14 | SE Inner ↔ SE Mid |
| line-20 |  6.5 km | 6 | 19 | NW Mid ↔ N Mid |
| line-21 |  3.7 km | 3 | 11 | SW Mid ↔ S Mid |
| line-22 |  3.9 km | 3 | 11 | SE Outer ↔ SE Outer |
| line-23 |  5.1 km | 3 | 13 | W Mid ↔ W Outer |
| line-24 |  3.5 km | 3 | 10 | NW Outer ↔ NW Outer |
| line-25 |  8.0 km | 5 | 18 | E Outer ↔ NE Mid |
| line-26 |  8.5 km | 6 | 20 | SE Inner ↔ S Mid |
| line-27 |  6.3 km | 5 | 16 | N Mid ↔ NE Mid |
| line-28 |  7.4 km | 5 | 16 | SW Mid ↔ S Outer |
| line-29 |  6.6 km | 5 | 18 | W Mid ↔ SW Inner |
| line-30 |  3.7 km | 4 | 14 | NW Mid ↔ N Mid |
| line-31 |  4.0 km | 3 | 11 | SW Mid ↔ SW Mid |
| line-32 | 10.2 km | 7 | 23 | SE Outer ↔ SE Outer |
| line-33 |  3.2 km | 3 | 10 | SE Outer ↔ S Outer |
| **Total** | **286.6 km** | **228 unique** | **665** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 15,112 one-way journeys / 121,407 train-km/day |
| Annual traction demand | 765.7 GWh |
| Station/depot PV / storage | 216.6 MW / 1,578.0 MWh |
| Aggregate charging power | 307.5 MW |
| Dedicated solar plant | 122.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-32: 10.2 km / 113 kWh |
| Lowest traversal charging margin | line-16: 38 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.54 bn |
| Stations | $1.36 bn |
| Depots | $511 M |
| Rolling stock | $745 M |
| Dedicated solar plant | $98 M |
| Residual train control | $14 M |
| Charging microgrids | $63 M |
| EPC / project services | $366 M |
| **Total city programme** | **$5.70 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.17 bn (20.6%) |
| Domestic / local capital | $4.52 bn (79.4%) |
| Annual public construction commitment | $469 M / yr for 10 years |
| Annual post-grace debt service | $424 M / yr |
| External capital saved vs default turnkey sensitivity | $9.08 bn |
| Capital + lifetime external interest saved | $20.81 bn |
| Annual OPEX | $132 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 18 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,947 assets / 9,996 tasks | [`niamey-operations-manifest.json`](operations/niamey-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`niamey.toml`](niamey.toml) | Expanded simulator scenario |
| [`niamey.corridor.geojson`](niamey.corridor.geojson) | GIS corridor and stations |
| [`niamey.design-quality.yaml`](niamey.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh niamey
```
