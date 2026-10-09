# Latakia — Urban Rail Network

**Country:** SY · **Population:** 700,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Latakia-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.79 bn (88.5%) of external capital** and **$2.32 bn of external interest**. Capital plus saved interest totals **$4.11 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **10 lines**, including **7 additional residential lines**. **78.9%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **40.022 km to 51.986 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **40 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**10 line-local depots** provide **210 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **210 light-metro-3car trainsets / 630 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Latakia rail network on OpenStreetMap](latakia-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 10 / 40 / 9 |
| Route length | 56.9 km double track |
| Direct transfers / reachable line pairs | 26.7% / 100.0% |
| Residents within 800 m radial station catchments | 389,797 (2020 raster; 62.2% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 210 × 3-car `light-metro-3car` trainsets (185 peak revenue) |
| Peak network throughput | 144,000 passengers/hour |
| Practical service capacity | 1,339,200 passenger-trips/day |
| Annual paid-trip planning range | 244.4–391.0 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 13.3 km | 9 | 48 | SW Mid ↔ E Outer |
| line-2 |  6.7 km | 4 | 23 | W Mid ↔ NE Mid |
| line-3 |  9.3 km | 6 | 32 | SW Mid ↔ NW Outer |
| line-4 |  5.2 km | 4 | 18 | SE Inner ↔ SW Mid |
| line-5 |  4.8 km | 3 | 17 | SE Mid ↔ S Mid |
| line-6 |  3.6 km | 3 | 14 | NW Mid ↔ NW Outer |
| line-7 |  4.5 km | 3 | 17 | NW Inner ↔ N Mid |
| line-8 |  2.6 km | 2 | 11 | W Inner ↔ S Inner |
| line-9 |  3.1 km | 3 | 14 | E Mid ↔ SE Mid |
| line-10 |  3.8 km | 3 | 16 | NW Outer ↔ N Outer |
| **Total** | **56.9 km** | **40 unique** | **210** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 4,650 one-way journeys / 26,437 train-km/day |
| Annual traction demand | 125.1 GWh |
| Station/depot PV / storage | 58.1 MW / 413.5 MWh |
| Aggregate charging power | 18.5 MW |
| Dedicated solar plant | 4.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 4.5 km / 32 kWh |
| Lowest traversal charging margin | line-10: 19 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $523 M |
| Stations | $184 M |
| Depots | $146 M |
| Rolling stock | $189 M |
| Dedicated solar plant | $3.9 M |
| Residual train control | $2.8 M |
| Charging microgrids | $3.9 M |
| EPC / project services | $73 M |
| **Total city programme** | **$1.13 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $234 M (20.7%) |
| Domestic / local capital | $893 M (79.3%) |
| Annual public construction commitment | $171 M / yr for 10 years |
| Annual post-grace debt service | $158 M / yr |
| External capital saved vs default turnkey sensitivity | $1.79 bn |
| Capital + lifetime external interest saved | $4.11 bn |
| Annual OPEX | $27 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 8 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 460 assets / 2,600 tasks | [`latakia-operations-manifest.json`](operations/latakia-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`latakia.toml`](latakia.toml) | Expanded simulator scenario |
| [`latakia.corridor.geojson`](latakia.corridor.geojson) | GIS corridor and stations |
| [`latakia.design-quality.yaml`](latakia.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh latakia
```
