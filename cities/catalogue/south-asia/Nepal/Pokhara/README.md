# Pokhara — Urban Rail Network

**Country:** NP · **Population:** 600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Pokhara-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.59 bn (88.5%) of external capital** and **$3.24 bn of external interest**. Capital plus saved interest totals **$5.83 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-12).** The controlled planning inventory contains **5 lines**, including **2 additional residential lines**. **45.5%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **58.854 km to 71.069 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **38 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**5 line-local depots** provide **293 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **293 light-metro-3car trainsets / 879 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Pokhara rail network on OpenStreetMap](pokhara-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 5 / 38 / 7 |
| Route length | 91.5 km double track |
| Direct transfers / reachable line pairs | 50.0% / 100.0% |
| Residents within 800 m radial station catchments | 132,866 (2020 raster; 33.0% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 293 × 3-car `light-metro-3car` trainsets (263 peak revenue) |
| Peak network throughput | 72,000 passengers/hour |
| Practical service capacity | 669,600 passenger-trips/day |
| Annual paid-trip planning range | 122.2–195.5 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 26.7 km | 13 | 89 | SE Outer ↔ NW Outer |
| line-2 | 25.7 km | 13 | 83 | NW Mid ↔ SE Outer |
| line-3 | 26.3 km | 7 | 79 | NW Outer ↔ SE Outer |
| line-4 |  7.2 km | 3 | 24 | NW Inner ↔ S Inner |
| line-5 |  5.5 km | 2 | 18 | E Inner ↔ NW Inner |
| **Total** | **91.5 km** | **38 unique** | **293** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,325 one-way journeys / 42,547 train-km/day |
| Annual traction demand | 201.3 GWh |
| Station/depot PV / storage | 34.3 MW / 215.5 MWh |
| Aggregate charging power | 18.0 MW |
| Dedicated solar plant | 62.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 10.0 km / 72 kWh |
| Lowest traversal charging margin | line-5: 21 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $869 M |
| Stations | $228 M |
| Depots | $101 M |
| Rolling stock | $264 M |
| Dedicated solar plant | $50 M |
| Residual train control | $4.6 M |
| Charging microgrids | $3.8 M |
| EPC / project services | $103 M |
| **Total city programme** | **$1.62 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $336 M (20.7%) |
| Domestic / local capital | $1.29 bn (79.3%) |
| Annual public construction commitment | $129 M / yr for 7 years |
| Annual post-grace debt service | $105 M / yr |
| External capital saved vs default turnkey sensitivity | $2.59 bn |
| Capital + lifetime external interest saved | $5.83 bn |
| Annual OPEX | $40 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 5 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 536 assets / 3,342 tasks | [`pokhara-operations-manifest.json`](operations/pokhara-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`pokhara.toml`](pokhara.toml) | Expanded simulator scenario |
| [`pokhara.corridor.geojson`](pokhara.corridor.geojson) | GIS corridor and stations |
| [`pokhara.design-quality.yaml`](pokhara.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh pokhara
```
