# Mbuji-Mayi — Urban Rail Network

**Country:** CD · **Population:** 2,500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Mbuji-Mayi-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.26 bn (88.5%) of external capital** and **$5.50 bn of external interest**. Capital plus saved interest totals **$9.76 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **12 lines**, including **8 additional residential lines**. **78.7%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **102.734 km to 127.253 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **98 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**12 line-local depots** provide **280 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **280 metro-4car trainsets / 1120 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Mbuji-Mayi rail network on OpenStreetMap](mbuji-mayi-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 12 / 98 / 20 |
| Route length | 143.8 km double track |
| Direct transfers / reachable line pairs | 31.8% / 100.0% |
| Residents within 800 m radial station catchments | 2,800,673 (2020 raster; 62.6% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 280 × 4-car `metro-4car` trainsets (246 peak revenue) |
| Peak network throughput | 230,400 passengers/hour |
| Practical service capacity | 2,053,440 passenger-trips/day |
| Annual paid-trip planning range | 374.8–599.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 25.1 km | 14 | 49 | W Outer ↔ E Outer |
| line-2 | 15.6 km | 9 | 34 | SW Mid ↔ SE Mid |
| line-3 | 29.3 km | 19 | 60 | NE Outer ↔ SW Mid |
| line-4 | 35.3 km | 23 | 20 | W Mid ↔ W Mid |
| line-5 |  5.2 km | 5 | 17 | SE Inner ↔ W Inner |
| line-6 |  2.7 km | 3 | 11 | W Inner ↔ W Mid |
| line-7 |  3.3 km | 3 | 11 | NW Inner ↔ N Inner |
| line-8 |  2.2 km | 2 | 8 | SE Inner ↔ SE Mid |
| line-9 |  4.7 km | 3 | 12 | E Inner ↔ NE Mid |
| line-10 | 12.5 km | 9 | 31 | NW Mid ↔ E Inner |
| line-11 |  4.2 km | 4 | 14 | E Inner ↔ NE Inner |
| line-12 |  3.7 km | 4 | 13 | W Mid ↔ W Mid |
| **Total** | **143.8 km** | **98 unique** | **280** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 5,348 one-way journeys / 58,672 train-km/day |
| Annual traction demand | 370.1 GWh |
| Station/depot PV / storage | 82.8 MW / 594.0 MWh |
| Aggregate charging power | 132.0 MW |
| Dedicated solar plant | 147.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 14.7 km / 146 kWh |
| Lowest traversal charging margin | line-8: 123 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.34 bn |
| Stations | $506 M |
| Depots | $193 M |
| Rolling stock | $314 M |
| Dedicated solar plant | $118 M |
| Residual train control | $7.2 M |
| Charging microgrids | $27 M |
| EPC / project services | $167 M |
| **Total city programme** | **$2.67 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $553 M (20.7%) |
| Domestic / local capital | $2.12 bn (79.3%) |
| Annual public construction commitment | $288 M / yr for 10 years |
| Annual post-grace debt service | $260 M / yr |
| External capital saved vs default turnkey sensitivity | $4.26 bn |
| Capital + lifetime external interest saved | $9.76 bn |
| Annual OPEX | $61 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 21 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 825 assets / 4,248 tasks | [`mbuji-mayi-operations-manifest.json`](operations/mbuji-mayi-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`mbuji-mayi.toml`](mbuji-mayi.toml) | Expanded simulator scenario |
| [`mbuji-mayi.corridor.geojson`](mbuji-mayi.corridor.geojson) | GIS corridor and stations |
| [`mbuji-mayi.design-quality.yaml`](mbuji-mayi.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh mbuji-mayi
```
