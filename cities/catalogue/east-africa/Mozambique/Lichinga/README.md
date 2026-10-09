# Lichinga — Urban Rail Network

**Country:** MZ · **Population:** 250,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Lichinga-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$453 M (89.1%) of external capital** and **$585 M of external interest**. Capital plus saved interest totals **$1.04 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **4 lines**, including **2 additional residential lines**. **29.7%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **14.939 km to 13.526 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **11 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**4 line-local depots** provide **43 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **43 tram-2car trainsets / 86 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Lichinga rail network on OpenStreetMap](lichinga-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 4 / 11 / 2 |
| Route length | 13.5 km double track |
| Direct transfers / reachable line pairs | 33.3% / 33.3% |
| Residents within 800 m radial station catchments | 52,503 (2020 raster; 21.7% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 43 × 2-car `tram-2car` trainsets (35 peak revenue) |
| Peak network throughput | 38,400 passengers/hour |
| Practical service capacity | 357,120 passenger-trips/day |
| Annual paid-trip planning range | 65.2–104.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  4.3 km | 3 | 12 | N Outer ↔ SE Mid |
| line-2 |  2.8 km | 3 | 11 | NW Outer ↔ NE Inner |
| line-3 |  4.3 km | 3 | 12 | NW Mid ↔ S Outer |
| line-4 |  2.1 km | 2 | 8 | SE Mid ↔ SE Outer |
| **Total** | **13.5 km** | **11 unique** | **43** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,860 one-way journeys / 6,290 train-km/day |
| Annual traction demand | 19.8 GWh |
| Station/depot PV / storage | 22.1 MW / 163.5 MWh |
| Aggregate charging power | 5.5 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 2.7 km / 13 kWh |
| Lowest traversal charging margin | line-4: 38 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $137 M |
| Stations | $50 M |
| Depots | $51 M |
| Rolling stock | $24 M |
| Residual train control | $676 k |
| Charging microgrids | $1.2 M |
| EPC / project services | $18 M |
| **Total city programme** | **$283 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $55 M (19.6%) |
| Domestic / local capital | $227 M (80.4%) |
| Annual public construction commitment | $32 M / yr for 10 years |
| Annual post-grace debt service | $28 M / yr |
| External capital saved vs default turnkey sensitivity | $453 M |
| Capital + lifetime external interest saved | $1.04 bn |
| Annual OPEX | $7.0 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 2 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 114 assets / 580 tasks | [`lichinga-operations-manifest.json`](operations/lichinga-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`lichinga.toml`](lichinga.toml) | Expanded simulator scenario |
| [`lichinga.corridor.geojson`](lichinga.corridor.geojson) | GIS corridor and stations |
| [`lichinga.design-quality.yaml`](lichinga.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh lichinga
```
