# Antananarivo — Urban Rail Network

**Country:** MG · **Population:** 3,058,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Antananarivo-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$8.85 bn (87.8%) of external capital** and **$11.44 bn of external interest**. Capital plus saved interest totals **$20.29 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **266.865 km to 246.069 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **115 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**9 line-local depots** provide **476 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **476 metro-6car trainsets / 2856 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Antananarivo rail network on OpenStreetMap](antananarivo-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 115 / 21 |
| Route length | 294.3 km double track |
| Direct transfers / reachable line pairs | 88.9% / 100.0% |
| Residents within 800 m radial station catchments | 863,234 (2020 raster; 24.9% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 476 × 6-car `metro-6car` trainsets (428 peak revenue) |
| Peak network throughput | 259,200 passengers/hour |
| Practical service capacity | 2,276,640 passenger-trips/day |
| Annual paid-trip planning range | 415.5–664.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 28.3 km | 14 | 61 | S Mid ↔ NE Outer |
| line-2 | 24.4 km | 11 | 50 | SE Mid ↔ NW Outer |
| line-3 | 29.6 km | 13 | 58 | W Outer ↔ E Mid |
| line-4 | 22.6 km | 9 | 43 | E Mid ↔ SW Mid |
| line-5 | 26.4 km | 12 | 52 | N Inner ↔ S Outer |
| line-6 | 32.5 km | 12 | 60 | E Outer ↔ W Outer |
| line-7 | 29.6 km | 11 | 58 | W Mid ↔ NE Outer |
| line-8 | 29.2 km | 13 | 59 | SE Mid ↔ NW Outer |
| line-9 | 71.7 km | 20 | 35 | NW Mid ↔ NW Mid |
| **Total** | **294.3 km** | **115 unique** | **476** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,952 one-way journeys / 120,167 train-km/day |
| Annual traction demand | 1,136.9 GWh |
| Station/depot PV / storage | 73.8 MW / 552.0 MWh |
| Aggregate charging power | 210.0 MW |
| Dedicated solar plant | 661.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-9: 15.2 km / 228 kWh |
| Lowest traversal charging margin | line-7: 280 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.97 bn |
| Stations | $686 M |
| Depots | $228 M |
| Rolling stock | $800 M |
| Dedicated solar plant | $529 M |
| Residual train control | $15 M |
| Charging microgrids | $43 M |
| EPC / project services | $332 M |
| **Total city programme** | **$5.60 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.23 bn (22.0%) |
| Domestic / local capital | $4.37 bn (78.0%) |
| Annual public construction commitment | $528 M / yr for 10 years |
| Annual post-grace debt service | $478 M / yr |
| External capital saved vs default turnkey sensitivity | $8.85 bn |
| Capital + lifetime external interest saved | $20.29 bn |
| Annual OPEX | $125 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 19 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,130 assets / 6,357 tasks | [`antananarivo-operations-manifest.json`](operations/antananarivo-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`antananarivo.toml`](antananarivo.toml) | Expanded simulator scenario |
| [`antananarivo.corridor.geojson`](antananarivo.corridor.geojson) | GIS corridor and stations |
| [`antananarivo.design-quality.yaml`](antananarivo.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh antananarivo
```
