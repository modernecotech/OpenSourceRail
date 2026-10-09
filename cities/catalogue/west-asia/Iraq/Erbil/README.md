# Erbil — Urban Rail Network

**Country:** IQ · **Population:** 1,952,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Erbil-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$7.42 bn (88.2%) of external capital** and **$9.12 bn of external interest**. Capital plus saved interest totals **$16.54 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **31 lines**, including **26 additional residential lines**. **75.0%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **103.830 km to 165.615 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **180 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**31 line-local depots** provide **628 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **628 metro-4car trainsets / 2512 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Erbil rail network on OpenStreetMap](erbil-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 31 / 180 / 43 |
| Route length | 245.5 km double track |
| Direct transfers / reachable line pairs | 10.8% / 100.0% |
| Residents within 800 m radial station catchments | 714,410 (2020 raster; 57.8% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 628 × 4-car `metro-4car` trainsets (546 peak revenue) |
| Peak network throughput | 595,200 passengers/hour |
| Practical service capacity | 5,535,360 passenger-trips/day |
| Annual paid-trip planning range | 1010.2–1616.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 29.5 km | 19 | 63 | NW Outer ↔ S Mid |
| line-2 | 30.8 km | 19 | 64 | SW Outer ↔ NE Outer |
| line-3 | 20.0 km | 14 | 48 | W Mid ↔ E Outer |
| line-4 | 25.0 km | 17 | 57 | N Outer ↔ S Mid |
| line-5 | 18.0 km | 13 | 45 | SW Mid ↔ SE Outer |
| line-6 |  4.3 km | 3 | 12 | E Inner ↔ SE Inner |
| line-7 |  2.6 km | 2 | 9 | SW Mid ↔ W Mid |
| line-8 |  2.9 km | 4 | 13 | E Mid ↔ E Mid |
| line-9 |  4.9 km | 5 | 16 | W Inner ↔ W Inner |
| line-10 |  2.9 km | 2 | 9 | SW Mid ↔ SW Mid |
| line-11 |  3.5 km | 3 | 11 | SE Mid ↔ SE Mid |
| line-12 |  6.3 km | 4 | 15 | SE Mid ↔ S Outer |
| line-13 |  8.1 km | 6 | 21 | N Inner ↔ NW Mid |
| line-14 |  4.0 km | 3 | 12 | SW Inner ↔ SW Mid |
| line-15 |  3.8 km | 3 | 11 | N Mid ↔ N Mid |
| line-16 |  2.7 km | 2 | 9 | S Mid ↔ S Mid |
| line-17 |  2.7 km | 2 | 9 | E Mid ↔ E Inner |
| line-18 |  3.6 km | 3 | 11 | E Mid ↔ E Mid |
| line-19 |  5.0 km | 5 | 15 | NW Mid ↔ W Mid |
| line-20 | 11.5 km | 7 | 25 | SW Mid ↔ W Outer |
| line-21 |  2.6 km | 2 | 9 | NE Mid ↔ N Inner |
| line-22 |  4.7 km | 4 | 13 | S Mid ↔ S Outer |
| line-23 |  4.3 km | 3 | 11 | NE Outer ↔ NE Outer |
| line-24 |  6.4 km | 6 | 19 | SE Mid ↔ E Mid |
| line-25 |  3.3 km | 3 | 10 | NE Mid ↔ N Mid |
| line-26 |  2.9 km | 2 | 9 | NW Mid ↔ NW Outer |
| line-27 |  3.3 km | 4 | 13 | NW Mid ↔ NW Mid |
| line-28 |  4.3 km | 3 | 12 | S Inner ↔ S Inner |
| line-29 | 10.5 km | 8 | 25 | N Mid ↔ NW Inner |
| line-30 |  7.0 km | 5 | 18 | SW Mid ↔ W Outer |
| line-31 |  4.2 km | 4 | 14 | W Inner ↔ NE Inner |
| **Total** | **245.5 km** | **180 unique** | **628** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 14,415 one-way journeys / 114,153 train-km/day |
| Annual traction demand | 720.0 GWh |
| Station/depot PV / storage | 194.0 MW / 1,435.0 MWh |
| Aggregate charging power | 241.5 MW |
| Dedicated solar plant | 155.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 8.3 km / 90 kWh |
| Lowest traversal charging margin | line-23: 96 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.99 bn |
| Stations | $1.02 bn |
| Depots | $481 M |
| Rolling stock | $703 M |
| Dedicated solar plant | $124 M |
| Residual train control | $12 M |
| Charging microgrids | $50 M |
| EPC / project services | $298 M |
| **Total city programme** | **$4.68 bn** |

## Iraq funding

Proposed facilities and appropriations remain uncommitted. The conditional ledger calculates government capital and the extra support required for fees, interest, reserves and cash shortfalls; additional support is not a funding commitment.

| Capital source | Planning USD equivalent |
|---|---:|
| bank credit | $444 M |
| chinese export credit | $238 M |
| domestic bonds | $1.33 bn |
| government | $2.66 bn |

The procurement schedule requires **71 calendar months** of capital cash under an assumed 260-working-day year. The resource-constrained full-network rollout needs review before a construction commitment.

Peak annual government cash: **$804 M**. This includes support required under the low capacity-use case; it is not a funded appropriation.

Chinese export buyer credit is allocated within existing imported budgets for solar equipment, bogies, batteries, windows and doors. City CAPEX excludes manufacturing tooling; the Baghdad-only programme separately funds one plant for Baghdad. IQD bonds assume a proposed Ministry of Finance programme; municipal borrowing authority is pending legal review.

The model includes actual scheduled draws, native-currency principal/interest, fees, revenue ramps, operating/debt support, reserve movements and downside cases. Short bullet bonds have explicit redemptions without assumed refinancing.

See [funding model](engineering/finance/FUNDING-MODEL.md), [monthly cashflow](engineering/finance/funding-monthly-cashflow.csv), [annual cashflow](engineering/finance/funding-annual-cashflow.csv) . This standalone city appraisal is outside the Baghdad-only funding programme.

Annual operating allowance: $142 M; demand remains capacity-led.

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 23 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,667 assets / 8,818 tasks | [`erbil-operations-manifest.json`](operations/erbil-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`erbil.toml`](erbil.toml) | Expanded simulator scenario |
| [`erbil.corridor.geojson`](erbil.corridor.geojson) | GIS corridor and stations |
| [`erbil.design-quality.yaml`](erbil.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh erbil
```
