# Machakos — Urban Rail Network

**Country:** KE · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Machakos-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.32 bn (89.3%) of external capital** and **$1.65 bn of external interest**. Capital plus saved interest totals **$2.97 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **8 lines**, including **5 additional residential lines**. **56.7%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **24.802 km to 39.263 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **34 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**8 line-local depots** provide **123 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **123 tram-2car trainsets / 246 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Machakos rail network on OpenStreetMap](machakos-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 8 / 34 / 9 |
| Route length | 46.8 km double track |
| Direct transfers / reachable line pairs | 39.3% / 100.0% |
| Residents within 800 m radial station catchments | 74,795 (2020 raster; 43.5% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 123 × 2-car `tram-2car` trainsets (106 peak revenue) |
| Peak network throughput | 76,800 passengers/hour |
| Practical service capacity | 714,240 passenger-trips/day |
| Annual paid-trip planning range | 130.3–208.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 10.6 km | 7 | 26 | N Outer ↔ S Mid |
| line-2 |  6.8 km | 5 | 18 | SE Mid ↔ SW Mid |
| line-3 |  6.2 km | 4 | 15 | N Inner ↔ SW Mid |
| line-4 |  2.8 km | 2 | 9 | S Inner ↔ SE Inner |
| line-5 |  3.4 km | 3 | 11 | N Mid ↔ NE Inner |
| line-6 |  7.9 km | 6 | 19 | N Inner ↔ NE Outer |
| line-7 |  6.0 km | 4 | 15 | SW Mid ↔ SE Mid |
| line-8 |  3.1 km | 3 | 10 | W Inner ↔ W Mid |
| **Total** | **46.8 km** | **34 unique** | **123** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,720 one-way journeys / 21,785 train-km/day |
| Annual traction demand | 68.7 GWh |
| Station/depot PV / storage | 46.6 MW / 331.0 MWh |
| Aggregate charging power | 15.0 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 7.3 km / 41 kWh |
| Lowest traversal charging margin | line-6: 21 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $403 M |
| Stations | $181 M |
| Depots | $108 M |
| Rolling stock | $69 M |
| Residual train control | $2.3 M |
| Charging microgrids | $3.1 M |
| EPC / project services | $54 M |
| **Total city programme** | **$820 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $158 M (19.3%) |
| Domestic / local capital | $662 M (80.7%) |
| Annual public construction commitment | $87 M / yr for 7 years |
| Annual post-grace debt service | $72 M / yr |
| External capital saved vs default turnkey sensitivity | $1.32 bn |
| Capital + lifetime external interest saved | $2.97 bn |
| Annual OPEX | $22 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 1 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 325 assets / 1,698 tasks | [`machakos-operations-manifest.json`](operations/machakos-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`machakos.toml`](machakos.toml) | Expanded simulator scenario |
| [`machakos.corridor.geojson`](machakos.corridor.geojson) | GIS corridor and stations |
| [`machakos.design-quality.yaml`](machakos.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh machakos
```
