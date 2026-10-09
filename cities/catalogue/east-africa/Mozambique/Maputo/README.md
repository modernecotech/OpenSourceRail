# Maputo — Urban Rail Network

**Country:** MZ · **Population:** 1,530,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Maputo-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$7.76 bn (88.2%) of external capital** and **$10.03 bn of external interest**. Capital plus saved interest totals **$17.79 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **23 lines**, including **17 additional residential lines**. **79.5%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **114.490 km to 147.248 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **190 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**23 line-local depots** provide **554 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **554 metro-4car trainsets / 2216 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Maputo rail network on OpenStreetMap](maputo-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 23 / 190 / 54 |
| Route length | 259.3 km double track |
| Direct transfers / reachable line pairs | 20.9% / 100.0% |
| Residents within 800 m radial station catchments | 1,289,500 (2020 raster; 62.3% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 554 × 4-car `metro-4car` trainsets (489 peak revenue) |
| Peak network throughput | 441,600 passengers/hour |
| Practical service capacity | 4,017,600 passenger-trips/day |
| Annual paid-trip planning range | 733.2–1173.1 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 21.9 km | 21 | 65 | S Mid ↔ NE Outer |
| line-2 | 19.7 km | 15 | 50 | SE Outer ↔ N Mid |
| line-3 | 18.5 km | 10 | 38 | NE Outer ↔ SW Mid |
| line-4 | 27.9 km | 16 | 56 | SE Outer ↔ NW Outer |
| line-5 | 18.1 km | 13 | 45 | E Outer ↔ W Mid |
| line-6 | 54.1 km | 40 | 34 | NW Inner ↔ NW Inner |
| line-7 |  6.7 km | 5 | 17 | W Mid ↔ SW Outer |
| line-8 |  6.0 km | 6 | 19 | SW Inner ↔ NW Inner |
| line-9 |  8.8 km | 5 | 18 | S Mid ↔ SW Outer |
| line-10 |  5.0 km | 4 | 14 | NW Inner ↔ N Mid |
| line-11 |  8.4 km | 6 | 20 | SW Mid ↔ SW Outer |
| line-12 |  4.0 km | 3 | 12 | SE Outer ↔ E Outer |
| line-13 |  5.3 km | 4 | 15 | SE Inner ↔ S Mid |
| line-14 |  4.7 km | 3 | 11 | W Mid ↔ W Outer |
| line-15 |  5.7 km | 3 | 13 | N Outer ↔ N Mid |
| line-16 |  4.7 km | 3 | 12 | NE Mid ↔ E Mid |
| line-17 |  5.0 km | 3 | 12 | N Mid ↔ NE Mid |
| line-18 |  8.3 km | 5 | 19 | SW Mid ↔ SW Outer |
| line-19 |  3.7 km | 3 | 12 | NE Outer ↔ NE Outer |
| line-20 |  4.5 km | 7 | 20 | N Mid ↔ N Outer |
| line-21 |  4.8 km | 4 | 14 | N Mid ↔ N Mid |
| line-22 |  6.4 km | 4 | 15 | NW Mid ↔ NW Mid |
| line-23 |  6.8 km | 7 | 23 | NE Inner ↔ SW Inner |
| **Total** | **259.3 km** | **190 unique** | **554** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 10,462 one-way journeys / 107,992 train-km/day |
| Annual traction demand | 681.1 GWh |
| Station/depot PV / storage | 162.7 MW / 1,158.5 MWh |
| Aggregate charging power | 273.0 MW |
| Dedicated solar plant | 260.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-4: 6.6 km / 66 kWh |
| Lowest traversal charging margin | line-14: 95 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.03 bn |
| Stations | $1.28 bn |
| Depots | $372 M |
| Rolling stock | $620 M |
| Dedicated solar plant | $208 M |
| Residual train control | $13 M |
| Charging microgrids | $57 M |
| EPC / project services | $306 M |
| **Total city programme** | **$4.89 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.04 bn (21.3%) |
| Domestic / local capital | $3.85 bn (78.7%) |
| Annual public construction commitment | $540 M / yr for 10 years |
| Annual post-grace debt service | $489 M / yr |
| External capital saved vs default turnkey sensitivity | $7.76 bn |
| Capital + lifetime external interest saved | $17.79 bn |
| Annual OPEX | $115 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 26 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,625 assets / 8,387 tasks | [`maputo-operations-manifest.json`](operations/maputo-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`maputo.toml`](maputo.toml) | Expanded simulator scenario |
| [`maputo.corridor.geojson`](maputo.corridor.geojson) | GIS corridor and stations |
| [`maputo.design-quality.yaml`](maputo.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh maputo
```
