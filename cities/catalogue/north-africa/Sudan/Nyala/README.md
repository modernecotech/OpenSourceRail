# Nyala — Urban Rail Network

**Country:** SD · **Population:** 600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Nyala-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.68 bn (88.8%) of external capital** and **$3.46 bn of external interest**. Capital plus saved interest totals **$6.14 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **12 lines**, including **9 additional residential lines**. **41.6%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **44.461 km to 74.354 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **56 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**12 line-local depots** provide **276 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **276 light-metro-3car trainsets / 828 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Nyala rail network on OpenStreetMap](nyala-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 12 / 56 / 12 |
| Route length | 77.2 km double track |
| Direct transfers / reachable line pairs | 21.2% / 100.0% |
| Residents within 800 m radial station catchments | 82,729 (2020 raster; 30.0% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 276 × 3-car `light-metro-3car` trainsets (245 peak revenue) |
| Peak network throughput | 172,800 passengers/hour |
| Practical service capacity | 1,607,040 passenger-trips/day |
| Annual paid-trip planning range | 293.3–469.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 16.4 km | 10 | 54 | SW Outer ↔ E Outer |
| line-2 | 11.6 km | 8 | 37 | N Mid ↔ S Outer |
| line-3 | 10.9 km | 7 | 38 | SE Mid ↔ W Outer |
| line-4 |  5.0 km | 3 | 17 | E Inner ↔ NW Mid |
| line-5 |  3.2 km | 3 | 14 | N Mid ↔ NE Inner |
| line-6 |  3.6 km | 4 | 17 | W Mid ↔ SW Mid |
| line-7 |  5.6 km | 4 | 19 | N Mid ↔ NE Mid |
| line-8 |  5.0 km | 4 | 18 | N Mid ↔ NW Mid |
| line-9 |  5.0 km | 4 | 19 | E Inner ↔ SE Outer |
| line-10 |  3.4 km | 3 | 14 | E Mid ↔ E Outer |
| line-11 |  3.4 km | 3 | 14 | SW Mid ↔ S Mid |
| line-12 |  4.1 km | 3 | 15 | W Outer ↔ NW Outer |
| **Total** | **77.2 km** | **56 unique** | **276** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 5,580 one-way journeys / 35,906 train-km/day |
| Annual traction demand | 169.8 GWh |
| Station/depot PV / storage | 72.9 MW / 501.5 MWh |
| Aggregate charging power | 27.5 MW |
| Dedicated solar plant | 5.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-9: 3.4 km / 28 kWh |
| Lowest traversal charging margin | line-4: 25 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $857 M |
| Stations | $269 M |
| Depots | $179 M |
| Rolling stock | $248 M |
| Dedicated solar plant | $4.3 M |
| Residual train control | $3.9 M |
| Charging microgrids | $5.7 M |
| EPC / project services | $109 M |
| **Total city programme** | **$1.68 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $337 M (20.1%) |
| Domestic / local capital | $1.34 bn (79.9%) |
| Annual public construction commitment | $203 M / yr for 10 years |
| Annual post-grace debt service | $184 M / yr |
| External capital saved vs default turnkey sensitivity | $2.68 bn |
| Capital + lifetime external interest saved | $6.14 bn |
| Annual OPEX | $41 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 16 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 622 assets / 3,494 tasks | [`nyala-operations-manifest.json`](operations/nyala-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`nyala.toml`](nyala.toml) | Expanded simulator scenario |
| [`nyala.corridor.geojson`](nyala.corridor.geojson) | GIS corridor and stations |
| [`nyala.design-quality.yaml`](nyala.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh nyala
```
