# Buraidah — Urban Rail Network

**Country:** SA · **Population:** 700,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Buraidah-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.17 bn (88.2%) of external capital** and **$3.90 bn of external interest**. Capital plus saved interest totals **$7.07 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **14 lines**, including **11 additional residential lines**. **66.0%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **56.903 km to 80.312 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **76 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**14 line-local depots** provide **403 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **403 light-metro-3car trainsets / 1209 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Buraidah rail network on OpenStreetMap](buraidah-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 14 / 76 / 15 |
| Route length | 115.3 km double track |
| Direct transfers / reachable line pairs | 17.6% / 100.0% |
| Residents within 800 m radial station catchments | 149,544 (2020 raster; 49.0% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 403 × 3-car `light-metro-3car` trainsets (359 peak revenue) |
| Peak network throughput | 201,600 passengers/hour |
| Practical service capacity | 1,874,880 passenger-trips/day |
| Annual paid-trip planning range | 342.2–547.5 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 27.0 km | 17 | 86 | SE Outer ↔ NW Outer |
| line-2 | 15.2 km | 9 | 49 | NW Mid ↔ E Mid |
| line-3 | 15.5 km | 10 | 53 | S Mid ↔ N Outer |
| line-4 |  4.6 km | 3 | 17 | NW Mid ↔ NW Mid |
| line-5 |  3.0 km | 3 | 14 | SE Inner ↔ S Mid |
| line-6 |  5.1 km | 4 | 19 | SE Mid ↔ E Outer |
| line-7 |  3.2 km | 3 | 14 | S Inner ↔ W Inner |
| line-8 | 10.3 km | 6 | 35 | NW Inner ↔ SW Mid |
| line-9 |  4.5 km | 3 | 17 | SE Outer ↔ S Mid |
| line-10 |  8.3 km | 5 | 29 | NW Mid ↔ NW Outer |
| line-11 |  3.4 km | 3 | 14 | E Mid ↔ E Mid |
| line-12 |  9.6 km | 5 | 32 | S Mid ↔ E Inner |
| line-13 |  3.3 km | 3 | 14 | S Mid ↔ SW Mid |
| line-14 |  2.4 km | 2 | 10 | NW Inner ↔ W Mid |
| **Total** | **115.3 km** | **76 unique** | **403** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 6,510 one-way journeys / 53,637 train-km/day |
| Annual traction demand | 253.7 GWh |
| Station/depot PV / storage | 86.8 MW / 588.0 MWh |
| Aggregate charging power | 35.0 MW |
| Dedicated solar plant | 33.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-10: 6.4 km / 52 kWh |
| Lowest traversal charging margin | line-6: 24 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $894 M |
| Stations | $354 M |
| Depots | $219 M |
| Rolling stock | $363 M |
| Dedicated solar plant | $27 M |
| Residual train control | $5.8 M |
| Charging microgrids | $7.2 M |
| EPC / project services | $129 M |
| **Total city programme** | **$2.00 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $424 M (21.2%) |
| Domestic / local capital | $1.57 bn (78.8%) |
| Annual public construction commitment | $139 M / yr for 5 years |
| Annual post-grace debt service | $96 M / yr |
| External capital saved vs default turnkey sensitivity | $3.17 bn |
| Capital + lifetime external interest saved | $7.07 bn |
| Annual OPEX | $132 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 18 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 867 assets / 4,990 tasks | [`buraidah-operations-manifest.json`](operations/buraidah-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`buraidah.toml`](buraidah.toml) | Expanded simulator scenario |
| [`buraidah.corridor.geojson`](buraidah.corridor.geojson) | GIS corridor and stations |
| [`buraidah.design-quality.yaml`](buraidah.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh buraidah
```
