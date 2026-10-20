<!-- osr-maglev-primary:start -->
> **Primary v0.5 ferrite-maglev planning:** [Open the current city planning package](engineering/maglev/README.md). Formation, duty, fleet, charging, depot quantities and partial cost allowances are recomputed; physical acceptance remains open.
>
> The material below this notice is the retained v0.4 wheel/rail comparator. Its costs, fleet, geometry and acceptance do not transfer to maglev.
<!-- osr-maglev-primary:end -->

# Karachi — Urban Rail Network

**Country:** PK · **Population:** 20,300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Karachi-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$16.10 bn (88.0%) of external capital** and **$20.18 bn of external interest**. Capital plus saved interest totals **$36.28 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-12).** The controlled planning inventory contains **14 lines**, including **5 additional residential lines**. **44.8%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **366.727 km to 473.389 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **242 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**14 line-local depots** provide **921 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **921 metro-6car trainsets / 5526 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Karachi rail network on OpenStreetMap](karachi-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 14 / 242 / 58 |
| Route length | 565.5 km double track |
| Direct transfers / reachable line pairs | 45.1% / 100.0% |
| Residents within 800 m radial station catchments | 4,999,890 (2020 raster; 31.5% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 921 × 6-car `metro-6car` trainsets (831 peak revenue) |
| Peak network throughput | 403,200 passengers/hour |
| Practical service capacity | 3,615,840 passenger-trips/day |
| Annual paid-trip planning range | 659.9–1055.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 51.6 km | 29 | 116 | E Outer ↔ W Mid |
| line-2 | 34.9 km | 17 | 73 | N Outer ↔ SW Mid |
| line-3 | 46.5 km | 16 | 85 | W Outer ↔ SE Outer |
| line-4 | 41.4 km | 18 | 82 | E Mid ↔ NW Mid |
| line-5 | 50.7 km | 15 | 95 | NE Outer ↔ S Mid |
| line-6 | 45.8 km | 29 | 111 | N Outer ↔ SE Mid |
| line-7 | 41.0 km | 17 | 76 | NW Outer ↔ S Mid |
| line-8 | 60.0 km | 27 | 118 | NE Outer ↔ SW Mid |
| line-9 | 146.0 km | 56 | 68 | NW Mid ↔ NW Mid |
| line-10 |  7.5 km | 3 | 16 | NE Inner ↔ N Mid |
| line-11 | 12.3 km | 5 | 26 | NE Mid ↔ N Inner |
| line-12 | 11.5 km | 4 | 21 | SE Mid ↔ SE Inner |
| line-13 |  9.7 km | 3 | 19 | NW Mid ↔ N Mid |
| line-14 |  6.5 km | 3 | 15 | E Mid ↔ E Mid |
| **Total** | **565.5 km** | **242 unique** | **921** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 6,278 one-way journeys / 228,994 train-km/day |
| Annual traction demand | 2,166.5 GWh |
| Station/depot PV / storage | 133.3 MW / 982.0 MWh |
| Aggregate charging power | 450.0 MW |
| Dedicated solar plant | 896.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-8: 17.3 km / 288 kWh |
| Lowest traversal charging margin | line-13: 50 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $5.17 bn |
| Stations | $1.59 bn |
| Depots | $404 M |
| Rolling stock | $1.55 bn |
| Dedicated solar plant | $717 M |
| Residual train control | $28 M |
| Charging microgrids | $91 M |
| EPC / project services | $618 M |
| **Total city programme** | **$10.17 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.20 bn (21.7%) |
| Domestic / local capital | $7.97 bn (78.3%) |
| Annual public construction commitment | $1.38 bn / yr for 7 years |
| Annual post-grace debt service | $1.19 bn / yr |
| External capital saved vs default turnkey sensitivity | $16.10 bn |
| Capital + lifetime external interest saved | $36.28 bn |
| Annual OPEX | $239 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 24 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 2,280 assets / 12,672 tasks | [`karachi-operations-manifest.json`](operations/karachi-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`karachi.toml`](karachi.toml) | Expanded simulator scenario |
| [`karachi.corridor.geojson`](karachi.corridor.geojson) | GIS corridor and stations |
| [`karachi.design-quality.yaml`](karachi.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh karachi
```
