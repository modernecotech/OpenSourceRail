# Herat — Urban Rail Network

**Country:** AF · **Population:** 800,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Herat-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.30 bn (88.4%) of external capital** and **$2.97 bn of external interest**. Capital plus saved interest totals **$5.27 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **10 lines**, including **7 additional residential lines**. **48.1%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **43.191 km to 69.184 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **52 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**10 line-local depots** provide **284 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **284 light-metro-3car trainsets / 852 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Herat rail network on OpenStreetMap](herat-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 10 / 52 / 7 |
| Route length | 79.8 km double track |
| Direct transfers / reachable line pairs | 26.7% / 100.0% |
| Residents within 800 m radial station catchments | 247,699 (2020 raster; 35.4% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 284 × 3-car `light-metro-3car` trainsets (252 peak revenue) |
| Peak network throughput | 144,000 passengers/hour |
| Practical service capacity | 1,339,200 passenger-trips/day |
| Annual paid-trip planning range | 244.4–391.0 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  9.2 km | 6 | 32 | NE Mid ↔ SW Inner |
| line-2 | 10.3 km | 6 | 34 | SE Inner ↔ NW Mid |
| line-3 | 20.7 km | 13 | 70 | NW Outer ↔ E Outer |
| line-4 |  2.3 km | 2 | 10 | NE Inner ↔ N Inner |
| line-5 |  6.6 km | 4 | 23 | SE Inner ↔ S Mid |
| line-6 |  3.3 km | 3 | 14 | NE Inner ↔ E Mid |
| line-7 |  8.4 km | 5 | 30 | NW Inner ↔ SW Outer |
| line-8 |  7.1 km | 5 | 27 | SE Inner ↔ SE Outer |
| line-9 |  7.1 km | 5 | 27 | SW Inner ↔ SW Outer |
| line-10 |  4.7 km | 3 | 17 | SE Inner ↔ S Mid |
| **Total** | **79.8 km** | **52 unique** | **284** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 4,650 one-way journeys / 37,100 train-km/day |
| Annual traction demand | 175.5 GWh |
| Station/depot PV / storage | 59.3 MW / 415.5 MWh |
| Aggregate charging power | 20.5 MW |
| Dedicated solar plant | 21.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-9: 7.1 km / 51 kWh |
| Lowest traversal charging margin | line-5: 21 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $724 M |
| Stations | $190 M |
| Depots | $157 M |
| Rolling stock | $256 M |
| Dedicated solar plant | $17 M |
| Residual train control | $4.0 M |
| Charging microgrids | $4.2 M |
| EPC / project services | $93 M |
| **Total city programme** | **$1.45 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $301 M (20.8%) |
| Domestic / local capital | $1.14 bn (79.2%) |
| Annual public construction commitment | $201 M / yr for 10 years |
| Annual post-grace debt service | $184 M / yr |
| External capital saved vs default turnkey sensitivity | $2.30 bn |
| Capital + lifetime external interest saved | $5.27 bn |
| Annual OPEX | $35 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 13 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 597 assets / 3,461 tasks | [`herat-operations-manifest.json`](operations/herat-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`herat.toml`](herat.toml) | Expanded simulator scenario |
| [`herat.corridor.geojson`](herat.corridor.geojson) | GIS corridor and stations |
| [`herat.design-quality.yaml`](herat.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh herat
```
