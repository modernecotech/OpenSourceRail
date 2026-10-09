# Sayun — Urban Rail Network

**Country:** YE · **Population:** 200,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Sayun-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.12 bn (89.3%) of external capital** and **$1.45 bn of external interest**. Capital plus saved interest totals **$2.57 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **6 lines**, including **3 additional residential lines**. **83.2%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **21.788 km to 31.190 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **28 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **100 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **100 tram-2car trainsets / 200 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Sayun rail network on OpenStreetMap](sayun-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 28 / 8 |
| Route length | 35.7 km double track |
| Direct transfers / reachable line pairs | 46.7% / 100.0% |
| Residents within 800 m radial station catchments | 86,166 (2020 raster; 65.6% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 100 × 2-car `tram-2car` trainsets (87 peak revenue) |
| Peak network throughput | 57,600 passengers/hour |
| Practical service capacity | 535,680 passenger-trips/day |
| Annual paid-trip planning range | 97.8–156.4 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 13.1 km | 8 | 30 | NE Outer ↔ W Outer |
| line-2 |  3.7 km | 3 | 11 | S Inner ↔ N Mid |
| line-3 |  4.2 km | 4 | 14 | SE Mid ↔ NE Mid |
| line-4 |  4.4 km | 4 | 14 | E Inner ↔ NE Mid |
| line-5 |  6.6 km | 5 | 18 | W Mid ↔ NW Inner |
| line-6 |  3.7 km | 4 | 13 | W Mid ↔ S Mid |
| **Total** | **35.7 km** | **28 unique** | **100** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,790 one-way journeys / 16,594 train-km/day |
| Annual traction demand | 52.3 GWh |
| Station/depot PV / storage | 36.6 MW / 251.0 MWh |
| Aggregate charging power | 14.0 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 3.2 km / 17 kWh |
| Lowest traversal charging margin | line-2: 44 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $329 M |
| Stations | $181 M |
| Depots | $81 M |
| Rolling stock | $56 M |
| Residual train control | $1.8 M |
| Charging microgrids | $3.0 M |
| EPC / project services | $46 M |
| **Total city programme** | **$698 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $134 M (19.3%) |
| Domestic / local capital | $563 M (80.7%) |
| Annual public construction commitment | $98 M / yr for 10 years |
| Annual post-grace debt service | $90 M / yr |
| External capital saved vs default turnkey sensitivity | $1.12 bn |
| Capital + lifetime external interest saved | $2.57 bn |
| Annual OPEX | $16 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 1 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 268 assets / 1,401 tasks | [`sayun-operations-manifest.json`](operations/sayun-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`sayun.toml`](sayun.toml) | Expanded simulator scenario |
| [`sayun.corridor.geojson`](sayun.corridor.geojson) | GIS corridor and stations |
| [`sayun.design-quality.yaml`](sayun.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh sayun
```
