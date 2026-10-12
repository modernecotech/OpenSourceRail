# Nairobi — Urban Rail Network

**Country:** KE · **Population:** 5,700,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Nairobi-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$18.45 bn (87.4%) of external capital** and **$23.13 bn of external interest**. Capital plus saved interest totals **$41.57 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-12).** The controlled planning inventory contains **14 lines**, including **5 additional residential lines**. **38.4%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **393.543 km to 466.841 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **304 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**14 line-local depots** provide **1128 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **1128 metro-6car trainsets / 6768 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Nairobi rail network on OpenStreetMap](nairobi-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 14 / 304 / 51 |
| Route length | 589.5 km double track |
| Direct transfers / reachable line pairs | 45.1% / 100.0% |
| Residents within 800 m radial station catchments | 1,776,673 (2020 raster; 27.2% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 1128 × 6-car `metro-6car` trainsets (1017 peak revenue) |
| Peak network throughput | 403,200 passengers/hour |
| Practical service capacity | 3,615,840 passenger-trips/day |
| Annual paid-trip planning range | 659.9–1055.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 63.2 km | 20 | 119 | NE Outer ↔ SW Mid |
| line-2 | 57.6 km | 54 | 181 | E Outer ↔ W Mid |
| line-3 | 55.7 km | 37 | 138 | N Inner ↔ SE Outer |
| line-4 | 28.1 km | 13 | 58 | E Mid ↔ W Mid |
| line-5 | 51.3 km | 23 | 101 | NE Mid ↔ SW Mid |
| line-6 | 65.6 km | 23 | 122 | SE Outer ↔ NW Mid |
| line-7 | 58.1 km | 39 | 145 | NW Outer ↔ SE Mid |
| line-8 | 47.2 km | 15 | 90 | SW Mid ↔ N Mid |
| line-9 | 108.5 km | 59 | 60 | NW Inner ↔ W Inner |
| line-10 | 17.9 km | 6 | 36 | NE Mid ↔ E Inner |
| line-11 | 10.5 km | 5 | 23 | W Inner ↔ W Mid |
| line-12 |  8.7 km | 3 | 18 | SW Mid ↔ SW Mid |
| line-13 |  7.6 km | 3 | 16 | W Mid ↔ W Mid |
| line-14 |  9.7 km | 4 | 21 | NE Outer ↔ NE Outer |
| **Total** | **589.5 km** | **304 unique** | **1128** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 6,278 one-way journeys / 248,900 train-km/day |
| Annual traction demand | 2,354.8 GWh |
| Station/depot PV / storage | 148.3 MW / 1,082.0 MWh |
| Aggregate charging power | 550.0 MW |
| Dedicated solar plant | 1,375.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-7: 20.3 km / 304 kWh |
| Lowest traversal charging margin | line-12: 53 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $5.45 bn |
| Stations | $1.99 bn |
| Depots | $453 M |
| Rolling stock | $1.90 bn |
| Dedicated solar plant | $1.10 bn |
| Residual train control | $29 M |
| Charging microgrids | $111 M |
| EPC / project services | $695 M |
| **Total city programme** | **$11.72 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.65 bn (22.6%) |
| Domestic / local capital | $9.07 bn (77.4%) |
| Annual public construction commitment | $1.21 bn / yr for 7 years |
| Annual post-grace debt service | $1.01 bn / yr |
| External capital saved vs default turnkey sensitivity | $18.45 bn |
| Capital + lifetime external interest saved | $41.57 bn |
| Annual OPEX | $287 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 29 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 2,816 assets / 15,634 tasks | [`nairobi-operations-manifest.json`](operations/nairobi-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`nairobi.toml`](nairobi.toml) | Expanded simulator scenario |
| [`nairobi.corridor.geojson`](nairobi.corridor.geojson) | GIS corridor and stations |
| [`nairobi.design-quality.yaml`](nairobi.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh nairobi
```
