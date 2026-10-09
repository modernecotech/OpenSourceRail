# Mbale — Urban Rail Network

**Country:** UG · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Mbale-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.42 bn (89.4%) of external capital** and **$1.78 bn of external interest**. Capital plus saved interest totals **$3.19 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **9 lines**, including **6 additional residential lines**. **51.3%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **32.666 km to 34.264 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **34 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**9 line-local depots** provide **124 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **124 tram-2car trainsets / 248 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Mbale rail network on OpenStreetMap](mbale-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 34 / 9 |
| Route length | 41.9 km double track |
| Direct transfers / reachable line pairs | 30.6% / 100.0% |
| Residents within 800 m radial station catchments | 141,065 (2020 raster; 39.6% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 124 × 2-car `tram-2car` trainsets (105 peak revenue) |
| Peak network throughput | 86,400 passengers/hour |
| Practical service capacity | 803,520 passenger-trips/day |
| Annual paid-trip planning range | 146.6–234.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  7.4 km | 6 | 20 | S Outer ↔ NW Mid |
| line-2 | 10.3 km | 7 | 26 | NE Outer ↔ S Mid |
| line-3 |  3.6 km | 4 | 13 | SE Inner ↔ W Mid |
| line-4 |  2.8 km | 2 | 9 | NE Inner ↔ NW Inner |
| line-5 |  5.2 km | 4 | 15 | S Mid ↔ W Mid |
| line-6 |  3.9 km | 3 | 12 | S Inner ↔ SE Mid |
| line-7 |  3.8 km | 3 | 11 | NE Mid ↔ NE Outer |
| line-8 |  3.0 km | 3 | 10 | NW Mid ↔ N Outer |
| line-9 |  2.0 km | 2 | 8 | SE Inner ↔ E Mid |
| **Total** | **41.9 km** | **34 unique** | **124** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 4,185 one-way journeys / 19,479 train-km/day |
| Annual traction demand | 61.4 GWh |
| Station/depot PV / storage | 51.9 MW / 371.5 MWh |
| Aggregate charging power | 16.0 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-7: 3.8 km / 19 kWh |
| Lowest traversal charging margin | line-7: 28 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $461 M |
| Stations | $167 M |
| Depots | $119 M |
| Rolling stock | $69 M |
| Residual train control | $2.1 M |
| Charging microgrids | $3.4 M |
| EPC / project services | $58 M |
| **Total city programme** | **$880 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $168 M (19.1%) |
| Domestic / local capital | $712 M (80.9%) |
| Annual public construction commitment | $108 M / yr for 7 years |
| Annual post-grace debt service | $91 M / yr |
| External capital saved vs default turnkey sensitivity | $1.42 bn |
| Capital + lifetime external interest saved | $3.19 bn |
| Annual OPEX | $21 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 5 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 330 assets / 1,712 tasks | [`mbale-operations-manifest.json`](operations/mbale-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`mbale.toml`](mbale.toml) | Expanded simulator scenario |
| [`mbale.corridor.geojson`](mbale.corridor.geojson) | GIS corridor and stations |
| [`mbale.design-quality.yaml`](mbale.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh mbale
```
