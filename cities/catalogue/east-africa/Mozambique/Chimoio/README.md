# Chimoio — Urban Rail Network

**Country:** MZ · **Population:** 400,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Chimoio-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.82 bn (88.3%) of external capital** and **$2.35 bn of external interest**. Capital plus saved interest totals **$4.17 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **7 lines**, including **5 additional residential lines**. **57.8%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **28.174 km to 54.272 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **42 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**7 line-local depots** provide **210 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **210 light-metro-3car trainsets / 630 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Chimoio rail network on OpenStreetMap](chimoio-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 7 / 42 / 8 |
| Route length | 60.0 km double track |
| Direct transfers / reachable line pairs | 47.6% / 100.0% |
| Residents within 800 m radial station catchments | 185,029 (2020 raster; 44.2% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 210 × 3-car `light-metro-3car` trainsets (186 peak revenue) |
| Peak network throughput | 100,800 passengers/hour |
| Practical service capacity | 937,440 passenger-trips/day |
| Annual paid-trip planning range | 171.1–273.7 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 17.6 km | 11 | 57 | E Outer ↔ SW Outer |
| line-2 | 12.6 km | 10 | 47 | E Outer ↔ W Mid |
| line-3 |  6.2 km | 4 | 23 | SE Inner ↔ NW Inner |
| line-4 |  8.2 km | 6 | 28 | NE Inner ↔ W Mid |
| line-5 |  5.8 km | 4 | 21 | W Mid ↔ W Outer |
| line-6 |  7.4 km | 5 | 24 | W Inner ↔ W Outer |
| line-7 |  2.2 km | 2 | 10 | E Mid ↔ E Mid |
| **Total** | **60.0 km** | **42 unique** | **210** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,255 one-way journeys / 27,893 train-km/day |
| Annual traction demand | 131.9 GWh |
| Station/depot PV / storage | 44.3 MW / 295.5 MWh |
| Aggregate charging power | 19.0 MW |
| Dedicated solar plant | 35.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 5.3 km / 40 kWh |
| Lowest traversal charging margin | line-5: 26 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $548 M |
| Stations | $188 M |
| Depots | $111 M |
| Rolling stock | $189 M |
| Dedicated solar plant | $29 M |
| Residual train control | $3.0 M |
| Charging microgrids | $4.0 M |
| EPC / project services | $73 M |
| **Total city programme** | **$1.15 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $241 M (21.0%) |
| Domestic / local capital | $905 M (79.0%) |
| Annual public construction commitment | $127 M / yr for 10 years |
| Annual post-grace debt service | $115 M / yr |
| External capital saved vs default turnkey sensitivity | $1.82 bn |
| Capital + lifetime external interest saved | $4.17 bn |
| Annual OPEX | $29 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 12 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 463 assets / 2,641 tasks | [`chimoio-operations-manifest.json`](operations/chimoio-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`chimoio.toml`](chimoio.toml) | Expanded simulator scenario |
| [`chimoio.corridor.geojson`](chimoio.corridor.geojson) | GIS corridor and stations |
| [`chimoio.design-quality.yaml`](chimoio.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh chimoio
```
