<!-- osr-maglev-primary:start -->
> **Primary v0.5 ferrite-maglev planning:** [Open the current city planning package](engineering/maglev/README.md). Formation, duty, fleet, charging, depot quantities and partial cost allowances are recomputed; physical acceptance remains open.
>
> The material below this notice is the retained v0.4 wheel/rail comparator. Its costs, fleet, geometry and acceptance do not transfer to maglev.
<!-- osr-maglev-primary:end -->

# Amman — Urban Rail Network

**Country:** JO · **Population:** 4,007,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Amman-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$11.33 bn (87.8%) of external capital** and **$13.93 bn of external interest**. Capital plus saved interest totals **$25.25 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-12).** The controlled planning inventory contains **14 lines**, including **5 additional residential lines**. **37.7%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **274.882 km to 309.978 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **132 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**14 line-local depots** provide **659 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **659 metro-6car trainsets / 3954 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Amman rail network on OpenStreetMap](amman-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 14 / 132 / 39 |
| Route length | 412.9 km double track |
| Direct transfers / reachable line pairs | 44.0% / 100.0% |
| Residents within 800 m radial station catchments | 919,907 (2020 raster; 25.7% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 659 × 6-car `metro-6car` trainsets (592 peak revenue) |
| Peak network throughput | 403,200 passengers/hour |
| Practical service capacity | 3,615,840 passenger-trips/day |
| Annual paid-trip planning range | 659.9–1055.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 48.2 km | 13 | 85 | SW Outer ↔ NE Outer |
| line-2 | 52.6 km | 14 | 95 | N Outer ↔ S Outer |
| line-3 | 30.3 km | 9 | 56 | S Outer ↔ NW Mid |
| line-4 | 18.2 km | 8 | 37 | N Inner ↔ S Mid |
| line-5 | 33.0 km | 10 | 59 | W Outer ↔ SE Mid |
| line-6 | 35.8 km | 14 | 68 | E Mid ↔ W Outer |
| line-7 | 28.8 km | 12 | 57 | E Mid ↔ NW Outer |
| line-8 | 34.9 km | 12 | 65 | NE Outer ↔ SW Mid |
| line-9 | 82.4 km | 23 | 38 | W Mid ↔ W Mid |
| line-10 | 11.1 km | 4 | 21 | S Inner ↔ E Inner |
| line-11 |  8.4 km | 3 | 17 | NW Mid ↔ NW Outer |
| line-12 | 13.3 km | 4 | 27 | E Mid ↔ NE Outer |
| line-13 |  8.3 km | 3 | 17 | NE Outer ↔ NE Outer |
| line-14 |  7.6 km | 3 | 17 | SE Mid ↔ SE Outer |
| **Total** | **412.9 km** | **132 unique** | **659** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 6,278 one-way journeys / 172,852 train-km/day |
| Annual traction demand | 1,635.3 GWh |
| Station/depot PV / storage | 101.8 MW / 772.0 MWh |
| Aggregate charging power | 240.0 MW |
| Dedicated solar plant | 741.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 14.8 km / 238 kWh |
| Lowest traversal charging margin | line-11: 47 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $3.82 bn |
| Stations | $812 M |
| Depots | $335 M |
| Rolling stock | $1.11 bn |
| Dedicated solar plant | $593 M |
| Residual train control | $21 M |
| Charging microgrids | $49 M |
| EPC / project services | $430 M |
| **Total city programme** | **$7.16 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.57 bn (21.9%) |
| Domestic / local capital | $5.60 bn (78.1%) |
| Annual public construction commitment | $630 M / yr for 5 years |
| Annual post-grace debt service | $455 M / yr |
| External capital saved vs default turnkey sensitivity | $11.33 bn |
| Capital + lifetime external interest saved | $25.25 bn |
| Annual OPEX | $205 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 12 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,433 assets / 8,314 tasks | [`amman-operations-manifest.json`](operations/amman-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`amman.toml`](amman.toml) | Expanded simulator scenario |
| [`amman.corridor.geojson`](amman.corridor.geojson) | GIS corridor and stations |
| [`amman.design-quality.yaml`](amman.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh amman
```
