<!-- osr-maglev-primary:start -->
> **Primary v0.5 ferrite-maglev planning:** [Open the current city planning package](engineering/maglev/README.md). Formation, duty, fleet, charging, depot quantities and partial cost allowances are recomputed; physical acceptance remains open.
>
> The material below this notice is the retained v0.4 wheel/rail comparator. Its costs, fleet, geometry and acceptance do not transfer to maglev.
<!-- osr-maglev-primary:end -->

# Jeddah — Urban Rail Network

**Country:** SA · **Population:** 4,700,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Jeddah-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$11.52 bn (87.7%) of external capital** and **$14.16 bn of external interest**. Capital plus saved interest totals **$25.68 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-12).** The controlled planning inventory contains **14 lines**, including **5 additional residential lines**. **34.0%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **310.121 km to 333.254 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **159 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**14 line-local depots** provide **702 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **702 metro-6car trainsets / 4212 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Jeddah rail network on OpenStreetMap](jeddah-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 14 / 159 / 38 |
| Route length | 408.4 km double track |
| Direct transfers / reachable line pairs | 37.4% / 100.0% |
| Residents within 800 m radial station catchments | 896,030 (2020 raster; 23.4% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 702 × 6-car `metro-6car` trainsets (631 peak revenue) |
| Peak network throughput | 403,200 passengers/hour |
| Practical service capacity | 3,615,840 passenger-trips/day |
| Annual paid-trip planning range | 659.9–1055.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 47.3 km | 17 | 84 | S Outer ↔ NW Outer |
| line-2 | 26.9 km | 9 | 52 | S Mid ↔ NW Mid |
| line-3 | 49.2 km | 22 | 98 | N Mid ↔ SE Outer |
| line-4 | 44.5 km | 14 | 84 | N Inner ↔ S Outer |
| line-5 | 33.2 km | 13 | 67 | E Outer ↔ W Inner |
| line-6 | 33.9 km | 11 | 65 | SE Outer ↔ W Inner |
| line-7 | 29.7 km | 11 | 58 | NE Mid ↔ S Inner |
| line-8 | 29.2 km | 13 | 58 | NE Mid ↔ SW Inner |
| line-9 | 74.2 km | 27 | 34 | NW Mid ↔ NW Mid |
| line-10 |  7.4 km | 10 | 32 | N Mid ↔ NW Inner |
| line-11 |  6.2 km | 2 | 13 | SE Mid ↔ SE Mid |
| line-12 | 14.2 km | 5 | 29 | NW Outer ↔ NW Mid |
| line-13 |  6.3 km | 3 | 15 | S Mid ↔ SW Inner |
| line-14 |  6.4 km | 2 | 13 | NW Mid ↔ W Mid |
| **Total** | **408.4 km** | **159 unique** | **702** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 6,278 one-way journeys / 172,664 train-km/day |
| Annual traction demand | 1,633.5 GWh |
| Station/depot PV / storage | 109.3 MW / 822.0 MWh |
| Aggregate charging power | 290.0 MW |
| Dedicated solar plant | 732.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-4: 15.8 km / 256 kWh |
| Lowest traversal charging margin | line-14: 83 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $3.69 bn |
| Stations | $980 M |
| Depots | $344 M |
| Rolling stock | $1.18 bn |
| Dedicated solar plant | $586 M |
| Residual train control | $20 M |
| Charging microgrids | $59 M |
| EPC / project services | $439 M |
| **Total city programme** | **$7.29 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.61 bn (22.1%) |
| Domestic / local capital | $5.68 bn (77.9%) |
| Annual public construction commitment | $504 M / yr for 5 years |
| Annual post-grace debt service | $353 M / yr |
| External capital saved vs default turnkey sensitivity | $11.52 bn |
| Capital + lifetime external interest saved | $25.68 bn |
| Annual OPEX | $323 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 20 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,616 assets / 9,186 tasks | [`jeddah-operations-manifest.json`](operations/jeddah-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`jeddah.toml`](jeddah.toml) | Expanded simulator scenario |
| [`jeddah.corridor.geojson`](jeddah.corridor.geojson) | GIS corridor and stations |
| [`jeddah.design-quality.yaml`](jeddah.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh jeddah
```
