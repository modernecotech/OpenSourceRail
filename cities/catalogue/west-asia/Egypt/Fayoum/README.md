# Fayoum — Urban Rail Network

**Country:** EG · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Fayoum-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.19 bn (88.0%) of external capital** and **$3.92 bn of external interest**. Capital plus saved interest totals **$7.10 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **13 lines**, including **10 additional residential lines**. **71.8%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **55.592 km to 69.098 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **82 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**13 line-local depots** provide **433 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **433 light-metro-3car trainsets / 1299 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Fayoum rail network on OpenStreetMap](fayoum-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 13 / 82 / 15 |
| Route length | 120.3 km double track |
| Direct transfers / reachable line pairs | 19.2% / 100.0% |
| Residents within 800 m radial station catchments | 867,884 (2020 raster; 58.1% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 433 × 3-car `light-metro-3car` trainsets (385 peak revenue) |
| Peak network throughput | 187,200 passengers/hour |
| Practical service capacity | 1,740,960 passenger-trips/day |
| Annual paid-trip planning range | 317.7–508.4 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 26.2 km | 18 | 89 | NW Outer ↔ SE Outer |
| line-2 | 15.2 km | 9 | 49 | E Mid ↔ NW Inner |
| line-3 | 18.9 km | 11 | 64 | SW Mid ↔ NE Mid |
| line-4 |  2.8 km | 2 | 11 | N Inner ↔ SW Inner |
| line-5 |  8.4 km | 6 | 31 | NE Mid ↔ N Outer |
| line-6 |  5.7 km | 5 | 24 | SW Mid ↔ SW Outer |
| line-7 |  6.5 km | 6 | 25 | NW Mid ↔ N Mid |
| line-8 |  2.5 km | 3 | 13 | SE Inner ↔ S Inner |
| line-9 | 10.6 km | 6 | 38 | NE Mid ↔ NE Outer |
| line-10 |  3.0 km | 2 | 11 | NE Inner ↔ N Inner |
| line-11 |  9.0 km | 6 | 34 | SW Mid ↔ W Outer |
| line-12 |  6.1 km | 4 | 23 | S Inner ↔ S Mid |
| line-13 |  5.3 km | 4 | 21 | NW Outer ↔ NW Outer |
| **Total** | **120.3 km** | **82 unique** | **433** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 6,045 one-way journeys / 55,948 train-km/day |
| Annual traction demand | 264.7 GWh |
| Station/depot PV / storage | 80.3 MW / 545.5 MWh |
| Aggregate charging power | 32.0 MW |
| Dedicated solar plant | 46.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-11: 8.3 km / 67 kWh |
| Lowest traversal charging margin | line-13: 18 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $851 M |
| Stations | $378 M |
| Depots | $214 M |
| Rolling stock | $390 M |
| Dedicated solar plant | $37 M |
| Residual train control | $6.0 M |
| Charging microgrids | $6.7 M |
| EPC / project services | $129 M |
| **Total city programme** | **$2.01 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $435 M (21.6%) |
| Domestic / local capital | $1.58 bn (78.4%) |
| Annual public construction commitment | $215 M / yr for 5 years |
| Annual post-grace debt service | $162 M / yr |
| External capital saved vs default turnkey sensitivity | $3.19 bn |
| Capital + lifetime external interest saved | $7.10 bn |
| Annual OPEX | $59 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 13 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 917 assets / 5,327 tasks | [`fayoum-operations-manifest.json`](operations/fayoum-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`fayoum.toml`](fayoum.toml) | Expanded simulator scenario |
| [`fayoum.corridor.geojson`](fayoum.corridor.geojson) | GIS corridor and stations |
| [`fayoum.design-quality.yaml`](fayoum.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh fayoum
```
