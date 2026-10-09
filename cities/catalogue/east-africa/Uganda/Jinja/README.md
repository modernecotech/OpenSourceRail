# Jinja — Urban Rail Network

**Country:** UG · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Jinja-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.50 bn (89.1%) of external capital** and **$3.13 bn of external interest**. Capital plus saved interest totals **$5.63 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **14 lines**, including **11 additional residential lines**. **72.5%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **32.128 km to 56.660 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **72 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**14 line-local depots** provide **244 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **244 tram-2car trainsets / 488 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Jinja rail network on OpenStreetMap](jinja-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 14 / 72 / 16 |
| Route length | 85.0 km double track |
| Direct transfers / reachable line pairs | 16.5% / 100.0% |
| Residents within 800 m radial station catchments | 185,123 (2020 raster; 54.4% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 244 × 2-car `tram-2car` trainsets (210 peak revenue) |
| Peak network throughput | 134,400 passengers/hour |
| Practical service capacity | 1,249,920 passenger-trips/day |
| Annual paid-trip planning range | 228.1–365.0 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 13.0 km | 9 | 31 | NE Outer ↔ S Inner |
| line-2 | 17.4 km | 17 | 51 | SE Mid ↔ NW Mid |
| line-3 | 12.8 km | 9 | 31 | SW Outer ↔ NE Inner |
| line-4 |  4.3 km | 3 | 12 | NE Outer ↔ NE Mid |
| line-5 |  6.1 km | 8 | 24 | W Inner ↔ W Mid |
| line-6 |  5.8 km | 4 | 14 | NE Inner ↔ N Outer |
| line-7 |  4.8 km | 4 | 13 | SW Outer ↔ W Outer |
| line-8 |  3.7 km | 3 | 11 | NE Mid ↔ E Mid |
| line-9 |  2.6 km | 2 | 9 | S Mid ↔ S Mid |
| line-10 |  4.1 km | 3 | 11 | NE Outer ↔ NE Outer |
| line-11 |  2.4 km | 2 | 8 | SW Mid ↔ W Mid |
| line-12 |  3.5 km | 3 | 11 | E Inner ↔ SE Mid |
| line-13 |  2.1 km | 3 | 10 | NW Mid ↔ NW Mid |
| line-14 |  2.3 km | 2 | 8 | NW Mid ↔ NW Mid |
| **Total** | **85.0 km** | **72 unique** | **244** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 6,510 one-way journeys / 39,535 train-km/day |
| Annual traction demand | 124.7 GWh |
| Station/depot PV / storage | 85.3 MW / 585.5 MWh |
| Aggregate charging power | 32.5 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-7: 4.8 km / 24 kWh |
| Lowest traversal charging margin | line-7: 23 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $697 M |
| Stations | $417 M |
| Depots | $193 M |
| Rolling stock | $137 M |
| Residual train control | $4.3 M |
| Charging microgrids | $6.8 M |
| EPC / project services | $102 M |
| **Total city programme** | **$1.56 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $304 M (19.5%) |
| Domestic / local capital | $1.25 bn (80.5%) |
| Annual public construction commitment | $190 M / yr for 7 years |
| Annual post-grace debt service | $160 M / yr |
| External capital saved vs default turnkey sensitivity | $2.50 bn |
| Capital + lifetime external interest saved | $5.63 bn |
| Annual OPEX | $38 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 4 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 663 assets / 3,459 tasks | [`jinja-operations-manifest.json`](operations/jinja-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`jinja.toml`](jinja.toml) | Expanded simulator scenario |
| [`jinja.corridor.geojson`](jinja.corridor.geojson) | GIS corridor and stations |
| [`jinja.design-quality.yaml`](jinja.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh jinja
```
