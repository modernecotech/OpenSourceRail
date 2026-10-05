# Lahij — Urban Rail Network

**Country:** YE · **Population:** 250,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Lahij-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$647 M (89.6%) of external capital** and **$835 M of external interest**. Capital plus saved interest totals **$1.48 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **26.298 km to 20.891 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **14 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **54 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **54 tram-2car trainsets / 108 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Lahij rail network on OpenStreetMap](lahij-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 14 / 3 |
| Route length | 23.6 km double track |
| Direct transfers / reachable line pairs | 100.0% / 100.0% |
| Residents within 800 m radial station catchments | 46,609 (2020 raster; 49.6% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 54 × 2-car `tram-2car` trainsets (48 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  8.2 km | 5 | 19 | S Mid ↔ N Outer |
| line-2 |  6.2 km | 4 | 15 | N Mid ↔ S Mid |
| line-3 |  9.2 km | 5 | 20 | SE Outer ↔ N Mid |
| **Total** | **23.6 km** | **14 unique** | **54** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 10,970 train-km/day |
| Annual traction demand | 34.6 GWh |
| Station/depot PV / storage | 18.3 MW / 125.5 MWh |
| Aggregate charging power | 7.0 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 4.2 km / 22 kWh |
| Lowest traversal charging margin | line-2: 45 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $215 M |
| Stations | $86 M |
| Depots | $41 M |
| Rolling stock | $30 M |
| Residual train control | $1.2 M |
| Charging microgrids | $1.6 M |
| EPC / project services | $26 M |
| **Total city programme** | **$401 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $75 M (18.8%) |
| Domestic / local capital | $326 M (81.2%) |
| Annual public construction commitment | $57 M / yr for 10 years |
| Annual post-grace debt service | $52 M / yr |
| External capital saved vs default turnkey sensitivity | $647 M |
| Capital + lifetime external interest saved | $1.48 bn |
| Annual OPEX | $8.9 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 1 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 140 assets / 738 tasks | [`lahij-operations-manifest.json`](operations/lahij-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`lahij.toml`](lahij.toml) | Expanded simulator scenario |
| [`lahij.corridor.geojson`](lahij.corridor.geojson) | GIS corridor and stations |
| [`lahij.design-quality.yaml`](lahij.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh lahij
```
