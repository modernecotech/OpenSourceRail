# Marrakech — Urban Rail Network

**Country:** MA · **Population:** 1,200,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Marrakech-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$6.39 bn (88.6%) of external capital** and **$7.85 bn of external interest**. Capital plus saved interest totals **$14.24 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **15 lines**, including **9 additional residential lines**. **79.7%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **162.306 km to 194.614 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 1 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **156 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**15 line-local depots** provide **434 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **434 metro-4car trainsets / 1736 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Marrakech rail network on OpenStreetMap](marrakech-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 15 / 156 / 27 |
| Route length | 229.4 km double track |
| Direct transfers / reachable line pairs | 28.6% / 100.0% |
| Residents within 800 m radial station catchments | 865,389 (2020 raster; 63.0% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 434 × 4-car `metro-4car` trainsets (385 peak revenue) |
| Peak network throughput | 288,000 passengers/hour |
| Practical service capacity | 2,589,120 passenger-trips/day |
| Annual paid-trip planning range | 472.5–756.0 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 27.8 km | 20 | 61 | NW Inner ↔ SE Outer |
| line-2 | 24.8 km | 17 | 54 | NE Outer ↔ SW Inner |
| line-3 | 21.1 km | 14 | 47 | W Inner ↔ E Outer |
| line-4 | 25.4 km | 18 | 58 | S Outer ↔ N Mid |
| line-5 | 30.6 km | 19 | 60 | S Mid ↔ NW Outer |
| line-6 | 53.0 km | 32 | 27 | W Inner ↔ W Inner |
| line-7 |  4.4 km | 3 | 12 | SE Inner ↔ SE Inner |
| line-8 |  5.1 km | 4 | 15 | SE Inner ↔ S Mid |
| line-9 |  4.2 km | 4 | 14 | NW Inner ↔ N Inner |
| line-10 |  6.1 km | 5 | 17 | SE Inner ↔ NE Inner |
| line-11 |  5.6 km | 4 | 13 | W Inner ↔ W Mid |
| line-12 |  5.3 km | 4 | 13 | SW Inner ↔ SW Mid |
| line-13 |  4.9 km | 3 | 12 | NW Outer ↔ NW Outer |
| line-14 |  6.4 km | 4 | 15 | SE Mid ↔ S Inner |
| line-15 |  4.7 km | 5 | 16 | NE Inner ↔ N Inner |
| **Total** | **229.4 km** | **156 unique** | **434** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 6,742 one-way journeys / 94,349 train-km/day |
| Annual traction demand | 595.1 GWh |
| Station/depot PV / storage | 106.2 MW / 756.0 MWh |
| Aggregate charging power | 178.5 MW |
| Dedicated solar plant | 190.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 12.5 km / 135 kWh |
| Lowest traversal charging margin | line-11: 80 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.08 bn |
| Stations | $723 M |
| Depots | $258 M |
| Rolling stock | $486 M |
| Dedicated solar plant | $152 M |
| Residual train control | $11 M |
| Charging microgrids | $36 M |
| EPC / project services | $252 M |
| **Total city programme** | **$4.00 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $818 M (20.4%) |
| Domestic / local capital | $3.18 bn (79.6%) |
| Annual public construction commitment | $279 M / yr for 5 years |
| Annual post-grace debt service | $193 M / yr |
| External capital saved vs default turnkey sensitivity | $6.39 bn |
| Capital + lifetime external interest saved | $14.24 bn |
| Annual OPEX | $116 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 27 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,272 assets / 6,585 tasks | [`marrakech-operations-manifest.json`](operations/marrakech-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`marrakech.toml`](marrakech.toml) | Expanded simulator scenario |
| [`marrakech.corridor.geojson`](marrakech.corridor.geojson) | GIS corridor and stations |
| [`marrakech.design-quality.yaml`](marrakech.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh marrakech
```
