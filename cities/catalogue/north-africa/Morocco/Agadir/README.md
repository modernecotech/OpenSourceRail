# Agadir — Urban Rail Network

**Country:** MA · **Population:** 900,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Agadir-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.66 bn (88.2%) of external capital** and **$3.27 bn of external interest**. Capital plus saved interest totals **$5.93 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **10 lines**, including **7 additional residential lines**. **77.7%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **57.669 km to 59.981 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **64 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**10 line-local depots** provide **340 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **340 light-metro-3car trainsets / 1020 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Agadir rail network on OpenStreetMap](agadir-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 10 / 64 / 11 |
| Route length | 96.4 km double track |
| Direct transfers / reachable line pairs | 26.7% / 100.0% |
| Residents within 800 m radial station catchments | 567,678 (2020 raster; 59.4% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 340 × 3-car `light-metro-3car` trainsets (301 peak revenue) |
| Peak network throughput | 144,000 passengers/hour |
| Practical service capacity | 1,339,200 passenger-trips/day |
| Annual paid-trip planning range | 244.4–391.0 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 24.4 km | 13 | 79 | SE Outer ↔ NW Mid |
| line-2 | 24.5 km | 17 | 83 | NW Outer ↔ SE Mid |
| line-3 | 24.3 km | 14 | 83 | SE Mid ↔ N Outer |
| line-4 |  7.2 km | 5 | 25 | SE Mid ↔ SE Outer |
| line-5 |  2.3 km | 2 | 10 | NW Inner ↔ W Inner |
| line-6 |  2.9 km | 3 | 12 | SE Mid ↔ SE Mid |
| line-7 |  3.1 km | 3 | 14 | SE Mid ↔ SE Mid |
| line-8 |  2.4 km | 2 | 10 | SE Inner ↔ S Inner |
| line-9 |  2.9 km | 3 | 14 | N Inner ↔ NE Inner |
| line-10 |  2.4 km | 2 | 10 | NW Outer ↔ NW Outer |
| **Total** | **96.4 km** | **64 unique** | **340** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 4,650 one-way journeys / 44,838 train-km/day |
| Annual traction demand | 212.1 GWh |
| Station/depot PV / storage | 64.4 MW / 424.0 MWh |
| Aggregate charging power | 29.0 MW |
| Dedicated solar plant | 37.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-4: 4.8 km / 39 kWh |
| Lowest traversal charging margin | line-6: 23 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $757 M |
| Stations | $300 M |
| Depots | $165 M |
| Rolling stock | $306 M |
| Dedicated solar plant | $30 M |
| Residual train control | $4.8 M |
| Charging microgrids | $6.1 M |
| EPC / project services | $108 M |
| **Total city programme** | **$1.68 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $356 M (21.3%) |
| Domestic / local capital | $1.32 bn (78.7%) |
| Annual public construction commitment | $116 M / yr for 5 years |
| Annual post-grace debt service | $81 M / yr |
| External capital saved vs default turnkey sensitivity | $2.66 bn |
| Capital + lifetime external interest saved | $5.93 bn |
| Annual OPEX | $54 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 21 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 726 assets / 4,209 tasks | [`agadir-operations-manifest.json`](operations/agadir-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`agadir.toml`](agadir.toml) | Expanded simulator scenario |
| [`agadir.corridor.geojson`](agadir.corridor.geojson) | GIS corridor and stations |
| [`agadir.design-quality.yaml`](agadir.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh agadir
```
