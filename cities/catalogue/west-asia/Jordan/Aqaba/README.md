# Aqaba — Urban Rail Network

**Country:** JO · **Population:** 250,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Aqaba-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.10 bn (89.4%) of external capital** and **$1.36 bn of external interest**. Capital plus saved interest totals **$2.46 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **5 lines**, including **2 additional residential lines**. **79.5%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **28.364 km to 32.640 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **28 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**5 line-local depots** provide **104 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **104 tram-2car trainsets / 208 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Aqaba rail network on OpenStreetMap](aqaba-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 5 / 28 / 7 |
| Route length | 42.4 km double track |
| Direct transfers / reachable line pairs | 60.0% / 100.0% |
| Residents within 800 m radial station catchments | 51,145 (2020 raster; 62.5% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 104 × 2-car `tram-2car` trainsets (92 peak revenue) |
| Peak network throughput | 48,000 passengers/hour |
| Practical service capacity | 446,400 passenger-trips/day |
| Annual paid-trip planning range | 81.5–130.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 11.6 km | 7 | 27 | W Outer ↔ E Outer |
| line-2 |  7.5 km | 5 | 18 | S Inner ↔ NE Mid |
| line-3 | 13.3 km | 9 | 32 | SE Inner ↔ W Outer |
| line-4 |  3.3 km | 3 | 11 | NE Mid ↔ NE Inner |
| line-5 |  6.6 km | 4 | 16 | S Inner ↔ S Outer |
| **Total** | **42.4 km** | **28 unique** | **104** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,325 one-way journeys / 19,710 train-km/day |
| Annual traction demand | 62.2 GWh |
| Station/depot PV / storage | 31.9 MW / 211.5 MWh |
| Aggregate charging power | 14.0 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 3.1 km / 16 kWh |
| Lowest traversal charging margin | line-5: 43 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $358 M |
| Stations | $150 M |
| Depots | $71 M |
| Rolling stock | $58 M |
| Residual train control | $2.1 M |
| Charging microgrids | $3.0 M |
| EPC / project services | $45 M |
| **Total city programme** | **$686 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $131 M (19.0%) |
| Domestic / local capital | $556 M (81.0%) |
| Annual public construction commitment | $61 M / yr for 5 years |
| Annual post-grace debt service | $44 M / yr |
| External capital saved vs default turnkey sensitivity | $1.10 bn |
| Capital + lifetime external interest saved | $2.46 bn |
| Annual OPEX | $24 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 6 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 271 assets / 1,441 tasks | [`aqaba-operations-manifest.json`](operations/aqaba-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`aqaba.toml`](aqaba.toml) | Expanded simulator scenario |
| [`aqaba.corridor.geojson`](aqaba.corridor.geojson) | GIS corridor and stations |
| [`aqaba.design-quality.yaml`](aqaba.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh aqaba
```
