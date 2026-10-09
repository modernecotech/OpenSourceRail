# Kigali — Urban Rail Network

**Country:** RW · **Population:** 1,208,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kigali-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$9.31 bn (88.3%) of external capital** and **$11.68 bn of external interest**. Capital plus saved interest totals **$20.99 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **30 lines**, including **24 additional residential lines**. **77.5%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **150.301 km to 218.916 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **226 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**30 line-local depots** provide **666 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **666 metro-4car trainsets / 2664 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Kigali rail network on OpenStreetMap](kigali-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 30 / 226 / 62 |
| Route length | 303.3 km double track |
| Direct transfers / reachable line pairs | 15.2% / 100.0% |
| Residents within 800 m radial station catchments | 1,036,361 (2020 raster; 62.5% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 666 × 4-car `metro-4car` trainsets (588 peak revenue) |
| Peak network throughput | 576,000 passengers/hour |
| Practical service capacity | 5,267,520 passenger-trips/day |
| Annual paid-trip planning range | 961.3–1538.1 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 27.6 km | 20 | 68 | W Outer ↔ SE Outer |
| line-2 | 15.8 km | 12 | 40 | NW Mid ↔ E Mid |
| line-3 | 14.3 km | 14 | 43 | S Mid ↔ N Mid |
| line-4 | 21.3 km | 14 | 48 | NE Outer ↔ SW Mid |
| line-5 | 21.5 km | 15 | 51 | NW Outer ↔ SE Mid |
| line-6 | 56.6 km | 37 | 31 | NW Mid ↔ W Mid |
| line-7 |  3.5 km | 4 | 13 | W Mid ↔ SW Mid |
| line-8 |  4.6 km | 3 | 12 | SW Mid ↔ S Inner |
| line-9 |  5.5 km | 3 | 13 | W Mid ↔ W Mid |
| line-10 |  4.8 km | 4 | 14 | SE Inner ↔ SE Inner |
| line-11 | 13.3 km | 9 | 30 | NE Inner ↔ NW Mid |
| line-12 |  5.0 km | 4 | 14 | S Mid ↔ SW Mid |
| line-13 |  4.3 km | 4 | 14 | W Mid ↔ W Outer |
| line-14 |  3.5 km | 3 | 11 | NW Mid ↔ W Inner |
| line-15 |  6.7 km | 4 | 15 | SE Mid ↔ E Outer |
| line-16 |  5.5 km | 6 | 19 | NE Mid ↔ N Inner |
| line-17 |  4.3 km | 4 | 14 | E Mid ↔ SE Inner |
| line-18 |  8.5 km | 6 | 19 | W Mid ↔ SW Mid |
| line-19 |  5.1 km | 4 | 13 | S Mid ↔ S Outer |
| line-20 |  5.0 km | 5 | 15 | NW Mid ↔ NW Mid |
| line-21 |  3.3 km | 3 | 10 | SE Outer ↔ SE Outer |
| line-22 |  5.8 km | 4 | 15 | E Mid ↔ E Mid |
| line-23 |  5.9 km | 4 | 13 | N Mid ↔ NW Mid |
| line-24 |  6.5 km | 6 | 18 | SE Outer ↔ E Outer |
| line-25 | 11.7 km | 10 | 32 | S Inner ↔ W Mid |
| line-26 |  5.8 km | 5 | 15 | NW Mid ↔ W Outer |
| line-27 |  6.6 km | 5 | 18 | E Mid ↔ NE Inner |
| line-28 |  8.9 km | 6 | 19 | SE Outer ↔ E Outer |
| line-29 |  7.1 km | 5 | 17 | SE Mid ↔ SE Mid |
| line-30 |  5.2 km | 3 | 12 | NE Mid ↔ NE Outer |
| **Total** | **303.3 km** | **226 unique** | **666** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 13,718 one-way journeys / 127,876 train-km/day |
| Annual traction demand | 806.5 GWh |
| Station/depot PV / storage | 200.4 MW / 1,452.0 MWh |
| Aggregate charging power | 297.0 MW |
| Dedicated solar plant | 298.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-18: 8.5 km / 84 kWh |
| Lowest traversal charging margin | line-18: 54 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.59 bn |
| Stations | $1.37 bn |
| Depots | $477 M |
| Rolling stock | $746 M |
| Dedicated solar plant | $239 M |
| Residual train control | $15 M |
| Charging microgrids | $61 M |
| EPC / project services | $368 M |
| **Total city programme** | **$5.86 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.24 bn (21.1%) |
| Domestic / local capital | $4.63 bn (78.9%) |
| Annual public construction commitment | $502 M / yr for 7 years |
| Annual post-grace debt service | $410 M / yr |
| External capital saved vs default turnkey sensitivity | $9.31 bn |
| Capital + lifetime external interest saved | $20.99 bn |
| Annual OPEX | $139 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 17 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,927 assets / 9,958 tasks | [`kigali-operations-manifest.json`](operations/kigali-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kigali.toml`](kigali.toml) | Expanded simulator scenario |
| [`kigali.corridor.geojson`](kigali.corridor.geojson) | GIS corridor and stations |
| [`kigali.design-quality.yaml`](kigali.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kigali
```
