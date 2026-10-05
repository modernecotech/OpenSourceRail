# Waw — Urban Rail Network

**Recorded country:** SD (jurisdiction mismatch; see below) · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Waw-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$429 M (89.3%) of external capital** and **$554 M of external interest**. Capital plus saved interest totals **$983 M**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **16.705 km to 13.627 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **10 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **40 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **40 tram-2car trainsets / 80 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

**Input discrepancy:** The retained Waw/Wau bbox is in South Sudan, while the canonical planning seed incorrectly records SD/Sudan. Use South Sudan population evidence; canonical jurisdiction and country-specific finance remain unreleased pending full city regeneration. [Evidence](https://unmiss.unmissions.org/en/news/wau-political-parties-and-security-actors-pledge-collaborate-creating-inclusive-civic).

## Network

![Waw rail network on OpenStreetMap](waw-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 10 / 1 |
| Route length | 15.3 km double track |
| Direct transfers / reachable line pairs | 33.3% / 33.3% |
| Residents within 800 m radial station catchments | 745 (2020 raster; 6.9% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 40 × 2-car `tram-2car` trainsets (34 peak revenue) |
| Peak network throughput | 28,800 passengers/hour |
| Practical service capacity | 267,840 passenger-trips/day |
| Annual paid-trip planning range | 48.9–78.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  6.6 km | 3 | 14 | NW Mid ↔ S Outer |
| line-2 |  6.6 km | 4 | 16 | N Outer ↔ S Inner |
| line-3 |  2.0 km | 3 | 10 | SE Inner ↔ NW Inner |
| **Total** | **15.3 km** | **10 unique** | **40** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 7,098 train-km/day |
| Annual traction demand | 22.4 GWh |
| Station/depot PV / storage | 17.1 MW / 123.5 MWh |
| Aggregate charging power | 5.0 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 3.6 km / 20 kWh |
| Lowest traversal charging margin | line-1: 33 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $137 M |
| Stations | $48 M |
| Depots | $40 M |
| Rolling stock | $22 M |
| Residual train control | $763 k |
| Charging microgrids | $1.1 M |
| EPC / project services | $17 M |
| **Total city programme** | **$267 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $51 M (19.3%) |
| Domestic / local capital | $215 M (80.7%) |
| Annual public construction commitment | $32 M / yr for 10 years |
| Annual post-grace debt service | $29 M / yr |
| External capital saved vs default turnkey sensitivity | $429 M |
| Capital + lifetime external interest saved | $983 M |
| Annual OPEX | $6.3 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 2 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 103 assets / 537 tasks | [`waw-operations-manifest.json`](operations/waw-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`waw.toml`](waw.toml) | Expanded simulator scenario |
| [`waw.corridor.geojson`](waw.corridor.geojson) | GIS corridor and stations |
| [`waw.design-quality.yaml`](waw.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh waw
```
