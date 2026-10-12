# Waw — Urban Rail Network

**Country:** SS · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Waw-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$499 M (89.4%) of external capital** and **$614 M of external interest**. Capital plus saved interest totals **$1.11 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-12).** The controlled planning inventory contains **3 lines**, including **0 additional residential lines**. **9.9%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **16.705 km to 15.175 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **12 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **45 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **45 tram-2car trainsets / 90 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

**Input discrepancy:** Wau is in South Sudan. The canonical jurisdiction and national aggregation now use SS; the historical slug waw remains an alias. Finance uses an explicitly uncalibrated generic scenario, with SSP currency; Sudan SD/SDG assumptions are excluded. [Evidence](https://www.unmissions.org/en/unmis-0/wau-celebrates-independence-procession-speeches).

## Network

![Waw rail network on OpenStreetMap](waw-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 12 / 1 |
| Route length | 16.8 km double track |
| Direct transfers / reachable line pairs | 33.3% / 33.3% |
| Residents within 800 m radial station catchments | 734 (2020 raster; 6.8% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 45 × 2-car `tram-2car` trainsets (39 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  6.6 km | 3 | 14 | NW Mid ↔ S Mid |
| line-2 |  7.9 km | 5 | 19 | N Outer ↔ S Inner |
| line-3 |  2.3 km | 4 | 12 | SE Inner ↔ NW Inner |
| **Total** | **16.8 km** | **12 unique** | **45** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 7,818 train-km/day |
| Annual traction demand | 24.7 GWh |
| Station/depot PV / storage | 17.7 MW / 124.5 MWh |
| Aggregate charging power | 6.0 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 4.4 km / 24 kWh |
| Lowest traversal charging margin | line-1: 25 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $158 M |
| Stations | $64 M |
| Depots | $40 M |
| Rolling stock | $25 M |
| Residual train control | $841 k |
| Charging microgrids | $1.4 M |
| EPC / project services | $20 M |
| **Total city programme** | **$310 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $59 M (19.1%) |
| Domestic / local capital | $251 M (80.9%) |
| Annual public construction commitment | $27 M / yr for 5 years |
| Annual post-grace debt service | $19 M / yr |
| External capital saved vs default turnkey sensitivity | $499 M |
| Capital + lifetime external interest saved | $1.11 bn |
| Annual OPEX | $12 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 2 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 119 assets / 619 tasks | [`waw-operations-manifest.json`](operations/waw-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`waw.toml`](waw.toml) | Expanded simulator scenario |
| [`waw.corridor.geojson`](waw.corridor.geojson) | GIS corridor and stations |
| [`waw.design-quality.yaml`](waw.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh waw
```
