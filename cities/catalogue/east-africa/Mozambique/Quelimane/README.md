# Quelimane — Urban Rail Network

**Country:** MZ · **Population:** 350,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Quelimane-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$180 M (88.6%) of external capital** and **$232 M of external interest**. Capital plus saved interest totals **$412 M**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **10.266 km to 5.694 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **5 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**1 line-local depots** provide **18 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **18 light-metro-3car trainsets / 54 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Quelimane rail network on OpenStreetMap](quelimane-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 1 / 5 / 0 |
| Route length | 5.7 km double track |
| Direct transfers / reachable line pairs | 100.0% / 100.0% |
| Residents within 800 m radial station catchments | 46,326 (2020 raster; 13.7% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 18 × 3-car `light-metro-3car` trainsets (16 peak revenue) |
| Peak network throughput | 14,400 passengers/hour |
| Practical service capacity | 133,920 passenger-trips/day |
| Annual paid-trip planning range | 24.4–39.1 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  5.7 km | 5 | 18 | E Outer ↔ W Outer |
| **Total** | **5.7 km** | **5 unique** | **18** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 465 one-way journeys / 2,648 train-km/day |
| Annual traction demand | 12.5 GWh |
| Station/depot PV / storage | 6.2 MW / 44.0 MWh |
| Aggregate charging power | 5.0 MW |
| Dedicated solar plant | 1.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 1.4 km / 11 kWh |
| Lowest traversal charging margin | line-1: 280 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $56 M |
| Stations | $17 M |
| Depots | $14 M |
| Rolling stock | $16 M |
| Dedicated solar plant | $873 k |
| Residual train control | $285 k |
| Charging microgrids | $1.3 M |
| EPC / project services | $7.3 M |
| **Total city programme** | **$113 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $23 M (20.5%) |
| Domestic / local capital | $90 M (79.5%) |
| Annual public construction commitment | $12 M / yr for 10 years |
| Annual post-grace debt service | $11 M / yr |
| External capital saved vs default turnkey sensitivity | $180 M |
| Capital + lifetime external interest saved | $412 M |
| Annual OPEX | $2.9 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 3 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 50 assets / 253 tasks | [`quelimane-operations-manifest.json`](operations/quelimane-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`quelimane.toml`](quelimane.toml) | Expanded simulator scenario |
| [`quelimane.corridor.geojson`](quelimane.corridor.geojson) | GIS corridor and stations |
| [`quelimane.design-quality.yaml`](quelimane.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh quelimane
```
