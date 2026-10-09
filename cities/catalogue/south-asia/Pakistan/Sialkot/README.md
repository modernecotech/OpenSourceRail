# Sialkot — Urban Rail Network

**Country:** PK · **Population:** 750,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Sialkot-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.15 bn (89.1%) of external capital** and **$5.20 bn of external interest**. Capital plus saved interest totals **$9.36 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **17 lines**, including **14 additional residential lines**. **65.9%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **46.692 km to 83.099 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **73 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**17 line-local depots** provide **397 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **397 light-metro-3car trainsets / 1191 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Sialkot rail network on OpenStreetMap](sialkot-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 17 / 73 / 17 |
| Route length | 107.1 km double track |
| Direct transfers / reachable line pairs | 15.4% / 100.0% |
| Residents within 800 m radial station catchments | 973,397 (2020 raster; 50.8% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 397 × 3-car `light-metro-3car` trainsets (349 peak revenue) |
| Peak network throughput | 244,800 passengers/hour |
| Practical service capacity | 2,276,640 passenger-trips/day |
| Annual paid-trip planning range | 415.5–664.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 17.5 km | 10 | 59 | NE Mid ↔ S Outer |
| line-2 | 22.7 km | 14 | 80 | SE Outer ↔ NW Outer |
| line-3 | 13.5 km | 9 | 48 | NE Mid ↔ W Mid |
| line-4 |  3.1 km | 3 | 14 | NE Inner ↔ E Inner |
| line-5 |  3.1 km | 3 | 14 | NW Inner ↔ N Inner |
| line-6 |  3.2 km | 2 | 12 | W Inner ↔ W Inner |
| line-7 |  2.9 km | 2 | 11 | S Inner ↔ SE Inner |
| line-8 |  2.1 km | 2 | 10 | S Mid ↔ SW Mid |
| line-9 |  4.8 km | 3 | 17 | SE Inner ↔ E Mid |
| line-10 |  5.2 km | 4 | 19 | NE Mid ↔ N Outer |
| line-11 |  2.1 km | 2 | 10 | W Mid ↔ W Mid |
| line-12 |  5.0 km | 4 | 19 | NE Mid ↔ NE Outer |
| line-13 |  6.2 km | 4 | 24 | S Outer ↔ SW Outer |
| line-14 |  4.9 km | 3 | 18 | W Mid ↔ W Outer |
| line-15 |  4.3 km | 3 | 16 | NE Mid ↔ E Mid |
| line-16 |  2.4 km | 2 | 10 | NW Mid ↔ NW Mid |
| line-17 |  4.3 km | 3 | 16 | NE Mid ↔ NE Outer |
| **Total** | **107.1 km** | **73 unique** | **397** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 7,905 one-way journeys / 49,818 train-km/day |
| Annual traction demand | 235.7 GWh |
| Station/depot PV / storage | 98.2 MW / 702.0 MWh |
| Aggregate charging power | 30.5 MW |
| Dedicated solar plant | 10.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 7.2 km / 58 kWh |
| Lowest traversal charging margin | line-15: 11 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.46 bn |
| Stations | $328 M |
| Depots | $254 M |
| Rolling stock | $357 M |
| Dedicated solar plant | $8.7 M |
| Residual train control | $5.4 M |
| Charging microgrids | $6.2 M |
| EPC / project services | $169 M |
| **Total city programme** | **$2.59 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $508 M (19.6%) |
| Domestic / local capital | $2.08 bn (80.4%) |
| Annual public construction commitment | $357 M / yr for 7 years |
| Annual post-grace debt service | $306 M / yr |
| External capital saved vs default turnkey sensitivity | $4.15 bn |
| Capital + lifetime external interest saved | $9.36 bn |
| Annual OPEX | $64 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 7 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 845 assets / 4,848 tasks | [`sialkot-operations-manifest.json`](operations/sialkot-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`sialkot.toml`](sialkot.toml) | Expanded simulator scenario |
| [`sialkot.corridor.geojson`](sialkot.corridor.geojson) | GIS corridor and stations |
| [`sialkot.design-quality.yaml`](sialkot.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh sialkot
```
