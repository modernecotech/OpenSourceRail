# Damascus — Urban Rail Network

**Country:** SY · **Population:** 2,503,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Damascus-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$7.89 bn (88.6%) of external capital** and **$10.19 bn of external interest**. Capital plus saved interest totals **$18.08 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **25 lines**, including **19 additional residential lines**. **79.8%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **165.310 km to 218.596 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **187 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**25 line-local depots** provide **557 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **557 metro-4car trainsets / 2228 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Damascus rail network on OpenStreetMap](damascus-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 25 / 187 / 48 |
| Route length | 271.3 km double track |
| Direct transfers / reachable line pairs | 17.7% / 100.0% |
| Residents within 800 m radial station catchments | 2,721,769 (2020 raster; 63.8% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 557 × 4-car `metro-4car` trainsets (490 peak revenue) |
| Peak network throughput | 480,000 passengers/hour |
| Practical service capacity | 4,374,720 passenger-trips/day |
| Annual paid-trip planning range | 798.4–1277.4 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 25.2 km | 17 | 58 | NE Outer ↔ W Mid |
| line-2 | 24.1 km | 14 | 50 | SE Mid ↔ NW Outer |
| line-3 | 22.4 km | 18 | 57 | S Mid ↔ N Outer |
| line-4 | 18.9 km | 11 | 40 | NW Outer ↔ E Inner |
| line-5 | 22.5 km | 13 | 47 | NE Mid ↔ SW Outer |
| line-6 | 56.0 km | 35 | 30 | NW Mid ↔ W Mid |
| line-7 |  3.4 km | 3 | 11 | SW Inner ↔ S Inner |
| line-8 |  5.3 km | 4 | 15 | SE Inner ↔ E Inner |
| line-9 |  4.2 km | 3 | 12 | S Mid ↔ S Mid |
| line-10 |  3.4 km | 3 | 11 | E Inner ↔ SE Mid |
| line-11 |  4.8 km | 4 | 14 | E Inner ↔ NE Mid |
| line-12 |  5.8 km | 4 | 13 | SE Mid ↔ SE Outer |
| line-13 |  3.5 km | 3 | 10 | SW Mid ↔ SW Outer |
| line-14 |  7.0 km | 5 | 18 | W Mid ↔ SW Inner |
| line-15 |  4.5 km | 4 | 14 | NE Mid ↔ N Inner |
| line-16 |  4.8 km | 3 | 11 | E Mid ↔ E Mid |
| line-17 |  8.1 km | 7 | 21 | S Mid ↔ S Mid |
| line-18 |  3.8 km | 4 | 14 | SE Mid ↔ SE Mid |
| line-19 |  5.5 km | 4 | 15 | NE Mid ↔ NE Outer |
| line-20 |  5.6 km | 4 | 15 | NW Outer ↔ NW Mid |
| line-21 |  7.4 km | 5 | 16 | SW Mid ↔ SW Outer |
| line-22 |  5.6 km | 5 | 17 | SE Inner ↔ S Mid |
| line-23 |  4.7 km | 5 | 16 | N Inner ↔ NE Inner |
| line-24 |  6.3 km | 4 | 15 | NW Mid ↔ W Inner |
| line-25 |  8.4 km | 5 | 17 | SE Mid ↔ SE Outer |
| **Total** | **271.3 km** | **187 unique** | **557** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 11,392 one-way journeys / 113,138 train-km/day |
| Annual traction demand | 713.6 GWh |
| Station/depot PV / storage | 167.6 MW / 1,213.0 MWh |
| Aggregate charging power | 250.5 MW |
| Dedicated solar plant | 182.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-21: 7.4 km / 80 kWh |
| Lowest traversal charging margin | line-21: 59 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.37 bn |
| Stations | $1.03 bn |
| Depots | $398 M |
| Rolling stock | $624 M |
| Dedicated solar plant | $146 M |
| Residual train control | $14 M |
| Charging microgrids | $51 M |
| EPC / project services | $314 M |
| **Total city programme** | **$4.95 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.02 bn (20.6%) |
| Domestic / local capital | $3.93 bn (79.4%) |
| Annual public construction commitment | $753 M / yr for 10 years |
| Annual post-grace debt service | $694 M / yr |
| External capital saved vs default turnkey sensitivity | $7.89 bn |
| Capital + lifetime external interest saved | $18.08 bn |
| Annual OPEX | $111 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 28 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,605 assets / 8,306 tasks | [`damascus-operations-manifest.json`](operations/damascus-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`damascus.toml`](damascus.toml) | Expanded simulator scenario |
| [`damascus.corridor.geojson`](damascus.corridor.geojson) | GIS corridor and stations |
| [`damascus.design-quality.yaml`](damascus.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh damascus
```
