# Sumbawanga — Urban Rail Network

**Country:** TZ · **Population:** 250,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Sumbawanga-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$727 M (89.0%) of external capital** and **$912 M of external interest**. Capital plus saved interest totals **$1.64 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **6 lines**, including **3 additional residential lines**. **67.2%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **15.698 km to 19.365 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **20 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **70 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **70 tram-2car trainsets / 140 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Sumbawanga rail network on OpenStreetMap](sumbawanga-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 20 / 4 |
| Route length | 19.4 km double track |
| Direct transfers / reachable line pairs | 26.7% / 46.7% |
| Residents within 800 m radial station catchments | 101,508 (2020 raster; 57.2% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 70 × 2-car `tram-2car` trainsets (58 peak revenue) |
| Peak network throughput | 57,600 passengers/hour |
| Practical service capacity | 535,680 passenger-trips/day |
| Annual paid-trip planning range | 97.8–156.4 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  3.8 km | 4 | 13 | E Inner ↔ NW Mid |
| line-2 |  4.1 km | 4 | 14 | S Outer ↔ NE Inner |
| line-3 |  2.0 km | 3 | 10 | NW Inner ↔ SW Mid |
| line-4 |  3.0 km | 3 | 11 | S Mid ↔ SE Outer |
| line-5 |  3.1 km | 3 | 11 | W Inner ↔ NW Outer |
| line-6 |  3.4 km | 3 | 11 | N Mid ↔ NE Mid |
| **Total** | **19.4 km** | **20 unique** | **70** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,790 one-way journeys / 9,005 train-km/day |
| Annual traction demand | 28.4 GWh |
| Station/depot PV / storage | 34.2 MW / 247.0 MWh |
| Aggregate charging power | 10.0 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 2.4 km / 13 kWh |
| Lowest traversal charging margin | line-6: 44 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $202 M |
| Stations | $102 M |
| Depots | $77 M |
| Rolling stock | $39 M |
| Residual train control | $968 k |
| Charging microgrids | $2.1 M |
| EPC / project services | $30 M |
| **Total city programme** | **$454 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $90 M (19.7%) |
| Domestic / local capital | $364 M (80.3%) |
| Annual public construction commitment | $42 M / yr for 7 years |
| Annual post-grace debt service | $34 M / yr |
| External capital saved vs default turnkey sensitivity | $727 M |
| Capital + lifetime external interest saved | $1.64 bn |
| Annual OPEX | $12 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 3 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 194 assets / 983 tasks | [`sumbawanga-operations-manifest.json`](operations/sumbawanga-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`sumbawanga.toml`](sumbawanga.toml) | Expanded simulator scenario |
| [`sumbawanga.corridor.geojson`](sumbawanga.corridor.geojson) | GIS corridor and stations |
| [`sumbawanga.design-quality.yaml`](sumbawanga.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh sumbawanga
```
