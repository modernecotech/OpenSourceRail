# Nakuru — Urban Rail Network

**Country:** KE · **Population:** 700,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Nakuru-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.81 bn (88.4%) of external capital** and **$3.52 bn of external interest**. Capital plus saved interest totals **$6.34 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **13 lines**, including **10 additional residential lines**. **75.4%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **45.561 km to 76.052 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 1 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **67 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**13 line-local depots** provide **343 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **343 light-metro-3car trainsets / 1029 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Nakuru rail network on OpenStreetMap](nakuru-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 13 / 67 / 14 |
| Route length | 95.5 km double track |
| Direct transfers / reachable line pairs | 25.6% / 100.0% |
| Residents within 800 m radial station catchments | 386,399 (2020 raster; 60.7% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 343 × 3-car `light-metro-3car` trainsets (304 peak revenue) |
| Peak network throughput | 187,200 passengers/hour |
| Practical service capacity | 1,740,960 passenger-trips/day |
| Annual paid-trip planning range | 317.7–508.4 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 11.5 km | 7 | 38 | NW Inner ↔ E Mid |
| line-2 | 20.4 km | 13 | 72 | NE Inner ↔ SW Outer |
| line-3 | 16.2 km | 11 | 51 | SE Mid ↔ W Mid |
| line-4 |  2.4 km | 3 | 13 | SW Inner ↔ W Inner |
| line-5 |  6.9 km | 5 | 24 | N Inner ↔ W Mid |
| line-6 |  2.7 km | 2 | 11 | E Inner ↔ NE Mid |
| line-7 |  6.1 km | 4 | 24 | NE Inner ↔ NE Mid |
| line-8 |  5.8 km | 4 | 21 | E Mid ↔ E Outer |
| line-9 |  3.8 km | 3 | 14 | NW Inner ↔ W Inner |
| line-10 |  5.0 km | 4 | 18 | NW Inner ↔ SE Inner |
| line-11 |  3.6 km | 3 | 14 | N Inner ↔ NE Inner |
| line-12 |  7.5 km | 5 | 29 | NE Inner ↔ NE Outer |
| line-13 |  3.6 km | 3 | 14 | NW Inner ↔ NW Mid |
| **Total** | **95.5 km** | **67 unique** | **343** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 6,045 one-way journeys / 44,400 train-km/day |
| Annual traction demand | 210.0 GWh |
| Station/depot PV / storage | 77.9 MW / 563.0 MWh |
| Aggregate charging power | 56.0 MW |
| Dedicated solar plant | 12.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 8.4 km / 70 kWh |
| Lowest traversal charging margin | line-6: 73 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $818 M |
| Stations | $300 M |
| Depots | $199 M |
| Rolling stock | $309 M |
| Dedicated solar plant | $9.8 M |
| Residual train control | $4.8 M |
| Charging microgrids | $12 M |
| EPC / project services | $115 M |
| **Total city programme** | **$1.77 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $369 M (20.9%) |
| Domestic / local capital | $1.40 bn (79.1%) |
| Annual public construction commitment | $185 M / yr for 7 years |
| Annual post-grace debt service | $154 M / yr |
| External capital saved vs default turnkey sensitivity | $2.81 bn |
| Capital + lifetime external interest saved | $6.34 bn |
| Annual OPEX | $50 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 11 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 746 assets / 4,262 tasks | [`nakuru-operations-manifest.json`](operations/nakuru-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`nakuru.toml`](nakuru.toml) | Expanded simulator scenario |
| [`nakuru.corridor.geojson`](nakuru.corridor.geojson) | GIS corridor and stations |
| [`nakuru.design-quality.yaml`](nakuru.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh nakuru
```
