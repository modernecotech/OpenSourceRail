# Tanta — Urban Rail Network

**Country:** EG · **Population:** 750,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Tanta-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.12 bn (88.2%) of external capital** and **$2.60 bn of external interest**. Capital plus saved interest totals **$4.72 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-12).** The controlled planning inventory contains **5 lines**, including **2 additional residential lines**. **32.9%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **55.793 km to 64.079 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **29 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**5 line-local depots** provide **269 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **269 light-metro-3car trainsets / 807 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Tanta rail network on OpenStreetMap](tanta-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 5 / 29 / 7 |
| Route length | 85.9 km double track |
| Direct transfers / reachable line pairs | 70.0% / 100.0% |
| Residents within 800 m radial station catchments | 356,753 (2020 raster; 23.5% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 269 × 3-car `light-metro-3car` trainsets (243 peak revenue) |
| Peak network throughput | 72,000 passengers/hour |
| Practical service capacity | 669,600 passenger-trips/day |
| Annual paid-trip planning range | 122.2–195.5 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 15.3 km | 5 | 48 | N Mid ↔ SW Mid |
| line-2 | 27.0 km | 9 | 85 | NW Outer ↔ SE Outer |
| line-3 | 28.4 km | 9 | 87 | SW Outer ↔ NE Outer |
| line-4 | 10.0 km | 4 | 31 | NW Inner ↔ SE Inner |
| line-5 |  5.3 km | 2 | 18 | SE Mid ↔ SE Mid |
| **Total** | **85.9 km** | **29 unique** | **269** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,325 one-way journeys / 39,963 train-km/day |
| Annual traction demand | 189.0 GWh |
| Station/depot PV / storage | 31.0 MW / 220.0 MWh |
| Aggregate charging power | 25.0 MW |
| Dedicated solar plant | 63.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 11.3 km / 91 kWh |
| Lowest traversal charging margin | line-5: 84 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $699 M |
| Stations | $151 M |
| Depots | $97 M |
| Rolling stock | $242 M |
| Dedicated solar plant | $51 M |
| Residual train control | $4.3 M |
| Charging microgrids | $5.3 M |
| EPC / project services | $84 M |
| **Total city programme** | **$1.33 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $284 M (21.3%) |
| Domestic / local capital | $1.05 bn (78.7%) |
| Annual public construction commitment | $143 M / yr for 5 years |
| Annual post-grace debt service | $107 M / yr |
| External capital saved vs default turnkey sensitivity | $2.12 bn |
| Capital + lifetime external interest saved | $4.72 bn |
| Annual OPEX | $36 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 3 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 462 assets / 2,953 tasks | [`tanta-operations-manifest.json`](operations/tanta-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`tanta.toml`](tanta.toml) | Expanded simulator scenario |
| [`tanta.corridor.geojson`](tanta.corridor.geojson) | GIS corridor and stations |
| [`tanta.design-quality.yaml`](tanta.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh tanta
```
