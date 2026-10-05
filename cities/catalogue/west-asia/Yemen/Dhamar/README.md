# Dhamar — Urban Rail Network

**Country:** YE · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Dhamar-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$523 M (89.5%) of external capital** and **$676 M of external interest**. Capital plus saved interest totals **$1.20 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **26.174 km to 17.655 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **10 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **48 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **48 tram-2car trainsets / 96 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Dhamar rail network on OpenStreetMap](dhamar-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 10 / 2 |
| Route length | 20.6 km double track |
| Direct transfers / reachable line pairs | 66.7% / 100.0% |
| Residents within 800 m radial station catchments | 50,107 (2020 raster; 24.6% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 48 × 2-car `tram-2car` trainsets (42 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  7.3 km | 3 | 16 | N Outer ↔ S Inner |
| line-2 |  9.4 km | 4 | 20 | E Mid ↔ SW Outer |
| line-3 |  3.9 km | 3 | 12 | NE Mid ↔ NW Inner |
| **Total** | **20.6 km** | **10 unique** | **48** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 9,595 train-km/day |
| Annual traction demand | 30.3 GWh |
| Station/depot PV / storage | 17.1 MW / 123.5 MWh |
| Aggregate charging power | 5.0 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 4.7 km / 25 kWh |
| Lowest traversal charging margin | line-1: 26 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $180 M |
| Stations | $54 M |
| Depots | $40 M |
| Rolling stock | $27 M |
| Residual train control | $1.0 M |
| Charging microgrids | $1.1 M |
| EPC / project services | $21 M |
| **Total city programme** | **$325 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $61 M (18.9%) |
| Domestic / local capital | $263 M (81.1%) |
| Annual public construction commitment | $46 M / yr for 10 years |
| Annual post-grace debt service | $42 M / yr |
| External capital saved vs default turnkey sensitivity | $523 M |
| Capital + lifetime external interest saved | $1.20 bn |
| Annual OPEX | $7.3 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 1 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 113 assets / 611 tasks | [`dhamar-operations-manifest.json`](operations/dhamar-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`dhamar.toml`](dhamar.toml) | Expanded simulator scenario |
| [`dhamar.corridor.geojson`](dhamar.corridor.geojson) | GIS corridor and stations |
| [`dhamar.design-quality.yaml`](dhamar.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh dhamar
```
