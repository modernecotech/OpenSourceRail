# Port-Harcourt — Urban Rail Network

**Country:** NG · **Population:** 3,000,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Port-Harcourt-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$10.68 bn (88.4%) of external capital** and **$13.39 bn of external interest**. Capital plus saved interest totals **$24.08 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **30 lines**, including **25 additional residential lines**. **64.6%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **158.976 km to 264.303 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **254 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**30 line-local depots** provide **747 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **747 metro-4car trainsets / 2988 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Port-Harcourt rail network on OpenStreetMap](port-harcourt-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 30 / 254 / 58 |
| Route length | 348.0 km double track |
| Direct transfers / reachable line pairs | 14.7% / 100.0% |
| Residents within 800 m radial station catchments | 1,157,061 (2020 raster; 50.1% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 747 × 4-car `metro-4car` trainsets (660 peak revenue) |
| Peak network throughput | 576,000 passengers/hour |
| Practical service capacity | 5,267,520 passenger-trips/day |
| Annual paid-trip planning range | 961.3–1538.1 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 35.5 km | 21 | 71 | E Mid ↔ NW Outer |
| line-2 | 23.5 km | 16 | 54 | NE Mid ↔ SW Mid |
| line-3 | 25.6 km | 16 | 56 | S Mid ↔ N Outer |
| line-4 | 29.2 km | 24 | 72 | SE Mid ↔ N Outer |
| line-5 | 60.0 km | 40 | 35 | NW Mid ↔ NW Mid |
| line-6 |  6.3 km | 5 | 17 | SW Inner ↔ W Mid |
| line-7 |  8.5 km | 7 | 24 | SW Inner ↔ W Inner |
| line-8 |  4.9 km | 5 | 16 | SE Inner ↔ SE Mid |
| line-9 |  4.4 km | 5 | 16 | W Mid ↔ W Mid |
| line-10 |  5.2 km | 4 | 13 | SE Mid ↔ SE Outer |
| line-11 |  7.7 km | 6 | 20 | W Mid ↔ W Inner |
| line-12 |  3.5 km | 3 | 11 | SW Mid ↔ SW Mid |
| line-13 |  3.8 km | 4 | 14 | N Inner ↔ NW Inner |
| line-14 |  4.1 km | 4 | 14 | N Inner ↔ NW Inner |
| line-15 |  7.1 km | 5 | 16 | E Mid ↔ E Outer |
| line-16 |  4.4 km | 3 | 12 | SW Mid ↔ S Mid |
| line-17 | 11.1 km | 9 | 30 | NW Inner ↔ W Mid |
| line-18 |  7.3 km | 5 | 16 | NW Mid ↔ NW Outer |
| line-19 | 10.0 km | 7 | 23 | SE Mid ↔ SE Outer |
| line-20 |  3.6 km | 3 | 11 | NW Mid ↔ NW Mid |
| line-21 |  7.6 km | 4 | 16 | SE Mid ↔ S Inner |
| line-22 |  4.5 km | 3 | 12 | N Mid ↔ N Mid |
| line-23 |  7.9 km | 9 | 27 | S Mid ↔ SE Mid |
| line-24 |  5.5 km | 5 | 17 | NE Inner ↔ E Inner |
| line-25 | 13.4 km | 8 | 27 | W Mid ↔ SW Mid |
| line-26 |  3.9 km | 5 | 16 | E Inner ↔ SE Mid |
| line-27 | 13.4 km | 8 | 28 | SE Mid ↔ SE Outer |
| line-28 | 13.2 km | 8 | 26 | N Outer ↔ NE Mid |
| line-29 |  9.1 km | 8 | 23 | W Mid ↔ NW Outer |
| line-30 |  3.7 km | 4 | 14 | SW Inner ↔ SW Mid |
| **Total** | **348.0 km** | **254 unique** | **747** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 13,718 one-way journeys / 147,879 train-km/day |
| Annual traction demand | 932.7 GWh |
| Station/depot PV / storage | 204.6 MW / 1,473.0 MWh |
| Aggregate charging power | 318.0 MW |
| Dedicated solar plant | 376.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 11.3 km / 113 kWh |
| Lowest traversal charging margin | line-15: 69 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $3.23 bn |
| Stations | $1.35 bn |
| Depots | $492 M |
| Rolling stock | $837 M |
| Dedicated solar plant | $302 M |
| Residual train control | $17 M |
| Charging microgrids | $64 M |
| EPC / project services | $420 M |
| **Total city programme** | **$6.72 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.40 bn (20.9%) |
| Domestic / local capital | $5.31 bn (79.1%) |
| Annual public construction commitment | $789 M / yr for 7 years |
| Annual post-grace debt service | $665 M / yr |
| External capital saved vs default turnkey sensitivity | $10.68 bn |
| Capital + lifetime external interest saved | $24.08 bn |
| Annual OPEX | $164 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 34 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 2,147 assets / 11,148 tasks | [`port-harcourt-operations-manifest.json`](operations/port-harcourt-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`port-harcourt.toml`](port-harcourt.toml) | Expanded simulator scenario |
| [`port-harcourt.corridor.geojson`](port-harcourt.corridor.geojson) | GIS corridor and stations |
| [`port-harcourt.design-quality.yaml`](port-harcourt.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh port-harcourt
```
