# Mosul — Urban Rail Network

**Country:** IQ · **Population:** 1,940,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Mosul-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$8.42 bn (88.9%) of external capital** and **$10.35 bn of external interest**. Capital plus saved interest totals **$18.77 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **19 lines**, including **13 additional residential lines**. **77.6%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **169.781 km to 209.647 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **175 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**19 line-local depots** provide **521 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **521 metro-4car trainsets / 2084 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Mosul rail network on OpenStreetMap](mosul-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 19 / 175 / 41 |
| Route length | 272.7 km double track |
| Direct transfers / reachable line pairs | 20.5% / 100.0% |
| Residents within 800 m radial station catchments | 653,496 (2020 raster; 62.8% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 521 × 4-car `metro-4car` trainsets (462 peak revenue) |
| Peak network throughput | 364,800 passengers/hour |
| Practical service capacity | 3,303,360 passenger-trips/day |
| Annual paid-trip planning range | 602.9–964.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 31.1 km | 19 | 61 | SE Mid ↔ NW Outer |
| line-2 | 28.9 km | 17 | 56 | S Mid ↔ NE Outer |
| line-3 | 28.7 km | 17 | 60 | SE Mid ↔ NW Outer |
| line-4 | 26.3 km | 16 | 53 | E Outer ↔ SW Inner |
| line-5 | 20.0 km | 13 | 43 | SE Mid ↔ NW Mid |
| line-6 | 56.0 km | 31 | 28 | N Mid ↔ N Mid |
| line-7 |  6.9 km | 7 | 23 | SW Inner ↔ S Inner |
| line-8 |  4.5 km | 3 | 12 | W Inner ↔ NW Inner |
| line-9 |  6.2 km | 6 | 19 | SW Inner ↔ SW Mid |
| line-10 |  4.1 km | 3 | 11 | W Mid ↔ W Mid |
| line-11 |  6.4 km | 4 | 15 | NW Outer ↔ NW Outer |
| line-12 |  4.6 km | 5 | 16 | S Inner ↔ SW Inner |
| line-13 |  4.4 km | 3 | 12 | SE Inner ↔ S Mid |
| line-14 |  3.8 km | 3 | 12 | N Mid ↔ N Mid |
| line-15 | 17.2 km | 10 | 36 | S Mid ↔ SE Outer |
| line-16 |  4.9 km | 3 | 12 | SE Inner ↔ SE Inner |
| line-17 |  7.4 km | 5 | 18 | SW Mid ↔ SW Outer |
| line-18 |  7.5 km | 5 | 18 | W Inner ↔ NW Mid |
| line-19 |  3.9 km | 5 | 16 | S Inner ↔ SW Inner |
| **Total** | **272.7 km** | **175 unique** | **521** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 8,602 one-way journeys / 113,772 train-km/day |
| Annual traction demand | 717.6 GWh |
| Station/depot PV / storage | 131.6 MW / 943.0 MWh |
| Aggregate charging power | 210.0 MW |
| Dedicated solar plant | 225.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-15: 17.2 km / 184 kWh |
| Lowest traversal charging margin | line-15: 67 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.96 bn |
| Stations | $824 M |
| Depots | $321 M |
| Rolling stock | $584 M |
| Dedicated solar plant | $180 M |
| Residual train control | $14 M |
| Charging microgrids | $42 M |
| EPC / project services | $332 M |
| **Total city programme** | **$5.26 bn** |

## Iraq funding

Proposed facilities and appropriations remain uncommitted. The conditional ledger calculates government capital and the extra support required for fees, interest, reserves and cash shortfalls; additional support is not a funding commitment.

| Capital source | Planning USD equivalent |
|---|---:|
| bank credit | $503 M |
| chinese export credit | $227 M |
| domestic bonds | $1.51 bn |
| government | $3.02 bn |

The procurement schedule requires **64 calendar months** of capital cash under an assumed 260-working-day year. The resource-constrained full-network rollout needs review before a construction commitment.

Peak annual government cash: **$922 M**. This includes support required under the low capacity-use case; it is not a funded appropriation.

Chinese export buyer credit is allocated within existing imported budgets for solar equipment, bogies, batteries, windows and doors. City CAPEX excludes manufacturing tooling; the Baghdad-only programme separately funds one plant for Baghdad. IQD bonds assume a proposed Ministry of Finance programme; municipal borrowing authority is pending legal review.

The model includes actual scheduled draws, native-currency principal/interest, fees, revenue ramps, operating/debt support, reserve movements and downside cases. Short bullet bonds have explicit redemptions without assumed refinancing.

See [funding model](engineering/finance/FUNDING-MODEL.md), [monthly cashflow](engineering/finance/funding-monthly-cashflow.csv), [annual cashflow](engineering/finance/funding-annual-cashflow.csv) . This standalone city appraisal is outside the Baghdad-only funding programme.

Annual operating allowance: $144 M; demand remains capacity-led.

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 31 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,478 assets / 7,723 tasks | [`mosul-operations-manifest.json`](operations/mosul-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`mosul.toml`](mosul.toml) | Expanded simulator scenario |
| [`mosul.corridor.geojson`](mosul.corridor.geojson) | GIS corridor and stations |
| [`mosul.design-quality.yaml`](mosul.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh mosul
```
