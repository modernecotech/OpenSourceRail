# Kano — Urban Rail Network

**Country:** NG · **Population:** 4,200,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kano-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$13.32 bn (88.0%) of external capital** and **$16.70 bn of external interest**. Capital plus saved interest totals **$30.02 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-12).** The controlled planning inventory contains **14 lines**, including **5 additional residential lines**. **43.0%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **358.026 km to 394.492 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 1 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **168 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**14 line-local depots** provide **777 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **777 metro-6car trainsets / 4662 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Kano rail network on OpenStreetMap](kano-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 14 / 168 / 44 |
| Route length | 473.7 km double track |
| Direct transfers / reachable line pairs | 46.2% / 100.0% |
| Residents within 800 m radial station catchments | 1,882,923 (2020 raster; 30.8% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 777 × 6-car `metro-6car` trainsets (701 peak revenue) |
| Peak network throughput | 403,200 passengers/hour |
| Practical service capacity | 3,615,840 passenger-trips/day |
| Annual paid-trip planning range | 659.9–1055.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 47.5 km | 17 | 85 | W Mid ↔ E Mid |
| line-2 | 49.5 km | 18 | 96 | SE Outer ↔ NW Mid |
| line-3 | 48.5 km | 19 | 90 | SW Mid ↔ NE Mid |
| line-4 | 35.5 km | 13 | 63 | SE Outer ↔ NW Inner |
| line-5 | 36.7 km | 13 | 70 | NE Outer ↔ SW Inner |
| line-6 | 30.3 km | 12 | 58 | N Mid ↔ S Mid |
| line-7 | 50.1 km | 17 | 97 | NE Outer ↔ S Mid |
| line-8 | 44.7 km | 17 | 85 | SE Inner ↔ NW Outer |
| line-9 | 83.2 km | 23 | 37 | NW Mid ↔ NW Mid |
| line-10 | 10.2 km | 4 | 20 | W Inner ↔ W Inner |
| line-11 |  6.8 km | 3 | 15 | SW Inner ↔ SW Inner |
| line-12 |  9.9 km | 4 | 20 | SW Mid ↔ SW Mid |
| line-13 |  9.6 km | 4 | 20 | W Mid ↔ W Inner |
| line-14 | 11.3 km | 4 | 21 | SW Mid ↔ SW Mid |
| **Total** | **473.7 km** | **168 unique** | **777** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 6,278 one-way journeys / 200,957 train-km/day |
| Annual traction demand | 1,901.2 GWh |
| Station/depot PV / storage | 111.7 MW / 838.0 MWh |
| Aggregate charging power | 306.0 MW |
| Dedicated solar plant | 793.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-8: 19.7 km / 330 kWh |
| Lowest traversal charging margin | line-13: 101 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $4.51 bn |
| Stations | $1.01 bn |
| Depots | $364 M |
| Rolling stock | $1.31 bn |
| Dedicated solar plant | $634 M |
| Residual train control | $24 M |
| Charging microgrids | $62 M |
| EPC / project services | $509 M |
| **Total city programme** | **$8.41 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.82 bn (21.7%) |
| Domestic / local capital | $6.59 bn (78.3%) |
| Annual public construction commitment | $982 M / yr for 7 years |
| Annual post-grace debt service | $830 M / yr |
| External capital saved vs default turnkey sensitivity | $13.32 bn |
| Capital + lifetime external interest saved | $30.02 bn |
| Annual OPEX | $199 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 26 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,746 assets / 10,030 tasks | [`kano-operations-manifest.json`](operations/kano-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kano.toml`](kano.toml) | Expanded simulator scenario |
| [`kano.corridor.geojson`](kano.corridor.geojson) | GIS corridor and stations |
| [`kano.design-quality.yaml`](kano.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kano
```
