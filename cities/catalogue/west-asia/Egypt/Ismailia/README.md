# Ismailia — Urban Rail Network

**Country:** EG · **Population:** 700,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Ismailia-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.26 bn (88.4%) of external capital** and **$2.78 bn of external interest**. Capital plus saved interest totals **$5.04 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **9 lines**, including **6 additional residential lines**. **81.4%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **43.606 km to 57.483 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **54 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**9 line-local depots** provide **270 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **270 light-metro-3car trainsets / 810 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Ismailia rail network on OpenStreetMap](ismailia-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 54 / 12 |
| Route length | 74.4 km double track |
| Direct transfers / reachable line pairs | 36.1% / 100.0% |
| Residents within 800 m radial station catchments | 470,713 (2020 raster; 69.9% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 270 × 3-car `light-metro-3car` trainsets (239 peak revenue) |
| Peak network throughput | 129,600 passengers/hour |
| Practical service capacity | 1,205,280 passenger-trips/day |
| Annual paid-trip planning range | 220.0–351.9 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 11.6 km | 8 | 37 | E Mid ↔ NW Mid |
| line-2 | 19.3 km | 15 | 69 | NE Outer ↔ S Mid |
| line-3 | 11.7 km | 9 | 40 | SE Mid ↔ N Inner |
| line-4 |  2.2 km | 3 | 13 | SE Inner ↔ NW Inner |
| line-5 |  8.8 km | 5 | 30 | S Mid ↔ W Outer |
| line-6 |  2.9 km | 2 | 11 | E Inner ↔ NE Mid |
| line-7 |  2.3 km | 3 | 13 | N Inner ↔ NE Inner |
| line-8 |  3.2 km | 2 | 12 | S Mid ↔ SE Mid |
| line-9 | 12.5 km | 7 | 45 | NW Mid ↔ SW Outer |
| **Total** | **74.4 km** | **54 unique** | **270** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 4,185 one-way journeys / 34,588 train-km/day |
| Annual traction demand | 163.6 GWh |
| Station/depot PV / storage | 55.8 MW / 378.0 MWh |
| Aggregate charging power | 22.5 MW |
| Dedicated solar plant | 21.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-9: 9.7 km / 78 kWh |
| Lowest traversal charging margin | line-5: 20 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $647 M |
| Stations | $270 M |
| Depots | $144 M |
| Rolling stock | $243 M |
| Dedicated solar plant | $17 M |
| Residual train control | $3.7 M |
| Charging microgrids | $4.7 M |
| EPC / project services | $92 M |
| **Total city programme** | **$1.42 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $297 M (20.9%) |
| Domestic / local capital | $1.12 bn (79.1%) |
| Annual public construction commitment | $153 M / yr for 5 years |
| Annual post-grace debt service | $114 M / yr |
| External capital saved vs default turnkey sensitivity | $2.26 bn |
| Capital + lifetime external interest saved | $5.04 bn |
| Annual OPEX | $41 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 6 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 591 assets / 3,380 tasks | [`ismailia-operations-manifest.json`](operations/ismailia-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`ismailia.toml`](ismailia.toml) | Expanded simulator scenario |
| [`ismailia.corridor.geojson`](ismailia.corridor.geojson) | GIS corridor and stations |
| [`ismailia.design-quality.yaml`](ismailia.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh ismailia
```
