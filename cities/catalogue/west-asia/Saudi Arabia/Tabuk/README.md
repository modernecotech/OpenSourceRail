# Tabuk — Urban Rail Network

**Country:** SA · **Population:** 650,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Tabuk-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.29 bn (88.4%) of external capital** and **$4.05 bn of external interest**. Capital plus saved interest totals **$7.34 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **12 lines**, including **9 additional residential lines**. **65.8%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **49.687 km to 84.223 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **76 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**12 line-local depots** provide **392 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **392 light-metro-3car trainsets / 1176 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Tabuk rail network on OpenStreetMap](tabuk-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 12 / 76 / 16 |
| Route length | 111.7 km double track |
| Direct transfers / reachable line pairs | 24.2% / 100.0% |
| Residents within 800 m radial station catchments | 278,966 (2020 raster; 50.2% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 392 × 3-car `light-metro-3car` trainsets (350 peak revenue) |
| Peak network throughput | 172,800 passengers/hour |
| Practical service capacity | 1,607,040 passenger-trips/day |
| Annual paid-trip planning range | 293.3–469.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 15.8 km | 10 | 53 | NE Mid ↔ W Outer |
| line-2 | 18.2 km | 11 | 60 | NW Outer ↔ S Mid |
| line-3 | 22.9 km | 15 | 81 | E Outer ↔ SW Outer |
| line-4 |  5.2 km | 4 | 18 | E Inner ↔ S Inner |
| line-5 |  5.0 km | 4 | 18 | NE Inner ↔ N Mid |
| line-6 |  9.6 km | 7 | 32 | SW Inner ↔ E Mid |
| line-7 |  2.1 km | 2 | 10 | NW Mid ↔ N Mid |
| line-8 |  4.2 km | 3 | 15 | E Mid ↔ E Mid |
| line-9 |  3.6 km | 3 | 14 | NW Mid ↔ W Inner |
| line-10 |  7.7 km | 5 | 29 | NW Outer ↔ W Outer |
| line-11 | 13.6 km | 9 | 48 | E Inner ↔ SE Outer |
| line-12 |  3.9 km | 3 | 14 | S Inner ↔ S Mid |
| **Total** | **111.7 km** | **76 unique** | **392** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 5,580 one-way journeys / 51,951 train-km/day |
| Annual traction demand | 245.8 GWh |
| Station/depot PV / storage | 76.8 MW / 508.0 MWh |
| Aggregate charging power | 34.0 MW |
| Dedicated solar plant | 40.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-10: 7.7 km / 62 kWh |
| Lowest traversal charging margin | line-10: 21 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $987 M |
| Stations | $354 M |
| Depots | $196 M |
| Rolling stock | $353 M |
| Dedicated solar plant | $33 M |
| Residual train control | $5.6 M |
| Charging microgrids | $7.0 M |
| EPC / project services | $133 M |
| **Total city programme** | **$2.07 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $432 M (20.9%) |
| Domestic / local capital | $1.64 bn (79.1%) |
| Annual public construction commitment | $144 M / yr for 5 years |
| Annual post-grace debt service | $100 M / yr |
| External capital saved vs default turnkey sensitivity | $3.29 bn |
| Capital + lifetime external interest saved | $7.34 bn |
| Annual OPEX | $129 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 21 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 848 assets / 4,887 tasks | [`tabuk-operations-manifest.json`](operations/tabuk-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`tabuk.toml`](tabuk.toml) | Expanded simulator scenario |
| [`tabuk.corridor.geojson`](tabuk.corridor.geojson) | GIS corridor and stations |
| [`tabuk.design-quality.yaml`](tabuk.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh tabuk
```
