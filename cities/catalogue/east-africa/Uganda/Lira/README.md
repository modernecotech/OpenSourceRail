# Lira — Urban Rail Network

**Country:** UG · **Population:** 250,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Lira-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.89 bn (89.3%) of external capital** and **$2.37 bn of external interest**. Capital plus saved interest totals **$4.27 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **11 lines**, including **8 additional residential lines**. **70.9%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **33.686 km to 49.793 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **52 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**11 line-local depots** provide **192 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **192 tram-2car trainsets / 384 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Lira rail network on OpenStreetMap](lira-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 11 / 52 / 13 |
| Route length | 77.3 km double track |
| Direct transfers / reachable line pairs | 23.6% / 100.0% |
| Residents within 800 m radial station catchments | 121,259 (2020 raster; 55.6% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 192 × 2-car `tram-2car` trainsets (167 peak revenue) |
| Peak network throughput | 105,600 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 11.8 km | 7 | 26 | W Mid ↔ NE Outer |
| line-2 | 13.3 km | 8 | 29 | E Outer ↔ W Mid |
| line-3 | 13.7 km | 9 | 32 | W Outer ↔ S Outer |
| line-4 |  3.2 km | 3 | 11 | W Inner ↔ N Inner |
| line-5 |  3.6 km | 3 | 11 | W Mid ↔ S Mid |
| line-6 |  8.8 km | 5 | 20 | N Inner ↔ W Mid |
| line-7 |  8.6 km | 6 | 21 | W Mid ↔ S Mid |
| line-8 |  6.6 km | 4 | 15 | NE Mid ↔ N Outer |
| line-9 |  3.6 km | 3 | 11 | NE Mid ↔ E Mid |
| line-10 |  2.1 km | 2 | 8 | S Outer ↔ S Outer |
| line-11 |  2.1 km | 2 | 8 | NE Outer ↔ NE Outer |
| **Total** | **77.3 km** | **52 unique** | **192** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 5,115 one-way journeys / 35,940 train-km/day |
| Annual traction demand | 113.3 GWh |
| Station/depot PV / storage | 64.3 MW / 455.5 MWh |
| Aggregate charging power | 21.0 MW |
| Dedicated solar plant | 0.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 8.8 km / 44 kWh |
| Lowest traversal charging margin | line-6: 17 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $599 M |
| Stations | $236 M |
| Depots | $151 M |
| Rolling stock | $108 M |
| Dedicated solar plant | $361 k |
| Residual train control | $3.9 M |
| Charging microgrids | $4.4 M |
| EPC / project services | $77 M |
| **Total city programme** | **$1.18 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $228 M (19.3%) |
| Domestic / local capital | $951 M (80.7%) |
| Annual public construction commitment | $144 M / yr for 7 years |
| Annual post-grace debt service | $121 M / yr |
| External capital saved vs default turnkey sensitivity | $1.89 bn |
| Capital + lifetime external interest saved | $4.27 bn |
| Annual OPEX | $29 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 7 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 494 assets / 2,620 tasks | [`lira-operations-manifest.json`](operations/lira-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`lira.toml`](lira.toml) | Expanded simulator scenario |
| [`lira.corridor.geojson`](lira.corridor.geojson) | GIS corridor and stations |
| [`lira.design-quality.yaml`](lira.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh lira
```
