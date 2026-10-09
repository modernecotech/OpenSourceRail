# Fort-Portal — Urban Rail Network

**Country:** UG · **Population:** 200,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Fort-Portal-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.52 bn (89.1%) of external capital** and **$1.91 bn of external interest**. Capital plus saved interest totals **$3.44 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **10 lines**, including **7 additional residential lines**. **57.6%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **32.031 km to 40.455 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **41 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**10 line-local depots** provide **150 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **150 tram-2car trainsets / 300 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Fort-Portal rail network on OpenStreetMap](fort-portal-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 10 / 41 / 11 |
| Route length | 55.8 km double track |
| Direct transfers / reachable line pairs | 26.7% / 100.0% |
| Residents within 800 m radial station catchments | 67,084 (2020 raster; 44.5% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 150 × 2-car `tram-2car` trainsets (128 peak revenue) |
| Peak network throughput | 96,000 passengers/hour |
| Practical service capacity | 892,800 passenger-trips/day |
| Annual paid-trip planning range | 162.9–260.7 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  9.3 km | 6 | 23 | SE Mid ↔ NW Mid |
| line-2 |  6.7 km | 6 | 19 | NE Mid ↔ S Mid |
| line-3 | 12.8 km | 9 | 31 | E Outer ↔ W Mid |
| line-4 |  2.6 km | 3 | 10 | NW Inner ↔ N Inner |
| line-5 |  6.6 km | 4 | 15 | NW Inner ↔ W Outer |
| line-6 |  4.8 km | 3 | 12 | NW Inner ↔ NE Mid |
| line-7 |  2.2 km | 2 | 8 | E Mid ↔ E Mid |
| line-8 |  5.7 km | 4 | 15 | S Mid ↔ SW Outer |
| line-9 |  2.3 km | 2 | 8 | S Inner ↔ SE Mid |
| line-10 |  2.8 km | 2 | 9 | NW Inner ↔ S Inner |
| **Total** | **55.8 km** | **41 unique** | **150** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 4,650 one-way journeys / 25,947 train-km/day |
| Annual traction demand | 81.8 GWh |
| Station/depot PV / storage | 58.1 MW / 413.5 MWh |
| Aggregate charging power | 18.5 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-8: 5.7 km / 28 kWh |
| Lowest traversal charging margin | line-8: 18 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $444 M |
| Stations | $218 M |
| Depots | $135 M |
| Rolling stock | $84 M |
| Residual train control | $2.8 M |
| Charging microgrids | $3.9 M |
| EPC / project services | $62 M |
| **Total city programme** | **$950 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $186 M (19.5%) |
| Domestic / local capital | $765 M (80.5%) |
| Annual public construction commitment | $116 M / yr for 7 years |
| Annual post-grace debt service | $98 M / yr |
| External capital saved vs default turnkey sensitivity | $1.52 bn |
| Capital + lifetime external interest saved | $3.44 bn |
| Annual OPEX | $23 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 2 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 395 assets / 2,065 tasks | [`fort-portal-operations-manifest.json`](operations/fort-portal-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`fort-portal.toml`](fort-portal.toml) | Expanded simulator scenario |
| [`fort-portal.corridor.geojson`](fort-portal.corridor.geojson) | GIS corridor and stations |
| [`fort-portal.design-quality.yaml`](fort-portal.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh fort-portal
```
