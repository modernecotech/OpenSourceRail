# Jos — Urban Rail Network

**Country:** NG · **Population:** 900,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Jos-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.32 bn (88.7%) of external capital** and **$2.91 bn of external interest**. Capital plus saved interest totals **$5.22 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **12 lines**, including **9 additional residential lines**. **49.2%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **42.443 km to 60.850 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **52 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**12 line-local depots** provide **256 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **256 light-metro-3car trainsets / 768 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Jos rail network on OpenStreetMap](jos-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 12 / 52 / 13 |
| Route length | 72.3 km double track |
| Direct transfers / reachable line pairs | 19.7% / 100.0% |
| Residents within 800 m radial station catchments | 265,115 (2020 raster; 35.9% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 256 × 3-car `light-metro-3car` trainsets (226 peak revenue) |
| Peak network throughput | 172,800 passengers/hour |
| Practical service capacity | 1,607,040 passenger-trips/day |
| Annual paid-trip planning range | 293.3–469.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 17.1 km | 10 | 54 | N Outer ↔ S Mid |
| line-2 | 11.4 km | 8 | 37 | N Mid ↔ SW Mid |
| line-3 |  7.9 km | 6 | 27 | NE Mid ↔ SE Mid |
| line-4 |  5.6 km | 4 | 19 | NE Mid ↔ N Mid |
| line-5 |  5.0 km | 4 | 19 | S Mid ↔ SE Mid |
| line-6 |  5.5 km | 4 | 21 | S Mid ↔ S Outer |
| line-7 |  2.6 km | 2 | 11 | E Inner ↔ SE Inner |
| line-8 |  3.7 km | 3 | 14 | NW Mid ↔ N Mid |
| line-9 |  3.2 km | 2 | 12 | SE Inner ↔ SE Mid |
| line-10 |  3.4 km | 3 | 14 | SW Mid ↔ SW Mid |
| line-11 |  3.3 km | 3 | 14 | N Mid ↔ N Outer |
| line-12 |  3.6 km | 3 | 14 | N Mid ↔ NE Mid |
| **Total** | **72.3 km** | **52 unique** | **256** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 5,580 one-way journeys / 33,629 train-km/day |
| Annual traction demand | 159.1 GWh |
| Station/depot PV / storage | 71.1 MW / 498.5 MWh |
| Aggregate charging power | 24.5 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 5.5 km / 46 kWh |
| Lowest traversal charging margin | line-6: 15 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $698 M |
| Stations | $246 M |
| Depots | $174 M |
| Rolling stock | $230 M |
| Residual train control | $3.6 M |
| Charging microgrids | $5.0 M |
| EPC / project services | $95 M |
| **Total city programme** | **$1.45 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $296 M (20.4%) |
| Domestic / local capital | $1.16 bn (79.6%) |
| Annual public construction commitment | $171 M / yr for 7 years |
| Annual post-grace debt service | $144 M / yr |
| External capital saved vs default turnkey sensitivity | $2.32 bn |
| Capital + lifetime external interest saved | $5.22 bn |
| Annual OPEX | $38 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 11 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 577 assets / 3,231 tasks | [`jos-operations-manifest.json`](operations/jos-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`jos.toml`](jos.toml) | Expanded simulator scenario |
| [`jos.corridor.geojson`](jos.corridor.geojson) | GIS corridor and stations |
| [`jos.design-quality.yaml`](jos.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh jos
```
