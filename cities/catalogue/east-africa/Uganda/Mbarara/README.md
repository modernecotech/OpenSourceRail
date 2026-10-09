# Mbarara — Urban Rail Network

**Country:** UG · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Mbarara-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.95 bn (88.3%) of external capital** and **$3.70 bn of external interest**. Capital plus saved interest totals **$6.65 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **13 lines**, including **10 additional residential lines**. **66.1%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **48.265 km to 78.685 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **67 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**13 line-local depots** provide **349 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **349 light-metro-3car trainsets / 1047 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Mbarara rail network on OpenStreetMap](mbarara-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 13 / 67 / 15 |
| Route length | 95.7 km double track |
| Direct transfers / reachable line pairs | 20.5% / 100.0% |
| Residents within 800 m radial station catchments | 133,697 (2020 raster; 54.2% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 349 × 3-car `light-metro-3car` trainsets (308 peak revenue) |
| Peak network throughput | 187,200 passengers/hour |
| Practical service capacity | 1,740,960 passenger-trips/day |
| Annual paid-trip planning range | 317.7–508.4 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 10.2 km | 8 | 36 | E Inner ↔ SW Mid |
| line-2 | 13.0 km | 9 | 46 | NW Mid ↔ SE Inner |
| line-3 | 24.7 km | 15 | 86 | SW Outer ↔ NE Outer |
| line-4 |  6.9 km | 4 | 23 | SW Inner ↔ E Inner |
| line-5 |  2.2 km | 2 | 10 | SW Inner ↔ W Inner |
| line-6 |  3.3 km | 3 | 14 | S Inner ↔ SE Inner |
| line-7 |  3.4 km | 3 | 14 | NE Inner ↔ E Inner |
| line-8 |  3.7 km | 3 | 14 | NE Outer ↔ NE Outer |
| line-9 | 10.0 km | 6 | 35 | SE Inner ↔ SE Outer |
| line-10 |  3.8 km | 3 | 14 | SW Mid ↔ W Mid |
| line-11 |  3.1 km | 3 | 14 | E Inner ↔ E Mid |
| line-12 |  7.3 km | 5 | 27 | SW Mid ↔ SW Outer |
| line-13 |  4.3 km | 3 | 16 | NE Mid ↔ N Inner |
| **Total** | **95.7 km** | **67 unique** | **349** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 6,045 one-way journeys / 44,523 train-km/day |
| Annual traction demand | 210.6 GWh |
| Station/depot PV / storage | 77.0 MW / 540.0 MWh |
| Aggregate charging power | 26.5 MW |
| Dedicated solar plant | 49.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-9: 8.0 km / 60 kWh |
| Lowest traversal charging margin | line-13: 14 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $871 M |
| Stations | $302 M |
| Depots | $199 M |
| Rolling stock | $314 M |
| Dedicated solar plant | $40 M |
| Residual train control | $4.8 M |
| Charging microgrids | $5.5 M |
| EPC / project services | $119 M |
| **Total city programme** | **$1.86 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $391 M (21.1%) |
| Domestic / local capital | $1.46 bn (78.9%) |
| Annual public construction commitment | $223 M / yr for 7 years |
| Annual post-grace debt service | $189 M / yr |
| External capital saved vs default turnkey sensitivity | $2.95 bn |
| Capital + lifetime external interest saved | $6.65 bn |
| Annual OPEX | $47 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 8 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 750 assets / 4,305 tasks | [`mbarara-operations-manifest.json`](operations/mbarara-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`mbarara.toml`](mbarara.toml) | Expanded simulator scenario |
| [`mbarara.corridor.geojson`](mbarara.corridor.geojson) | GIS corridor and stations |
| [`mbarara.design-quality.yaml`](mbarara.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh mbarara
```
