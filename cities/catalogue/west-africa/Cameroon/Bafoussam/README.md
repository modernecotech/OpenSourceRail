# Bafoussam — Urban Rail Network

**Country:** CM · **Population:** 600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Bafoussam-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.48 bn (88.2%) of external capital** and **$4.36 bn of external interest**. Capital plus saved interest totals **$7.85 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **15 lines**, including **12 additional residential lines**. **58.9%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **56.221 km to 83.319 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **80 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**15 line-local depots** provide **416 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **416 light-metro-3car trainsets / 1248 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Bafoussam rail network on OpenStreetMap](bafoussam-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 15 / 80 / 15 |
| Route length | 117.7 km double track |
| Direct transfers / reachable line pairs | 20.0% / 100.0% |
| Residents within 800 m radial station catchments | 165,198 (2020 raster; 43.4% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 416 × 3-car `light-metro-3car` trainsets (369 peak revenue) |
| Peak network throughput | 216,000 passengers/hour |
| Practical service capacity | 2,008,800 passenger-trips/day |
| Annual paid-trip planning range | 366.6–586.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 17.0 km | 10 | 58 | N Inner ↔ S Outer |
| line-2 | 19.6 km | 14 | 63 | NW Outer ↔ E Mid |
| line-3 | 22.7 km | 14 | 76 | E Mid ↔ SW Outer |
| line-4 |  3.1 km | 2 | 12 | N Inner ↔ W Inner |
| line-5 |  2.6 km | 2 | 11 | NW Mid ↔ W Inner |
| line-6 |  4.9 km | 4 | 19 | NW Mid ↔ NW Outer |
| line-7 |  5.2 km | 4 | 19 | E Mid ↔ NE Mid |
| line-8 |  2.1 km | 2 | 10 | SE Inner ↔ SW Inner |
| line-9 |  5.6 km | 4 | 21 | E Mid ↔ E Outer |
| line-10 | 11.0 km | 7 | 39 | N Inner ↔ NW Mid |
| line-11 |  2.1 km | 2 | 10 | E Inner ↔ NE Inner |
| line-12 | 11.0 km | 7 | 36 | NW Inner ↔ SE Inner |
| line-13 |  4.4 km | 3 | 16 | NW Mid ↔ W Mid |
| line-14 |  2.3 km | 2 | 10 | E Inner ↔ NE Mid |
| line-15 |  4.2 km | 3 | 16 | NW Inner ↔ N Inner |
| **Total** | **117.7 km** | **80 unique** | **416** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 6,975 one-way journeys / 54,738 train-km/day |
| Annual traction demand | 258.9 GWh |
| Station/depot PV / storage | 88.5 MW / 622.5 MWh |
| Aggregate charging power | 30.0 MW |
| Dedicated solar plant | 68.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 10.7 km / 80 kWh |
| Lowest traversal charging margin | line-13: 13 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.03 bn |
| Stations | $350 M |
| Depots | $234 M |
| Rolling stock | $374 M |
| Dedicated solar plant | $55 M |
| Residual train control | $5.9 M |
| Charging microgrids | $6.2 M |
| EPC / project services | $140 M |
| **Total city programme** | **$2.19 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $465 M (21.2%) |
| Domestic / local capital | $1.73 bn (78.8%) |
| Annual public construction commitment | $188 M / yr for 7 years |
| Annual post-grace debt service | $153 M / yr |
| External capital saved vs default turnkey sensitivity | $3.48 bn |
| Capital + lifetime external interest saved | $7.85 bn |
| Annual OPEX | $58 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 9 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 890 assets / 5,122 tasks | [`bafoussam-operations-manifest.json`](operations/bafoussam-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`bafoussam.toml`](bafoussam.toml) | Expanded simulator scenario |
| [`bafoussam.corridor.geojson`](bafoussam.corridor.geojson) | GIS corridor and stations |
| [`bafoussam.design-quality.yaml`](bafoussam.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh bafoussam
```
