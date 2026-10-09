# Fez — Urban Rail Network

**Country:** MA · **Population:** 1,300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Fez-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.26 bn (88.8%) of external capital** and **$4.00 bn of external interest**. Capital plus saved interest totals **$7.26 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **9 lines**, including **5 additional residential lines**. **80.5%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **106.603 km to 101.672 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **74 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**9 line-local depots** provide **200 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **200 metro-4car trainsets / 800 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Fez rail network on OpenStreetMap](fez-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 74 / 19 |
| Route length | 109.1 km double track |
| Direct transfers / reachable line pairs | 36.1% / 100.0% |
| Residents within 800 m radial station catchments | 936,372 (2020 raster; 67.0% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 200 × 4-car `metro-4car` trainsets (174 peak revenue) |
| Peak network throughput | 172,800 passengers/hour |
| Practical service capacity | 1,517,760 passenger-trips/day |
| Annual paid-trip planning range | 277.0–443.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 18.9 km | 13 | 45 | NE Mid ↔ SW Outer |
| line-2 | 13.6 km | 10 | 35 | W Outer ↔ SE Mid |
| line-3 | 17.8 km | 12 | 40 | E Outer ↔ W Mid |
| line-4 | 40.9 km | 24 | 23 | W Mid ↔ W Mid |
| line-5 |  3.4 km | 4 | 13 | NE Mid ↔ NE Inner |
| line-6 |  3.8 km | 3 | 12 | S Inner ↔ SW Mid |
| line-7 |  4.5 km | 3 | 12 | SW Mid ↔ W Inner |
| line-8 |  3.4 km | 3 | 11 | SE Mid ↔ E Inner |
| line-9 |  2.9 km | 2 | 9 | NW Inner ↔ N Inner |
| **Total** | **109.1 km** | **74 unique** | **200** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,952 one-way journeys / 41,241 train-km/day |
| Annual traction demand | 260.1 GWh |
| Station/depot PV / storage | 63.9 MW / 454.5 MWh |
| Aggregate charging power | 108.0 MW |
| Dedicated solar plant | 75.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 5.6 km / 54 kWh |
| Lowest traversal charging margin | line-9: 117 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.05 bn |
| Stations | $403 M |
| Depots | $143 M |
| Rolling stock | $224 M |
| Dedicated solar plant | $60 M |
| Residual train control | $5.5 M |
| Charging microgrids | $22 M |
| EPC / project services | $129 M |
| **Total city programme** | **$2.04 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $410 M (20.1%) |
| Domestic / local capital | $1.63 bn (79.9%) |
| Annual public construction commitment | $142 M / yr for 5 years |
| Annual post-grace debt service | $98 M / yr |
| External capital saved vs default turnkey sensitivity | $3.26 bn |
| Capital + lifetime external interest saved | $7.26 bn |
| Annual OPEX | $58 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 21 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 615 assets / 3,125 tasks | [`fez-operations-manifest.json`](operations/fez-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`fez.toml`](fez.toml) | Expanded simulator scenario |
| [`fez.corridor.geojson`](fez.corridor.geojson) | GIS corridor and stations |
| [`fez.design-quality.yaml`](fez.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh fez
```
