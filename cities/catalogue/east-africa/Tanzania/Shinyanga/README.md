# Shinyanga — Urban Rail Network

**Country:** TZ · **Population:** 250,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Shinyanga-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$827 M (89.6%) of external capital** and **$1.04 bn of external interest**. Capital plus saved interest totals **$1.86 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-12).** The controlled planning inventory contains **4 lines**, including **1 additional residential lines**. **43.5%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **28.738 km to 27.642 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **15 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**4 line-local depots** provide **77 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **77 tram-2car trainsets / 154 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Shinyanga rail network on OpenStreetMap](shinyanga-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 4 / 15 / 2 |
| Route length | 35.8 km double track |
| Direct transfers / reachable line pairs | 33.3% / 50.0% |
| Residents within 800 m radial station catchments | 46,640 (2020 raster; 32.0% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 77 × 2-car `tram-2car` trainsets (68 peak revenue) |
| Peak network throughput | 38,400 passengers/hour |
| Practical service capacity | 357,120 passenger-trips/day |
| Annual paid-trip planning range | 65.2–104.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 15.9 km | 6 | 32 | NE Outer ↔ SW Mid |
| line-2 |  7.8 km | 4 | 17 | W Mid ↔ S Inner |
| line-3 |  6.7 km | 2 | 15 | SE Inner ↔ S Outer |
| line-4 |  5.3 km | 3 | 13 | W Inner ↔ E Inner |
| **Total** | **35.8 km** | **15 unique** | **77** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,860 one-way journeys / 16,628 train-km/day |
| Annual traction demand | 52.4 GWh |
| Station/depot PV / storage | 23.0 MW / 165.0 MWh |
| Aggregate charging power | 7.0 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 7.0 km / 39 kWh |
| Lowest traversal charging margin | line-3: 16 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $308 M |
| Stations | $69 M |
| Depots | $56 M |
| Rolling stock | $43 M |
| Residual train control | $1.8 M |
| Charging microgrids | $1.6 M |
| EPC / project services | $34 M |
| **Total city programme** | **$512 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $96 M (18.6%) |
| Domestic / local capital | $417 M (81.4%) |
| Annual public construction commitment | $48 M / yr for 7 years |
| Annual post-grace debt service | $39 M / yr |
| External capital saved vs default turnkey sensitivity | $827 M |
| Capital + lifetime external interest saved | $1.86 bn |
| Annual OPEX | $13 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 3 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 172 assets / 959 tasks | [`shinyanga-operations-manifest.json`](operations/shinyanga-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`shinyanga.toml`](shinyanga.toml) | Expanded simulator scenario |
| [`shinyanga.corridor.geojson`](shinyanga.corridor.geojson) | GIS corridor and stations |
| [`shinyanga.design-quality.yaml`](shinyanga.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh shinyanga
```
