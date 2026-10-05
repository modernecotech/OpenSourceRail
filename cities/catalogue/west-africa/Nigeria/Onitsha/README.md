# Onitsha — Urban Rail Network

**Country:** NG · **Population:** 1,500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Onitsha-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$15.04 bn (90.8%) of external capital** and **$18.85 bn of external interest**. Capital plus saved interest totals **$33.89 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **125.684 km to 131.504 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **65 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**5 line-local depots** provide **210 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **210 metro-4car trainsets / 840 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Onitsha rail network on OpenStreetMap](onitsha-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 5 / 65 / 8 |
| Route length | 195.4 km double track |
| Direct transfers / reachable line pairs | 80.0% / 100.0% |
| Residents within 800 m radial station catchments | 347,132 (2020 raster; 17.1% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 210 × 4-car `metro-4car` trainsets (188 peak revenue) |
| Peak network throughput | 96,000 passengers/hour |
| Practical service capacity | 803,520 passenger-trips/day |
| Annual paid-trip planning range | 146.6–234.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 25.6 km | 8 | 39 | W Mid ↔ E Mid |
| line-2 | 34.9 km | 14 | 58 | NW Outer ↔ SE Outer |
| line-3 | 29.2 km | 12 | 50 | S Outer ↔ NE Outer |
| line-4 | 15.0 km | 6 | 26 | SE Outer ↔ SW Inner |
| line-5 | 90.7 km | 25 | 37 | NW Outer ↔ NW Outer |
| **Total** | **195.4 km** | **65 unique** | **210** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,092 one-way journeys / 69,778 train-km/day |
| Annual traction demand | 440.1 GWh |
| Station/depot PV / storage | 37.6 MW / 263.0 MWh |
| Aggregate charging power | 70.5 MW |
| Dedicated solar plant | 245.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-5: 31.8 km / 318 kWh |
| Lowest traversal charging margin | line-4: 129 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $7.80 bn |
| Stations | $255 M |
| Depots | $98 M |
| Rolling stock | $235 M |
| Dedicated solar plant | $197 M |
| Residual train control | $9.8 M |
| Charging microgrids | $15 M |
| EPC / project services | $589 M |
| **Total city programme** | **$9.20 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.52 bn (16.5%) |
| Domestic / local capital | $7.68 bn (83.5%) |
| Annual public construction commitment | $1.12 bn / yr for 7 years |
| Annual post-grace debt service | $932 M / yr |
| External capital saved vs default turnkey sensitivity | $15.04 bn |
| Capital + lifetime external interest saved | $33.89 bn |
| Annual OPEX | $182 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 18 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 558 assets / 3,003 tasks | [`onitsha-operations-manifest.json`](operations/onitsha-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`onitsha.toml`](onitsha.toml) | Expanded simulator scenario |
| [`onitsha.corridor.geojson`](onitsha.corridor.geojson) | GIS corridor and stations |
| [`onitsha.design-quality.yaml`](onitsha.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh onitsha
```
