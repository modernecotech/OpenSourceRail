# Colombo — Urban Rail Network

**Country:** LK · **Population:** 5,648,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Colombo-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$11.07 bn (87.5%) of external capital** and **$13.87 bn of external interest**. Capital plus saved interest totals **$24.94 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-12).** The controlled planning inventory contains **14 lines**, including **5 additional residential lines**. **37.9%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **217.561 km to 232.783 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **172 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**14 line-local depots** provide **652 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **652 metro-6car trainsets / 3912 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Colombo rail network on OpenStreetMap](colombo-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 14 / 172 / 44 |
| Route length | 355.7 km double track |
| Direct transfers / reachable line pairs | 39.6% / 100.0% |
| Residents within 800 m radial station catchments | 773,297 (2020 raster; 26.3% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 652 × 6-car `metro-6car` trainsets (585 peak revenue) |
| Peak network throughput | 403,200 passengers/hour |
| Practical service capacity | 3,615,840 passenger-trips/day |
| Annual paid-trip planning range | 659.9–1055.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 29.4 km | 11 | 57 | SW Mid ↔ NE Outer |
| line-2 | 29.9 km | 10 | 58 | NW Mid ↔ S Mid |
| line-3 | 47.8 km | 22 | 97 | N Outer ↔ SE Outer |
| line-4 | 29.9 km | 10 | 58 | E Outer ↔ SW Mid |
| line-5 | 28.9 km | 16 | 65 | W Mid ↔ SE Outer |
| line-6 | 30.5 km | 14 | 62 | NE Outer ↔ W Mid |
| line-7 | 25.1 km | 14 | 58 | W Mid ↔ SE Outer |
| line-8 | 25.4 km | 13 | 56 | NW Mid ↔ S Outer |
| line-9 | 71.0 km | 38 | 40 | NW Mid ↔ W Mid |
| line-10 |  6.5 km | 2 | 14 | SW Mid ↔ S Outer |
| line-11 |  6.6 km | 2 | 14 | N Mid ↔ N Mid |
| line-12 |  6.2 km | 3 | 15 | NW Mid ↔ N Inner |
| line-13 |  9.5 km | 8 | 28 | N Outer ↔ NE Outer |
| line-14 |  9.0 km | 9 | 30 | N Outer ↔ N Mid |
| **Total** | **355.7 km** | **172 unique** | **652** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 6,278 one-way journeys / 148,888 train-km/day |
| Annual traction demand | 1,408.6 GWh |
| Station/depot PV / storage | 115.3 MW / 862.0 MWh |
| Aggregate charging power | 330.0 MW |
| Dedicated solar plant | 792.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 11.0 km / 164 kWh |
| Lowest traversal charging margin | line-11: 87 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $3.24 bn |
| Stations | $1.23 bn |
| Depots | $330 M |
| Rolling stock | $1.10 bn |
| Dedicated solar plant | $634 M |
| Residual train control | $18 M |
| Charging microgrids | $68 M |
| EPC / project services | $418 M |
| **Total city programme** | **$7.03 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.58 bn (22.5%) |
| Domestic / local capital | $5.45 bn (77.5%) |
| Annual public construction commitment | $815 M / yr for 7 years |
| Annual post-grace debt service | $690 M / yr |
| External capital saved vs default turnkey sensitivity | $11.07 bn |
| Capital + lifetime external interest saved | $24.94 bn |
| Annual OPEX | $173 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 10 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,630 assets / 8,990 tasks | [`colombo-operations-manifest.json`](operations/colombo-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`colombo.toml`](colombo.toml) | Expanded simulator scenario |
| [`colombo.corridor.geojson`](colombo.corridor.geojson) | GIS corridor and stations |
| [`colombo.design-quality.yaml`](colombo.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh colombo
```
