# Benin-City — Urban Rail Network

**Country:** NG · **Population:** 1,800,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Benin-City-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$6.99 bn (88.4%) of external capital** and **$8.76 bn of external interest**. Capital plus saved interest totals **$15.75 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **28 lines**, including **23 additional residential lines**. **70.2%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **103.509 km to 189.991 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **159 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**28 line-local depots** provide **505 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **505 metro-4car trainsets / 2020 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Benin-City rail network on OpenStreetMap](benin-city-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 28 / 159 / 40 |
| Route length | 212.6 km double track |
| Direct transfers / reachable line pairs | 14.3% / 100.0% |
| Residents within 800 m radial station catchments | 856,102 (2020 raster; 55.9% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 505 × 4-car `metro-4car` trainsets (437 peak revenue) |
| Peak network throughput | 537,600 passengers/hour |
| Practical service capacity | 4,910,400 passenger-trips/day |
| Annual paid-trip planning range | 896.1–1433.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 13.6 km | 10 | 35 | N Mid ↔ SW Mid |
| line-2 | 22.1 km | 16 | 51 | S Outer ↔ N Mid |
| line-3 | 23.3 km | 15 | 49 | NW Inner ↔ SE Outer |
| line-4 | 22.6 km | 15 | 49 | NE Outer ↔ SW Mid |
| line-5 | 24.0 km | 20 | 17 | NW Inner ↔ NW Inner |
| line-6 |  2.8 km | 2 | 9 | N Inner ↔ NW Mid |
| line-7 |  3.6 km | 3 | 11 | NW Inner ↔ W Mid |
| line-8 |  4.4 km | 3 | 12 | SW Inner ↔ SW Mid |
| line-9 |  4.0 km | 4 | 14 | W Inner ↔ N Inner |
| line-10 |  5.8 km | 5 | 17 | NW Inner ↔ NW Mid |
| line-11 |  4.6 km | 4 | 14 | S Mid ↔ SE Inner |
| line-12 |  2.7 km | 2 | 9 | SW Mid ↔ SW Inner |
| line-13 |  6.0 km | 4 | 14 | SW Mid ↔ S Mid |
| line-14 |  2.8 km | 2 | 9 | NE Inner ↔ E Inner |
| line-15 |  5.2 km | 4 | 14 | SW Mid ↔ SW Outer |
| line-16 | 12.6 km | 9 | 31 | N Inner ↔ E Mid |
| line-17 |  3.6 km | 3 | 11 | NW Inner ↔ W Mid |
| line-18 |  7.7 km | 6 | 20 | NW Inner ↔ NW Mid |
| line-19 |  3.2 km | 3 | 11 | SW Mid ↔ W Mid |
| line-20 |  4.6 km | 3 | 11 | SW Mid ↔ SW Mid |
| line-21 |  2.3 km | 2 | 9 | SE Mid ↔ SE Mid |
| line-22 |  2.6 km | 3 | 11 | N Inner ↔ N Inner |
| line-23 |  2.3 km | 2 | 8 | SW Mid ↔ SW Mid |
| line-24 |  5.8 km | 4 | 15 | NE Inner ↔ E Inner |
| line-25 |  8.8 km | 6 | 19 | SW Mid ↔ SW Outer |
| line-26 |  4.2 km | 3 | 12 | SE Inner ↔ SE Inner |
| line-27 |  2.5 km | 2 | 9 | S Mid ↔ S Mid |
| line-28 |  5.3 km | 4 | 14 | NE Mid ↔ NE Mid |
| **Total** | **212.6 km** | **159 unique** | **505** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 12,788 one-way journeys / 93,286 train-km/day |
| Annual traction demand | 588.4 GWh |
| Station/depot PV / storage | 173.6 MW / 1,288.0 MWh |
| Aggregate charging power | 210.0 MW |
| Dedicated solar plant | 186.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-4: 9.0 km / 90 kWh |
| Lowest traversal charging margin | line-20: 97 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.08 bn |
| Stations | $844 M |
| Depots | $422 M |
| Rolling stock | $566 M |
| Dedicated solar plant | $149 M |
| Residual train control | $11 M |
| Charging microgrids | $42 M |
| EPC / project services | $277 M |
| **Total city programme** | **$4.39 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $915 M (20.8%) |
| Domestic / local capital | $3.48 bn (79.2%) |
| Annual public construction commitment | $516 M / yr for 7 years |
| Annual post-grace debt service | $435 M / yr |
| External capital saved vs default turnkey sensitivity | $6.99 bn |
| Capital + lifetime external interest saved | $15.75 bn |
| Annual OPEX | $109 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 18 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,412 assets / 7,321 tasks | [`benin-city-operations-manifest.json`](operations/benin-city-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`benin-city.toml`](benin-city.toml) | Expanded simulator scenario |
| [`benin-city.corridor.geojson`](benin-city.corridor.geojson) | GIS corridor and stations |
| [`benin-city.design-quality.yaml`](benin-city.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh benin-city
```
