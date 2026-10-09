# Fallujah — Urban Rail Network

**Country:** IQ · **Population:** 360,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Fallujah-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.71 bn (88.5%) of external capital** and **$3.34 bn of external interest**. Capital plus saved interest totals **$6.05 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **12 lines**, including **9 additional residential lines**. **63.7%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **47.537 km to 62.738 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **63 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**12 line-local depots** provide **316 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **316 light-metro-3car trainsets / 948 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Fallujah rail network on OpenStreetMap](fallujah-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 12 / 63 / 14 |
| Route length | 88.1 km double track |
| Direct transfers / reachable line pairs | 28.8% / 100.0% |
| Residents within 800 m radial station catchments | 98,821 (2020 raster; 51.8% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 316 × 3-car `light-metro-3car` trainsets (279 peak revenue) |
| Peak network throughput | 172,800 passengers/hour |
| Practical service capacity | 1,607,040 passenger-trips/day |
| Annual paid-trip planning range | 293.3–469.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 18.0 km | 12 | 59 | NW Outer ↔ SE Mid |
| line-2 | 11.3 km | 8 | 37 | W Mid ↔ E Mid |
| line-3 | 14.9 km | 10 | 53 | SE Outer ↔ W Inner |
| line-4 |  2.8 km | 2 | 11 | NE Inner ↔ N Inner |
| line-5 |  5.2 km | 5 | 20 | W Inner ↔ W Mid |
| line-6 |  2.6 km | 2 | 11 | NW Outer ↔ NW Outer |
| line-7 |  6.3 km | 4 | 24 | E Mid ↔ NE Outer |
| line-8 |  7.0 km | 5 | 24 | SE Inner ↔ NW Mid |
| line-9 |  8.7 km | 6 | 30 | W Inner ↔ SW Outer |
| line-10 |  7.1 km | 5 | 27 | E Mid ↔ E Outer |
| line-11 |  2.2 km | 2 | 10 | NW Inner ↔ SW Inner |
| line-12 |  2.1 km | 2 | 10 | NW Inner ↔ NW Inner |
| **Total** | **88.1 km** | **63 unique** | **316** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 5,580 one-way journeys / 40,976 train-km/day |
| Annual traction demand | 193.8 GWh |
| Station/depot PV / storage | 71.7 MW / 499.5 MWh |
| Aggregate charging power | 25.5 MW |
| Dedicated solar plant | 19.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-10: 7.1 km / 57 kWh |
| Lowest traversal charging margin | line-7: 18 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $801 M |
| Stations | $297 M |
| Depots | $186 M |
| Rolling stock | $284 M |
| Dedicated solar plant | $15 M |
| Residual train control | $4.4 M |
| Charging microgrids | $5.3 M |
| EPC / project services | $110 M |
| **Total city programme** | **$1.70 bn** |

## Iraq funding

Proposed facilities and appropriations remain uncommitted. The conditional ledger calculates government capital and the extra support required for fees, interest, reserves and cash shortfalls; additional support is not a funding commitment.

| Capital source | Planning USD equivalent |
|---|---:|
| bank credit | $163 M |
| chinese export credit | $79 M |
| domestic bonds | $488 M |
| government | $975 M |

The procurement schedule requires **41 calendar months** of capital cash under an assumed 260-working-day year. The resource-constrained full-network rollout needs review before a construction commitment.

Peak annual government cash: **$565 M**. This includes support required under the low capacity-use case; it is not a funded appropriation.

Chinese export buyer credit is allocated within existing imported budgets for solar equipment, bogies, batteries, windows and doors. City CAPEX excludes manufacturing tooling; the Baghdad-only programme separately funds one plant for Baghdad. IQD bonds assume a proposed Ministry of Finance programme; municipal borrowing authority is pending legal review.

The model includes actual scheduled draws, native-currency principal/interest, fees, revenue ramps, operating/debt support, reserve movements and downside cases. Short bullet bonds have explicit redemptions without assumed refinancing.

See [funding model](engineering/finance/FUNDING-MODEL.md), [monthly cashflow](engineering/finance/funding-monthly-cashflow.csv), [annual cashflow](engineering/finance/funding-annual-cashflow.csv) . This standalone city appraisal is outside the Baghdad-only funding programme.

Annual operating allowance: $54 M; demand remains capacity-led.

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 7 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 692 assets / 3,942 tasks | [`fallujah-operations-manifest.json`](operations/fallujah-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`fallujah.toml`](fallujah.toml) | Expanded simulator scenario |
| [`fallujah.corridor.geojson`](fallujah.corridor.geojson) | GIS corridor and stations |
| [`fallujah.design-quality.yaml`](fallujah.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh fallujah
```
