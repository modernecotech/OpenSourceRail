# Jalalabad-Af — Urban Rail Network

**Country:** AF · **Population:** 350,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Jalalabad-Af-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.41 bn (88.4%) of external capital** and **$3.12 bn of external interest**. Capital plus saved interest totals **$5.53 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **10 lines**, including **7 additional residential lines**. **74.2%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **43.025 km to 62.546 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **57 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**10 line-local depots** provide **291 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **291 light-metro-3car trainsets / 873 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Jalalabad-Af rail network on OpenStreetMap](jalalabad-af-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 10 / 57 / 13 |
| Route length | 78.9 km double track |
| Direct transfers / reachable line pairs | 26.7% / 100.0% |
| Residents within 800 m radial station catchments | 350,013 (2020 raster; 60.3% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 291 × 3-car `light-metro-3car` trainsets (259 peak revenue) |
| Peak network throughput | 144,000 passengers/hour |
| Practical service capacity | 1,339,200 passenger-trips/day |
| Annual paid-trip planning range | 244.4–391.0 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  8.2 km | 6 | 28 | SE Mid ↔ N Inner |
| line-2 | 20.4 km | 14 | 71 | SE Outer ↔ NW Mid |
| line-3 | 11.9 km | 8 | 42 | NE Mid ↔ S Inner |
| line-4 |  2.8 km | 3 | 13 | E Inner ↔ SE Inner |
| line-5 |  3.5 km | 3 | 14 | NW Inner ↔ S Inner |
| line-6 |  3.4 km | 3 | 14 | NW Inner ↔ W Mid |
| line-7 |  7.9 km | 6 | 31 | NW Mid ↔ NW Outer |
| line-8 |  6.8 km | 5 | 27 | SE Mid ↔ S Outer |
| line-9 |  6.1 km | 4 | 23 | NW Inner ↔ SW Mid |
| line-10 |  7.8 km | 5 | 28 | SE Inner ↔ SE Mid |
| **Total** | **78.9 km** | **57 unique** | **291** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 4,650 one-way journeys / 36,709 train-km/day |
| Annual traction demand | 173.6 GWh |
| Station/depot PV / storage | 61.4 MW / 419.0 MWh |
| Aggregate charging power | 24.0 MW |
| Dedicated solar plant | 17.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-7: 6.8 km / 49 kWh |
| Lowest traversal charging margin | line-9: 25 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $702 M |
| Stations | $275 M |
| Depots | $157 M |
| Rolling stock | $262 M |
| Dedicated solar plant | $14 M |
| Residual train control | $3.9 M |
| Charging microgrids | $5.0 M |
| EPC / project services | $98 M |
| **Total city programme** | **$1.52 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $316 M (20.8%) |
| Domestic / local capital | $1.20 bn (79.2%) |
| Annual public construction commitment | $211 M / yr for 10 years |
| Annual post-grace debt service | $194 M / yr |
| External capital saved vs default turnkey sensitivity | $2.41 bn |
| Capital + lifetime external interest saved | $5.53 bn |
| Annual OPEX | $36 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 9 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 632 assets / 3,623 tasks | [`jalalabad-af-operations-manifest.json`](operations/jalalabad-af-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`jalalabad-af.toml`](jalalabad-af.toml) | Expanded simulator scenario |
| [`jalalabad-af.corridor.geojson`](jalalabad-af.corridor.geojson) | GIS corridor and stations |
| [`jalalabad-af.design-quality.yaml`](jalalabad-af.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh jalalabad-af
```
