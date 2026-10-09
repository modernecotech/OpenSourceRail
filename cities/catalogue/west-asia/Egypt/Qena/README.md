# Qena — Urban Rail Network

**Country:** EG · **Population:** 350,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Qena-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.58 bn (88.9%) of external capital** and **$3.18 bn of external interest**. Capital plus saved interest totals **$5.76 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **10 lines**, including **7 additional residential lines**. **81.6%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **41.769 km to 51.811 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **52 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**10 line-local depots** provide **247 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **247 light-metro-3car trainsets / 741 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Qena rail network on OpenStreetMap](qena-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 10 / 52 / 11 |
| Route length | 70.5 km double track |
| Direct transfers / reachable line pairs | 26.7% / 100.0% |
| Residents within 800 m radial station catchments | 202,900 (2020 raster; 65.2% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 247 × 3-car `light-metro-3car` trainsets (219 peak revenue) |
| Peak network throughput | 144,000 passengers/hour |
| Practical service capacity | 1,339,200 passenger-trips/day |
| Annual paid-trip planning range | 244.4–391.0 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 10.3 km | 7 | 32 | N Mid ↔ W Mid |
| line-2 | 18.4 km | 13 | 59 | W Mid ↔ SE Outer |
| line-3 | 13.2 km | 8 | 43 | NW Inner ↔ N Outer |
| line-4 |  2.9 km | 3 | 13 | NW Inner ↔ NE Inner |
| line-5 |  2.4 km | 2 | 10 | W Inner ↔ W Mid |
| line-6 |  7.0 km | 5 | 24 | N Mid ↔ SE Inner |
| line-7 |  5.3 km | 4 | 21 | W Mid ↔ W Outer |
| line-8 |  2.1 km | 2 | 10 | W Inner ↔ SW Inner |
| line-9 |  3.9 km | 4 | 16 | SE Mid ↔ SE Outer |
| line-10 |  5.1 km | 4 | 19 | SE Mid ↔ SE Outer |
| **Total** | **70.5 km** | **52 unique** | **247** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 4,650 one-way journeys / 32,803 train-km/day |
| Annual traction demand | 155.2 GWh |
| Station/depot PV / storage | 60.5 MW / 435.0 MWh |
| Aggregate charging power | 45.0 MW |
| Dedicated solar plant | 11.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 6.0 km / 48 kWh |
| Lowest traversal charging margin | line-10: 69 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $855 M |
| Stations | $257 M |
| Depots | $152 M |
| Rolling stock | $222 M |
| Dedicated solar plant | $9.5 M |
| Residual train control | $3.5 M |
| Charging microgrids | $9.4 M |
| EPC / project services | $105 M |
| **Total city programme** | **$1.61 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $321 M (19.9%) |
| Domestic / local capital | $1.29 bn (80.1%) |
| Annual public construction commitment | $175 M / yr for 5 years |
| Annual post-grace debt service | $130 M / yr |
| External capital saved vs default turnkey sensitivity | $2.58 bn |
| Capital + lifetime external interest saved | $5.76 bn |
| Annual OPEX | $44 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 9 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 559 assets / 3,139 tasks | [`qena-operations-manifest.json`](operations/qena-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`qena.toml`](qena.toml) | Expanded simulator scenario |
| [`qena.corridor.geojson`](qena.corridor.geojson) | GIS corridor and stations |
| [`qena.design-quality.yaml`](qena.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh qena
```
