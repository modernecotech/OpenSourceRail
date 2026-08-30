# Beira — Urban Rail Network

**Country:** MZ · **Population:** 535,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Beira-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$580 M (86.3%) of external capital** and **$750 M of external interest**. Capital plus saved interest totals **$1.33 bn**. See the common reference for interpretation and limitations.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Beira rail network on OpenStreetMap](beira-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 18 / 1 |
| Route length | 44.8 km double track |
| Coverage / transfer reachability | 34.0% / 33% |
| Estimated station catchment | 181,900 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 96 × 3-car `light-metro-3car` trainsets (86 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 17.5 km | 7 | 37 | S Mid ↔ N Outer |
| line-2 | 12.2 km | 6 | 27 | SW Mid ↔ E Mid |
| line-3 | 15.1 km | 5 | 32 | NW Outer ↔ E Mid |
| **Total** | **44.8 km** | **18 unique** | **96** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 20,843 train-km/day |
| Annual traction demand | 98.6 GWh |
| Station/depot PV / storage | 10.1 MW / 48.5 MWh |
| Aggregate charging power | 9.0 MW |
| Dedicated solar plant | 53.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 5.4 km / 40 kWh |
| Lowest traversal charging margin | line-2: 47 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $130 M |
| Stations | $80 M |
| Depots | $8.0 M |
| Rolling stock | $86 M |
| Dedicated solar plant | $42 M |
| Residual train control | $2.2 M |
| Charging microgrids | $2.0 M |
| EPC / project services | $22 M |
| **Total city programme** | **$374 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $92 M (24.7%) |
| Domestic / local capital | $281 M (75.3%) |
| Annual public construction commitment | $40 M / yr for 10 years |
| Annual post-grace debt service | $37 M / yr |
| External capital saved vs default turnkey sensitivity | $580 M |
| Capital + lifetime external interest saved | $1.33 bn |
| Annual OPEX | $9.2 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Grid/charging/solar | pass | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 205 assets / 950 tasks | [`beira-operations-manifest.json`](operations/beira-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`beira.toml`](beira.toml) | Expanded simulator scenario |
| [`beira.corridor.geojson`](beira.corridor.geojson) | GIS corridor and stations |
| [`beira.design-quality.yaml`](beira.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh beira
```
