# Taiz — Urban Rail Network

**Country:** YE · **Population:** 615,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Taiz-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.23 bn (88.4%) of external capital** and **$2.88 bn of external interest**. Capital plus saved interest totals **$5.12 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **11 lines**, including **8 additional residential lines**. **75.3%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **34.229 km to 56.687 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **56 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**11 line-local depots** provide **269 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **269 light-metro-3car trainsets / 807 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Taiz rail network on OpenStreetMap](taiz-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 11 / 56 / 11 |
| Route length | 72.5 km double track |
| Direct transfers / reachable line pairs | 29.1% / 100.0% |
| Residents within 800 m radial station catchments | 740,006 (2020 raster; 60.6% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 269 × 3-car `light-metro-3car` trainsets (238 peak revenue) |
| Peak network throughput | 158,400 passengers/hour |
| Practical service capacity | 1,473,120 passenger-trips/day |
| Annual paid-trip planning range | 268.8–430.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 16.5 km | 12 | 58 | E Outer ↔ W Mid |
| line-2 |  6.1 km | 4 | 23 | NW Mid ↔ NE Mid |
| line-3 | 15.3 km | 13 | 54 | SW Outer ↔ N Mid |
| line-4 |  2.7 km | 2 | 11 | N Mid ↔ N Inner |
| line-5 |  2.5 km | 2 | 10 | SW Mid ↔ S Mid |
| line-6 |  3.1 km | 3 | 14 | NW Inner ↔ NW Mid |
| line-7 |  5.6 km | 4 | 19 | NW Inner ↔ SW Mid |
| line-8 |  4.4 km | 5 | 20 | N Inner ↔ E Inner |
| line-9 |  6.8 km | 4 | 25 | SW Outer ↔ S Outer |
| line-10 |  5.2 km | 4 | 18 | NW Inner ↔ NW Mid |
| line-11 |  4.5 km | 3 | 17 | NE Mid ↔ NE Outer |
| **Total** | **72.5 km** | **56 unique** | **269** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 5,115 one-way journeys / 33,706 train-km/day |
| Annual traction demand | 159.4 GWh |
| Station/depot PV / storage | 67.0 MW / 460.0 MWh |
| Aggregate charging power | 25.5 MW |
| Dedicated solar plant | 4.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-9: 6.8 km / 49 kWh |
| Lowest traversal charging margin | line-4: 28 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $604 M |
| Stations | $288 M |
| Depots | $166 M |
| Rolling stock | $242 M |
| Dedicated solar plant | $3.2 M |
| Residual train control | $3.6 M |
| Charging microgrids | $5.3 M |
| EPC / project services | $92 M |
| **Total city programme** | **$1.40 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $293 M (20.9%) |
| Domestic / local capital | $1.11 bn (79.1%) |
| Annual public construction commitment | $195 M / yr for 10 years |
| Annual post-grace debt service | $179 M / yr |
| External capital saved vs default turnkey sensitivity | $2.23 bn |
| Capital + lifetime external interest saved | $5.12 bn |
| Annual OPEX | $34 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 8 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 608 assets / 3,417 tasks | [`taiz-operations-manifest.json`](operations/taiz-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`taiz.toml`](taiz.toml) | Expanded simulator scenario |
| [`taiz.corridor.geojson`](taiz.corridor.geojson) | GIS corridor and stations |
| [`taiz.design-quality.yaml`](taiz.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh taiz
```
