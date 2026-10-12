# Jinja — Urban Rail Network

**Country:** UG · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Jinja-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.50 bn (89.5%) of external capital** and **$1.88 bn of external interest**. Capital plus saved interest totals **$3.38 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-12).** The controlled planning inventory contains **4 lines**, including **1 additional residential lines**. **36.7%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **32.128 km to 42.423 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **31 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**4 line-local depots** provide **121 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **121 tram-2car trainsets / 242 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Jinja rail network on OpenStreetMap](jinja-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 4 / 31 / 8 |
| Route length | 56.1 km double track |
| Direct transfers / reachable line pairs | 66.7% / 100.0% |
| Residents within 800 m radial station catchments | 92,904 (2020 raster; 27.3% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 121 × 2-car `tram-2car` trainsets (109 peak revenue) |
| Peak network throughput | 38,400 passengers/hour |
| Practical service capacity | 357,120 passenger-trips/day |
| Annual paid-trip planning range | 65.2–104.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 15.2 km | 8 | 32 | NE Outer ↔ S Inner |
| line-2 | 19.9 km | 11 | 43 | SE Mid ↔ NW Mid |
| line-3 | 12.8 km | 7 | 27 | SW Outer ↔ NE Inner |
| line-4 |  8.2 km | 5 | 19 | NW Inner ↔ W Mid |
| **Total** | **56.1 km** | **31 unique** | **121** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,860 one-way journeys / 26,097 train-km/day |
| Annual traction demand | 82.3 GWh |
| Station/depot PV / storage | 27.8 MW / 173.0 MWh |
| Aggregate charging power | 15.0 MW |
| Dedicated solar plant | 22.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 7.3 km / 37 kWh |
| Lowest traversal charging margin | line-3: 44 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $516 M |
| Stations | $202 M |
| Depots | $61 M |
| Rolling stock | $68 M |
| Dedicated solar plant | $18 M |
| Residual train control | $2.8 M |
| Charging microgrids | $3.1 M |
| EPC / project services | $60 M |
| **Total city programme** | **$931 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $176 M (19.0%) |
| Domestic / local capital | $754 M (81.0%) |
| Annual public construction commitment | $114 M / yr for 7 years |
| Annual post-grace debt service | $96 M / yr |
| External capital saved vs default turnkey sensitivity | $1.50 bn |
| Capital + lifetime external interest saved | $3.38 bn |
| Annual OPEX | $21 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 2 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 303 assets / 1,650 tasks | [`jinja-operations-manifest.json`](operations/jinja-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`jinja.toml`](jinja.toml) | Expanded simulator scenario |
| [`jinja.corridor.geojson`](jinja.corridor.geojson) | GIS corridor and stations |
| [`jinja.design-quality.yaml`](jinja.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh jinja
```
