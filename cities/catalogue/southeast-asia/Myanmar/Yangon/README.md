<!-- osr-maglev-primary:start -->
> **Primary v0.5 ferrite-maglev planning:** [Open the current city planning package](engineering/maglev/README.md). Formation, duty, fleet, charging, depot quantities and partial cost allowances are recomputed; physical acceptance remains open.
>
> The material below this notice is the retained v0.4 wheel/rail comparator. Its costs, fleet, geometry and acceptance do not transfer to maglev.
<!-- osr-maglev-primary:end -->

# Yangon — Urban Rail Network

**Country:** MM · **Population:** 5,200,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Yangon-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$16.58 bn (87.5%) of external capital** and **$21.42 bn of external interest**. Capital plus saved interest totals **$38.00 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-12).** The controlled planning inventory contains **14 lines**, including **5 additional residential lines**. **44.8%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **321.816 km to 418.059 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **252 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**14 line-local depots** provide **956 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **956 metro-6car trainsets / 5736 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Yangon rail network on OpenStreetMap](yangon-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 14 / 252 / 63 |
| Route length | 542.2 km double track |
| Direct transfers / reachable line pairs | 48.4% / 100.0% |
| Residents within 800 m radial station catchments | 1,988,986 (2020 raster; 32.5% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 956 × 6-car `metro-6car` trainsets (863 peak revenue) |
| Peak network throughput | 403,200 passengers/hour |
| Practical service capacity | 3,615,840 passenger-trips/day |
| Annual paid-trip planning range | 659.9–1055.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 44.9 km | 19 | 86 | N Mid ↔ S Outer |
| line-2 | 40.4 km | 16 | 75 | S Outer ↔ NW Mid |
| line-3 | 59.4 km | 31 | 127 | SE Outer ↔ NW Mid |
| line-4 | 52.1 km | 17 | 96 | NE Outer ↔ SW Outer |
| line-5 | 48.5 km | 25 | 106 | SE Mid ↔ NW Outer |
| line-6 | 38.6 km | 12 | 70 | SW Mid ↔ NE Outer |
| line-7 | 48.4 km | 24 | 101 | W Outer ↔ E Mid |
| line-8 | 56.2 km | 32 | 127 | NW Mid ↔ S Mid |
| line-9 | 102.6 km | 53 | 57 | NW Mid ↔ NW Mid |
| line-10 |  8.3 km | 4 | 18 | NW Mid ↔ NW Outer |
| line-11 |  7.6 km | 5 | 20 | N Mid ↔ N Mid |
| line-12 | 12.3 km | 6 | 27 | SW Mid ↔ W Mid |
| line-13 | 15.1 km | 5 | 30 | NW Outer ↔ W Outer |
| line-14 |  7.8 km | 3 | 16 | NE Inner ↔ NE Mid |
| **Total** | **542.2 km** | **252 unique** | **956** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 6,278 one-way journeys / 228,252 train-km/day |
| Annual traction demand | 2,159.4 GWh |
| Station/depot PV / storage | 136.6 MW / 1,004.0 MWh |
| Aggregate charging power | 472.0 MW |
| Dedicated solar plant | 1,260.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-4: 16.0 km / 240 kWh |
| Lowest traversal charging margin | line-14: 132 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $4.98 bn |
| Stations | $1.78 bn |
| Depots | $411 M |
| Rolling stock | $1.61 bn |
| Dedicated solar plant | $1.01 bn |
| Residual train control | $27 M |
| Charging microgrids | $97 M |
| EPC / project services | $623 M |
| **Total city programme** | **$10.53 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.37 bn (22.5%) |
| Domestic / local capital | $8.16 bn (77.5%) |
| Annual public construction commitment | $1.12 bn / yr for 10 years |
| Annual post-grace debt service | $1.02 bn / yr |
| External capital saved vs default turnkey sensitivity | $16.58 bn |
| Capital + lifetime external interest saved | $38.00 bn |
| Annual OPEX | $242 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 16 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 2,371 assets / 13,176 tasks | [`yangon-operations-manifest.json`](operations/yangon-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`yangon.toml`](yangon.toml) | Expanded simulator scenario |
| [`yangon.corridor.geojson`](yangon.corridor.geojson) | GIS corridor and stations |
| [`yangon.design-quality.yaml`](yangon.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh yangon
```
