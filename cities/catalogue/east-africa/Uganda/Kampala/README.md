# Kampala — Urban Rail Network

**Country:** UG · **Population:** 1,875,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kampala-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$11.38 bn (88.2%) of external capital** and **$14.27 bn of external interest**. Capital plus saved interest totals **$25.66 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **41 lines**, including **35 additional residential lines**. **76.5%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **174.304 km to 265.529 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **271 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**41 line-local depots** provide **833 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **833 metro-4car trainsets / 3332 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Kampala rail network on OpenStreetMap](kampala-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 41 / 271 / 79 |
| Route length | 375.4 km double track |
| Direct transfers / reachable line pairs | 11.6% / 100.0% |
| Residents within 800 m radial station catchments | 2,207,509 (2020 raster; 58.8% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 833 × 4-car `metro-4car` trainsets (729 peak revenue) |
| Peak network throughput | 787,200 passengers/hour |
| Practical service capacity | 7,231,680 passenger-trips/day |
| Annual paid-trip planning range | 1319.8–2111.7 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 32.5 km | 24 | 78 | E Outer ↔ W Outer |
| line-2 | 22.3 km | 14 | 49 | S Mid ↔ N Outer |
| line-3 | 25.3 km | 19 | 60 | S Mid ↔ N Outer |
| line-4 | 27.0 km | 15 | 53 | NW Outer ↔ E Mid |
| line-5 | 22.5 km | 15 | 52 | NE Mid ↔ S Outer |
| line-6 | 57.9 km | 41 | 35 | W Mid ↔ W Mid |
| line-7 |  5.4 km | 5 | 17 | NW Mid ↔ N Mid |
| line-8 |  4.6 km | 4 | 14 | S Mid ↔ SE Mid |
| line-9 |  4.6 km | 4 | 14 | SW Mid ↔ SW Mid |
| line-10 |  4.3 km | 3 | 12 | NW Mid ↔ W Inner |
| line-11 |  4.8 km | 4 | 14 | E Mid ↔ SE Inner |
| line-12 |  4.2 km | 3 | 12 | NE Mid ↔ E Outer |
| line-13 |  3.9 km | 3 | 12 | NW Mid ↔ NW Outer |
| line-14 |  4.0 km | 3 | 12 | N Mid ↔ NE Inner |
| line-15 |  5.3 km | 5 | 16 | S Mid ↔ S Outer |
| line-16 |  4.1 km | 3 | 11 | S Outer ↔ SE Mid |
| line-17 |  4.8 km | 4 | 14 | S Mid ↔ S Mid |
| line-18 |  5.3 km | 3 | 13 | E Mid ↔ NE Mid |
| line-19 |  5.4 km | 4 | 13 | NE Mid ↔ NE Outer |
| line-20 |  6.5 km | 4 | 14 | N Mid ↔ NW Outer |
| line-21 |  7.6 km | 5 | 17 | SW Mid ↔ SW Outer |
| line-22 |  3.9 km | 3 | 12 | SE Mid ↔ SE Outer |
| line-23 |  3.8 km | 3 | 11 | E Mid ↔ E Outer |
| line-24 |  5.4 km | 4 | 13 | W Mid ↔ W Outer |
| line-25 |  8.5 km | 6 | 20 | NW Mid ↔ N Mid |
| line-26 |  5.4 km | 4 | 13 | N Outer ↔ NE Mid |
| line-27 |  5.2 km | 4 | 13 | NE Mid ↔ E Outer |
| line-28 |  8.1 km | 5 | 19 | SE Mid ↔ SE Inner |
| line-29 |  6.2 km | 4 | 15 | NW Inner ↔ SW Inner |
| line-30 |  7.7 km | 5 | 17 | W Mid ↔ SW Outer |
| line-31 |  5.9 km | 4 | 14 | S Outer ↔ S Outer |
| line-32 | 14.1 km | 10 | 31 | SW Mid ↔ S Mid |
| line-33 |  3.8 km | 3 | 12 | W Mid ↔ SW Mid |
| line-34 |  4.0 km | 4 | 14 | NE Mid ↔ NE Mid |
| line-35 |  3.8 km | 3 | 11 | NE Mid ↔ NE Outer |
| line-36 |  4.7 km | 3 | 12 | S Outer ↔ S Outer |
| line-37 |  5.7 km | 5 | 17 | NE Inner ↔ N Mid |
| line-38 |  4.0 km | 4 | 14 | SW Mid ↔ SW Mid |
| line-39 |  5.1 km | 4 | 15 | E Mid ↔ SE Inner |
| line-40 |  3.9 km | 5 | 16 | N Mid ↔ N Mid |
| line-41 |  4.0 km | 3 | 12 | S Mid ↔ SE Mid |
| **Total** | **375.4 km** | **271 unique** | **833** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 18,832 one-way journeys / 161,092 train-km/day |
| Annual traction demand | 1,016.0 GWh |
| Station/depot PV / storage | 264.4 MW / 1,937.0 MWh |
| Aggregate charging power | 357.0 MW |
| Dedicated solar plant | 362.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-32: 8.8 km / 88 kWh |
| Lowest traversal charging margin | line-20: 76 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $3.17 bn |
| Stations | $1.60 bn |
| Depots | $633 M |
| Rolling stock | $933 M |
| Dedicated solar plant | $290 M |
| Residual train control | $19 M |
| Charging microgrids | $73 M |
| EPC / project services | $450 M |
| **Total city programme** | **$7.17 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.52 bn (21.2%) |
| Domestic / local capital | $5.65 bn (78.8%) |
| Annual public construction commitment | $863 M / yr for 7 years |
| Annual post-grace debt service | $730 M / yr |
| External capital saved vs default turnkey sensitivity | $11.38 bn |
| Capital + lifetime external interest saved | $25.66 bn |
| Annual OPEX | $173 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 21 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 2,362 assets / 12,247 tasks | [`kampala-operations-manifest.json`](operations/kampala-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kampala.toml`](kampala.toml) | Expanded simulator scenario |
| [`kampala.corridor.geojson`](kampala.corridor.geojson) | GIS corridor and stations |
| [`kampala.design-quality.yaml`](kampala.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kampala
```
