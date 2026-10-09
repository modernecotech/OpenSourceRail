# Iringa — Urban Rail Network

**Country:** TZ · **Population:** 250,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Iringa-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.31 bn (89.4%) of external capital** and **$1.64 bn of external interest**. Capital plus saved interest totals **$2.94 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **7 lines**, including **4 additional residential lines**. **77.3%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **27.118 km to 38.893 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **33 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**7 line-local depots** provide **112 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **112 tram-2car trainsets / 224 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Iringa rail network on OpenStreetMap](iringa-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 7 / 33 / 9 |
| Route length | 38.9 km double track |
| Direct transfers / reachable line pairs | 38.1% / 100.0% |
| Residents within 800 m radial station catchments | 126,677 (2020 raster; 64.0% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 112 × 2-car `tram-2car` trainsets (97 peak revenue) |
| Peak network throughput | 67,200 passengers/hour |
| Practical service capacity | 624,960 passenger-trips/day |
| Annual paid-trip planning range | 114.1–182.5 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  7.9 km | 7 | 23 | NE Outer ↔ SW Mid |
| line-2 |  7.6 km | 6 | 20 | S Outer ↔ W Outer |
| line-3 |  4.7 km | 4 | 14 | NW Mid ↔ E Mid |
| line-4 |  2.3 km | 3 | 10 | NE Mid ↔ NE Outer |
| line-5 |  4.2 km | 3 | 12 | SW Mid ↔ SE Outer |
| line-6 |  7.1 km | 6 | 19 | S Mid ↔ W Mid |
| line-7 |  5.1 km | 4 | 14 | N Inner ↔ NE Outer |
| **Total** | **38.9 km** | **33 unique** | **112** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,255 one-way journeys / 18,085 train-km/day |
| Annual traction demand | 57.0 GWh |
| Station/depot PV / storage | 42.5 MW / 292.5 MWh |
| Aggregate charging power | 16.0 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 3.8 km / 21 kWh |
| Lowest traversal charging margin | line-5: 40 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $408 M |
| Stations | $188 M |
| Depots | $94 M |
| Rolling stock | $63 M |
| Residual train control | $1.9 M |
| Charging microgrids | $3.4 M |
| EPC / project services | $53 M |
| **Total city programme** | **$812 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $155 M (19.1%) |
| Domestic / local capital | $657 M (80.9%) |
| Annual public construction commitment | $76 M / yr for 7 years |
| Annual post-grace debt service | $62 M / yr |
| External capital saved vs default turnkey sensitivity | $1.31 bn |
| Capital + lifetime external interest saved | $2.94 bn |
| Annual OPEX | $20 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 3 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 308 assets / 1,594 tasks | [`iringa-operations-manifest.json`](operations/iringa-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`iringa.toml`](iringa.toml) | Expanded simulator scenario |
| [`iringa.corridor.geojson`](iringa.corridor.geojson) | GIS corridor and stations |
| [`iringa.design-quality.yaml`](iringa.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh iringa
```
