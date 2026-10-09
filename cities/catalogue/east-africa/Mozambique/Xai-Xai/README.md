# Xai-Xai — Urban Rail Network

**Country:** MZ · **Population:** 250,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Xai-Xai-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$955 M (89.2%) of external capital** and **$1.23 bn of external interest**. Capital plus saved interest totals **$2.19 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **7 lines**, including **4 additional residential lines**. **63.9%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **21.701 km to 24.681 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **26 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**7 line-local depots** provide **93 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **93 tram-2car trainsets / 186 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Xai-Xai rail network on OpenStreetMap](xai-xai-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 7 / 26 / 5 |
| Route length | 33.0 km double track |
| Direct transfers / reachable line pairs | 33.3% / 100.0% |
| Residents within 800 m radial station catchments | 70,036 (2020 raster; 48.3% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 93 × 2-car `tram-2car` trainsets (79 peak revenue) |
| Peak network throughput | 67,200 passengers/hour |
| Practical service capacity | 624,960 passenger-trips/day |
| Annual paid-trip planning range | 114.1–182.5 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  6.0 km | 4 | 15 | SW Mid ↔ NE Inner |
| line-2 |  6.7 km | 5 | 18 | E Inner ↔ NW Mid |
| line-3 |  4.3 km | 4 | 14 | S Inner ↔ NE Inner |
| line-4 |  2.4 km | 2 | 8 | SW Mid ↔ W Mid |
| line-5 |  4.8 km | 4 | 13 | E Inner ↔ NE Mid |
| line-6 |  5.4 km | 4 | 14 | S Inner ↔ SE Outer |
| line-7 |  3.4 km | 3 | 11 | NW Mid ↔ NW Outer |
| **Total** | **33.0 km** | **26 unique** | **93** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,255 one-way journeys / 15,361 train-km/day |
| Annual traction demand | 48.4 GWh |
| Station/depot PV / storage | 39.5 MW / 287.5 MWh |
| Aggregate charging power | 11.0 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 5.4 km / 27 kWh |
| Lowest traversal charging margin | line-6: 19 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $289 M |
| Stations | $119 M |
| Depots | $92 M |
| Rolling stock | $52 M |
| Residual train control | $1.7 M |
| Charging microgrids | $2.4 M |
| EPC / project services | $39 M |
| **Total city programme** | **$595 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $116 M (19.5%) |
| Domestic / local capital | $479 M (80.5%) |
| Annual public construction commitment | $67 M / yr for 10 years |
| Annual post-grace debt service | $60 M / yr |
| External capital saved vs default turnkey sensitivity | $955 M |
| Capital + lifetime external interest saved | $2.19 bn |
| Annual OPEX | $15 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 2 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 248 assets / 1,282 tasks | [`xai-xai-operations-manifest.json`](operations/xai-xai-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`xai-xai.toml`](xai-xai.toml) | Expanded simulator scenario |
| [`xai-xai.corridor.geojson`](xai-xai.corridor.geojson) | GIS corridor and stations |
| [`xai-xai.design-quality.yaml`](xai-xai.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh xai-xai
```
