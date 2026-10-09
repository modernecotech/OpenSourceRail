# Ngaoundere — Urban Rail Network

**Country:** CM · **Population:** 350,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Ngaoundere-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.41 bn (88.8%) of external capital** and **$1.77 bn of external interest**. Capital plus saved interest totals **$3.18 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **7 lines**, including **4 additional residential lines**. **46.6%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **29.427 km to 38.540 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **30 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**7 line-local depots** provide **150 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **150 light-metro-3car trainsets / 450 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Ngaoundere rail network on OpenStreetMap](ngaoundere-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 7 / 30 / 7 |
| Route length | 41.2 km double track |
| Direct transfers / reachable line pairs | 33.3% / 100.0% |
| Residents within 800 m radial station catchments | 32,648 (2020 raster; 36.0% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 150 × 3-car `light-metro-3car` trainsets (132 peak revenue) |
| Peak network throughput | 100,800 passengers/hour |
| Practical service capacity | 937,440 passenger-trips/day |
| Annual paid-trip planning range | 171.1–273.7 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  8.2 km | 6 | 28 | N Mid ↔ S Outer |
| line-2 |  6.7 km | 5 | 24 | W Mid ↔ SE Mid |
| line-3 |  6.1 km | 5 | 23 | SW Mid ↔ NE Inner |
| line-4 |  3.3 km | 3 | 14 | SE Mid ↔ E Mid |
| line-5 |  4.7 km | 3 | 17 | N Inner ↔ NW Mid |
| line-6 |  5.8 km | 4 | 21 | N Mid ↔ NW Outer |
| line-7 |  6.4 km | 4 | 23 | SE Mid ↔ NE Mid |
| **Total** | **41.2 km** | **30 unique** | **150** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,255 one-way journeys / 19,176 train-km/day |
| Annual traction demand | 90.7 GWh |
| Station/depot PV / storage | 41.3 MW / 290.5 MWh |
| Aggregate charging power | 14.0 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 5.8 km / 48 kWh |
| Lowest traversal charging margin | line-6: 12 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $438 M |
| Stations | $144 M |
| Depots | $103 M |
| Rolling stock | $135 M |
| Residual train control | $2.1 M |
| Charging microgrids | $3.0 M |
| EPC / project services | $58 M |
| **Total city programme** | **$882 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $178 M (20.2%) |
| Domestic / local capital | $704 M (79.8%) |
| Annual public construction commitment | $76 M / yr for 7 years |
| Annual post-grace debt service | $62 M / yr |
| External capital saved vs default turnkey sensitivity | $1.41 bn |
| Capital + lifetime external interest saved | $3.18 bn |
| Annual OPEX | $23 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 6 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 336 assets / 1,884 tasks | [`ngaoundere-operations-manifest.json`](operations/ngaoundere-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`ngaoundere.toml`](ngaoundere.toml) | Expanded simulator scenario |
| [`ngaoundere.corridor.geojson`](ngaoundere.corridor.geojson) | GIS corridor and stations |
| [`ngaoundere.design-quality.yaml`](ngaoundere.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh ngaoundere
```
