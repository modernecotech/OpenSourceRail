# Jaffna — Urban Rail Network

**Country:** LK · **Population:** 600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Jaffna-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.69 bn (88.1%) of external capital** and **$3.37 bn of external interest**. Capital plus saved interest totals **$6.06 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **12 lines**, including **9 additional residential lines**. **74.4%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **41.480 km to 62.802 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **65 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**12 line-local depots** provide **329 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **329 light-metro-3car trainsets / 987 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Jaffna rail network on OpenStreetMap](jaffna-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 12 / 65 / 16 |
| Route length | 91.8 km double track |
| Direct transfers / reachable line pairs | 27.3% / 100.0% |
| Residents within 800 m radial station catchments | 187,795 (2020 raster; 58.4% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 329 × 3-car `light-metro-3car` trainsets (293 peak revenue) |
| Peak network throughput | 172,800 passengers/hour |
| Practical service capacity | 1,607,040 passenger-trips/day |
| Annual paid-trip planning range | 293.3–469.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 11.0 km | 9 | 39 | S Mid ↔ N Mid |
| line-2 | 19.8 km | 11 | 63 | SE Outer ↔ W Outer |
| line-3 | 16.0 km | 11 | 57 | NE Outer ↔ S Mid |
| line-4 |  4.8 km | 4 | 18 | SE Inner ↔ SW Mid |
| line-5 |  8.6 km | 5 | 28 | S Mid ↔ NW Inner |
| line-6 |  3.3 km | 3 | 14 | N Mid ↔ NE Inner |
| line-7 |  4.4 km | 3 | 17 | W Outer ↔ NW Outer |
| line-8 |  4.6 km | 4 | 18 | W Mid ↔ NW Inner |
| line-9 |  3.3 km | 3 | 14 | N Mid ↔ NE Mid |
| line-10 |  3.6 km | 3 | 14 | SE Mid ↔ SE Outer |
| line-11 |  3.9 km | 3 | 15 | SE Inner ↔ E Mid |
| line-12 |  8.5 km | 6 | 32 | W Mid ↔ N Mid |
| **Total** | **91.8 km** | **65 unique** | **329** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 5,580 one-way journeys / 42,692 train-km/day |
| Annual traction demand | 201.9 GWh |
| Station/depot PV / storage | 72.0 MW / 500.0 MWh |
| Aggregate charging power | 26.0 MW |
| Dedicated solar plant | 49.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-12: 8.5 km / 63 kWh |
| Lowest traversal charging margin | line-7: 21 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $740 M |
| Stations | $315 M |
| Depots | $186 M |
| Rolling stock | $296 M |
| Dedicated solar plant | $40 M |
| Residual train control | $4.6 M |
| Charging microgrids | $5.4 M |
| EPC / project services | $108 M |
| **Total city programme** | **$1.70 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $363 M (21.4%) |
| Domestic / local capital | $1.33 bn (78.6%) |
| Annual public construction commitment | $198 M / yr for 7 years |
| Annual post-grace debt service | $167 M / yr |
| External capital saved vs default turnkey sensitivity | $2.69 bn |
| Capital + lifetime external interest saved | $6.06 bn |
| Annual OPEX | $48 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 6 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 716 assets / 4,093 tasks | [`jaffna-operations-manifest.json`](operations/jaffna-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`jaffna.toml`](jaffna.toml) | Expanded simulator scenario |
| [`jaffna.corridor.geojson`](jaffna.corridor.geojson) | GIS corridor and stations |
| [`jaffna.design-quality.yaml`](jaffna.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh jaffna
```
