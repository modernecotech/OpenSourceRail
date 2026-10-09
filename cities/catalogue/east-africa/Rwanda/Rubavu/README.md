# Rubavu — Urban Rail Network

**Country:** RW · **Population:** 250,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Rubavu-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.82 bn (89.2%) of external capital** and **$2.29 bn of external interest**. Capital plus saved interest totals **$4.11 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **10 lines**, including **7 additional residential lines**. **78.7%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **35.627 km to 43.065 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **50 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**10 line-local depots** provide **187 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **187 tram-2car trainsets / 374 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Rubavu rail network on OpenStreetMap](rubavu-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 10 / 50 / 11 |
| Route length | 73.3 km double track |
| Direct transfers / reachable line pairs | 24.4% / 100.0% |
| Residents within 800 m radial station catchments | 183,820 (2020 raster; 60.8% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 187 × 2-car `tram-2car` trainsets (163 peak revenue) |
| Peak network throughput | 96,000 passengers/hour |
| Practical service capacity | 892,800 passenger-trips/day |
| Annual paid-trip planning range | 162.9–260.7 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 11.0 km | 6 | 24 | W Outer ↔ N Mid |
| line-2 | 12.4 km | 10 | 34 | S Mid ↔ NW Outer |
| line-3 | 13.3 km | 9 | 32 | NW Outer ↔ E Mid |
| line-4 |  2.7 km | 2 | 9 | W Inner ↔ SW Inner |
| line-5 |  7.4 km | 5 | 18 | E Mid ↔ S Mid |
| line-6 |  7.1 km | 5 | 18 | S Inner ↔ NW Inner |
| line-7 |  6.4 km | 4 | 16 | E Mid ↔ NE Mid |
| line-8 |  6.8 km | 4 | 17 | N Mid ↔ NE Outer |
| line-9 |  3.8 km | 3 | 11 | S Mid ↔ SE Outer |
| line-10 |  2.2 km | 2 | 8 | S Mid ↔ SE Mid |
| **Total** | **73.3 km** | **50 unique** | **187** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 4,650 one-way journeys / 34,069 train-km/day |
| Annual traction demand | 107.4 GWh |
| Station/depot PV / storage | 59.6 MW / 416.0 MWh |
| Aggregate charging power | 21.0 MW |
| Dedicated solar plant | 2.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-5: 7.4 km / 37 kWh |
| Lowest traversal charging margin | line-7: 14 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $564 M |
| Stations | $244 M |
| Depots | $139 M |
| Rolling stock | $105 M |
| Dedicated solar plant | $1.6 M |
| Residual train control | $3.7 M |
| Charging microgrids | $4.5 M |
| EPC / project services | $74 M |
| **Total city programme** | **$1.14 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $220 M (19.4%) |
| Domestic / local capital | $916 M (80.6%) |
| Annual public construction commitment | $98 M / yr for 7 years |
| Annual post-grace debt service | $80 M / yr |
| External capital saved vs default turnkey sensitivity | $1.82 bn |
| Capital + lifetime external interest saved | $4.11 bn |
| Annual OPEX | $27 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 6 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 479 assets / 2,550 tasks | [`rubavu-operations-manifest.json`](operations/rubavu-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`rubavu.toml`](rubavu.toml) | Expanded simulator scenario |
| [`rubavu.corridor.geojson`](rubavu.corridor.geojson) | GIS corridor and stations |
| [`rubavu.design-quality.yaml`](rubavu.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh rubavu
```
