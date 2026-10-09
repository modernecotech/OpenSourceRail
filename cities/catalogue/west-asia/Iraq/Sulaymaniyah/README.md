# Sulaymaniyah — Urban Rail Network

**Country:** IQ · **Population:** 2,150,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Sulaymaniyah-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$5.29 bn (88.4%) of external capital** and **$6.50 bn of external interest**. Capital plus saved interest totals **$11.79 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **17 lines**, including **13 additional residential lines**. **80.6%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **107.875 km to 144.599 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **122 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**17 line-local depots** provide **337 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **337 metro-4car trainsets / 1348 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Sulaymaniyah rail network on OpenStreetMap](sulaymaniyah-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 17 / 122 / 28 |
| Route length | 182.5 km double track |
| Direct transfers / reachable line pairs | 22.1% / 100.0% |
| Residents within 800 m radial station catchments | 550,618 (2020 raster; 61.0% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 337 × 4-car `metro-4car` trainsets (296 peak revenue) |
| Peak network throughput | 326,400 passengers/hour |
| Practical service capacity | 2,946,240 passenger-trips/day |
| Annual paid-trip planning range | 537.7–860.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 13.5 km | 9 | 32 | W Mid ↔ E Mid |
| line-2 | 12.3 km | 8 | 29 | SE Mid ↔ W Inner |
| line-3 | 27.3 km | 17 | 53 | NE Outer ↔ S Inner |
| line-4 | 53.4 km | 32 | 28 | W Mid ↔ W Mid |
| line-5 |  5.0 km | 4 | 14 | NW Inner ↔ NE Inner |
| line-6 |  5.0 km | 4 | 14 | N Inner ↔ NE Inner |
| line-7 |  6.5 km | 4 | 16 | W Mid ↔ NW Mid |
| line-8 |  7.4 km | 6 | 20 | SE Inner ↔ SE Mid |
| line-9 |  5.4 km | 4 | 15 | E Inner ↔ SE Mid |
| line-10 |  6.0 km | 5 | 15 | S Mid ↔ S Mid |
| line-11 |  8.1 km | 5 | 18 | W Mid ↔ NW Mid |
| line-12 |  2.2 km | 2 | 8 | N Inner ↔ N Inner |
| line-13 |  7.2 km | 5 | 16 | N Mid ↔ N Outer |
| line-14 |  2.8 km | 2 | 9 | W Inner ↔ NW Inner |
| line-15 |  3.3 km | 3 | 11 | SW Inner ↔ SW Mid |
| line-16 | 10.4 km | 7 | 23 | W Mid ↔ W Outer |
| line-17 |  6.6 km | 5 | 16 | S Mid ↔ SE Outer |
| **Total** | **182.5 km** | **122 unique** | **337** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 7,672 one-way journeys / 72,424 train-km/day |
| Annual traction demand | 456.8 GWh |
| Station/depot PV / storage | 110.2 MW / 806.0 MWh |
| Aggregate charging power | 151.5 MW |
| Dedicated solar plant | 215.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 13.3 km / 128 kWh |
| Lowest traversal charging margin | line-13: 71 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.65 bn |
| Stations | $612 M |
| Depots | $264 M |
| Rolling stock | $377 M |
| Dedicated solar plant | $173 M |
| Residual train control | $9.1 M |
| Charging microgrids | $31 M |
| EPC / project services | $206 M |
| **Total city programme** | **$3.32 bn** |

## Iraq funding

Proposed facilities and appropriations remain uncommitted. The conditional ledger calculates government capital and the extra support required for fees, interest, reserves and cash shortfalls; additional support is not a funding commitment.

| Capital source | Planning USD equivalent |
|---|---:|
| bank credit | $315 M |
| chinese export credit | $169 M |
| domestic bonds | $946 M |
| government | $1.89 bn |

The procurement schedule requires **46 calendar months** of capital cash under an assumed 260-working-day year. The resource-constrained full-network rollout needs review before a construction commitment.

Peak annual government cash: **$850 M**. This includes support required under the low capacity-use case; it is not a funded appropriation.

Chinese export buyer credit is allocated within existing imported budgets for solar equipment, bogies, batteries, windows and doors. City CAPEX excludes manufacturing tooling; the Baghdad-only programme separately funds one plant for Baghdad. IQD bonds assume a proposed Ministry of Finance programme; municipal borrowing authority is pending legal review.

The model includes actual scheduled draws, native-currency principal/interest, fees, revenue ramps, operating/debt support, reserve movements and downside cases. Short bullet bonds have explicit redemptions without assumed refinancing.

See [funding model](engineering/finance/FUNDING-MODEL.md), [monthly cashflow](engineering/finance/funding-monthly-cashflow.csv), [annual cashflow](engineering/finance/funding-annual-cashflow.csv) . This standalone city appraisal is outside the Baghdad-only funding programme.

Annual operating allowance: $94 M; demand remains capacity-led.

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 22 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,010 assets / 5,143 tasks | [`sulaymaniyah-operations-manifest.json`](operations/sulaymaniyah-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`sulaymaniyah.toml`](sulaymaniyah.toml) | Expanded simulator scenario |
| [`sulaymaniyah.corridor.geojson`](sulaymaniyah.corridor.geojson) | GIS corridor and stations |
| [`sulaymaniyah.design-quality.yaml`](sulaymaniyah.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh sulaymaniyah
```
