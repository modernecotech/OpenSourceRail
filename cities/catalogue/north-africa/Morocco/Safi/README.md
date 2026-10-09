# Safi — Urban Rail Network

**Country:** MA · **Population:** 350,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Safi-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.22 bn (88.3%) of external capital** and **$1.50 bn of external interest**. Capital plus saved interest totals **$2.73 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **5 lines**, including **2 additional residential lines**. **84.0%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **34.491 km to 33.584 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **30 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**5 line-local depots** provide **150 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **150 light-metro-3car trainsets / 450 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Safi rail network on OpenStreetMap](safi-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 5 / 30 / 5 |
| Route length | 40.4 km double track |
| Direct transfers / reachable line pairs | 60.0% / 100.0% |
| Residents within 800 m radial station catchments | 262,293 (2020 raster; 71.5% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 150 × 3-car `light-metro-3car` trainsets (134 peak revenue) |
| Peak network throughput | 72,000 passengers/hour |
| Practical service capacity | 669,600 passenger-trips/day |
| Annual paid-trip planning range | 122.2–195.5 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 18.7 km | 11 | 65 | SE Outer ↔ NW Mid |
| line-2 |  8.3 km | 6 | 28 | N Mid ↔ SW Mid |
| line-3 |  7.6 km | 6 | 27 | N Inner ↔ SW Mid |
| line-4 |  2.6 km | 4 | 16 | N Mid ↔ NW Inner |
| line-5 |  3.2 km | 3 | 14 | SW Mid ↔ S Outer |
| **Total** | **40.4 km** | **30 unique** | **150** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,325 one-way journeys / 18,802 train-km/day |
| Annual traction demand | 88.9 GWh |
| Station/depot PV / storage | 31.0 MW / 210.0 MWh |
| Aggregate charging power | 12.5 MW |
| Dedicated solar plant | 15.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 8.8 km / 63 kWh |
| Lowest traversal charging margin | line-5: 24 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $350 M |
| Stations | $140 M |
| Depots | $79 M |
| Rolling stock | $135 M |
| Dedicated solar plant | $12 M |
| Residual train control | $2.0 M |
| Charging microgrids | $2.6 M |
| EPC / project services | $50 M |
| **Total city programme** | **$769 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $162 M (21.1%) |
| Domestic / local capital | $607 M (78.9%) |
| Annual public construction commitment | $53 M / yr for 5 years |
| Annual post-grace debt service | $37 M / yr |
| External capital saved vs default turnkey sensitivity | $1.22 bn |
| Capital + lifetime external interest saved | $2.73 bn |
| Annual OPEX | $25 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 4 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 329 assets / 1,878 tasks | [`safi-operations-manifest.json`](operations/safi-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`safi.toml`](safi.toml) | Expanded simulator scenario |
| [`safi.corridor.geojson`](safi.corridor.geojson) | GIS corridor and stations |
| [`safi.design-quality.yaml`](safi.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh safi
```
